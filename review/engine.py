"""Deterministic verdicts from a review's observations: no model calls, no I/O beyond reading the ruleset.

The rule evaluator is the Kleene three-valued core of the method-legibility policy pack (~/Downloads/method-policy/
engine.py, after the content-moderation cookbook): False dominates all(), True dominates any(), and a comparison
against a missing value is unknown, so an unknown never becomes a pass. On top of it, this engine
  - applies the evidence gates of policy.md (G1 sampling, G2 stills, G3 timestamps, G4 scope) from facts the reviewer
    never states: the clip's sampling rate and duration, and the stills the harness actually served, and from the
    reviewer's own measurements where they contradict its claims;
  - decides each axis (S, R) separately: withheld > flag > needs_review > approve;
  - builds a card listing what fired, what was unknown, what the gates changed, and what is reported but not judged.
"""
import json
import re
from dataclasses import dataclass, field as dc_field
from pathlib import Path

RULESET = Path(__file__).resolve().parent / 'ruleset.json'
OBS = ['s1_silhouette', 's2_flight_mode', 's3_flock_motion', 's4_attitude_variety', 's5_predator',
       'r1_scale', 'r2_tone', 'r3_numbers', 'r4_artefacts', 'r5_camera', 'r6_scene']
RESOLVED_PX = 8                          # policy S0: birds are resolved from about 8 px wingtip to wingtip
RENDER_KINDS = {'ghosting', 'popping', 'flicker', 'hard_edges', 'aliasing', 'duplicates', 'wrong_occlusion'}
LABELS = {'S': {'approve': 'reads as starlings', 'flag': 'does not read as starlings', 'needs_review': 'needs review', 'withheld': 'withheld'},
          'R': {'approve': 'passes as real', 'flag': 'tells found', 'needs_review': 'needs review', 'withheld': 'withheld'}}
_MISSING = object()


# ---- three-valued rule evaluation (from method-policy/engine.py)

def _bool_mismatch(a, b):
    return isinstance(a, bool) != isinstance(b, bool)


def _leaf(cond, values, trace):
    name, op, expected = cond['field'], cond['op'], cond.get('value')
    actual = values.get(name, _MISSING)
    absent = actual is _MISSING or actual is None
    if op == 'exists':
        result = not absent
    elif absent:
        result = None
    elif op in ('eq', 'neq'):
        result = None if _bool_mismatch(actual, expected) else (actual == expected) == (op == 'eq')
    elif op in ('gt', 'gte', 'lt', 'lte'):
        if isinstance(actual, bool) or isinstance(expected, bool):
            result = None
        else:
            result = {'gt': actual > expected, 'gte': actual >= expected, 'lt': actual < expected, 'lte': actual <= expected}[op]
    elif op in ('in', 'not_in'):
        result = (actual in expected) == (op == 'in')
    elif op in ('contains', 'not_contains'):
        result = (expected in actual) == (op == 'contains')
    else:
        raise ValueError(f'unknown op {op!r}')
    trace.append({'field': name, 'op': op, 'expected': expected, 'actual': None if absent else actual, 'result': result})
    return result


def _eval(cond, values, trace):
    if 'all' in cond:
        unknown = False
        for sub in cond['all']:
            r = _eval(sub, values, trace)
            if r is False:
                return False
            unknown |= r is None
        return None if unknown else True
    if 'any' in cond:
        unknown = False
        for sub in cond['any']:
            r = _eval(sub, values, trace)
            if r is True:
                return True
            unknown |= r is None
        return None if unknown else False
    if 'not' in cond:
        r = _eval(cond['not'], values, trace)
        return None if r is None else not r
    return _leaf(cond, values, trace)


@dataclass
class RuleResult:
    rule_id: str
    axis: str
    policy_ref: str
    outcome: str                  # fired | clear | unknown | out_of_scope
    trace: list = dc_field(default_factory=list)


def evaluate_rule(rule, fields):
    rr = RuleResult(rule['id'], rule['axis'], rule['policy_ref'], 'clear')
    scope = _eval(rule['scope'], fields, rr.trace) if 'scope' in rule else True
    if scope is False:
        rr.outcome = 'out_of_scope'
        return rr
    w = _eval(rule['when'], fields, rr.trace)
    if scope is None:                                                # v0.4: an undecided scope leaves the rule undecided,
        rr.outcome = 'unknown'                                       # whichever way the observation points
    else:
        rr.outcome = 'fired' if w is True else 'clear' if w is False else 'unknown'
    return rr


# ---- gates and flattening

_TS = re.compile(r'^\s*(\d{1,2}):(\d{2}(?:\.\d+)?)\s*$')


def seconds(ts):
    m = _TS.match(ts or '')
    return int(m[1]) * 60 + float(m[2]) if m else None


def apply_gates(ext: dict, clip: dict, stills_served: set[str]):
    """Returns (gated copy of the extraction, gate notes, axes withheld). `clip` is the clip's key entry."""
    ext = json.loads(json.dumps(ext))
    notes, withheld = [], set()
    dur = clip['video_seconds']
    in_clip = lambda ts: seconds(ts) is not None and 0 <= seconds(ts) <= dur + .05
    res, span = ext.get('birds_resolved'), ext.get('bird_span_px_median')   # G4 (v0.4): scope must agree with its own measure
    if span is not None and res is not None and res != (span >= RESOLVED_PX):
        notes.append(f'G4 birds_resolved {res} contradicts the reviewer\'s own median span of {span:g} px (resolved means '
                     f'about {RESOLVED_PX} px or more, policy S0); scope set to unknown')
        ext['birds_resolved'] = None
    for name in OBS:                                                  # G3: timestamps
        o = ext.get(name)
        if not o or o.get('holds') is None:
            continue
        ok = [t for t in (o.get('timestamps') or []) if in_clip(t)]
        if not ok:
            notes.append(f'G3 {name}: no valid timestamp within 00:00-{int(dur // 60):02d}:{dur % 60:04.1f}; set to unknown')
            o['holds'] = None
        else:
            o['timestamps'] = ok
    kept = []                                                         # G3 for artefacts (v0.4): R4 counts only these
    for a in ext.get('artefacts') or []:
        ok = [t for t in a.get('timestamps') or [] if in_clip(t)]
        if ok:
            kept.append({**a, 'timestamps': ok})
        else:
            notes.append(f'G3 artefact {a.get("kind")}: no timestamp within the clip; not counted')
    if ext.get('artefacts'):
        ext['artefacts'] = kept
    wts = ext.get('wingbeat_timestamps') or []                        # G3 for the moments a rate rests on (v0.4)
    wok = [t for t in wts if in_clip(t)]
    if len(wok) < len(wts):
        notes.append(f'G3 wingbeat_timestamps: {len(wts) - len(wok)} of {len(wts)} outside the clip; dropped')
    ext['wingbeat_timestamps'] = wok
    hz = ext.get('wingbeat_hz')                                       # G1: sampling
    why = None
    if hz is not None and hz >= clip['nyquist_hz']:
        why = f'G1 wingbeat_hz {hz:g} is at or above half the clip\'s sampling rate ({clip["sample_hz"]:g}/s); withheld'
    elif hz is not None and hz <= 0:                                  # G1b for 'no flapping': must outlast a glide pause
        real = sorted({seconds(t) * clip['slow'] for t in ext.get('wingbeat_timestamps') or [] if seconds(t) is not None})
        if len(real) < 4 or real[-1] - real[0] <= 1.0:                # "more than 1 s" (v0.4: exactly 1 s passed)
            why = (f'G1 wingbeat_hz 0 (no flapping) rests on {len(real)} cited moment(s) spanning '
                   f'{(real[-1] - real[0]) if real else 0:.2f} s; glide pauses last up to 1 s, so "no flapping" needs at '
                   f'least 4 moments over more than 1 s; withheld')
    elif hz is not None:                                              # G1b: the moments cited must sample the rate
        real = sorted({seconds(t) * clip['slow'] for t in ext.get('wingbeat_timestamps') or [] if seconds(t) is not None})
        gap = max((b - a for a, b in zip(real, real[1:])), default=None)
        if len(real) < 4 or gap >= 1 / (2 * hz) or real[-1] - real[0] < 2 / hz:
            why = (f'G1 wingbeat_hz {hz:g} rests on {len(real)} cited moment(s)'
                   + (f', up to {gap:.3f} s apart in real time,' if gap else '')
                   + f' spanning {(real[-1] - real[0]) if real else 0:.3f} s; a rate needs at least 4 moments less than'
                   + f' {1 / (2 * hz):.3f} s apart over at least {2 / hz:.3f} s (two cycles); withheld')
    if why:
        notes.append(why)
        ext['wingbeat_hz'] = None
        if (ext.get('s2_flight_mode') or {}).get('holds') is False:
            ext['s2_flight_mode']['holds'] = None
            notes.append('G1 s2_flight_mode: a fault judged in a clip whose wingbeat claim was withheld; set to unknown')
    s2 = ext.get('s2_flight_mode') or {}                              # G1c (v0.4): an S2 fault stands on its own moments
    if s2.get('holds') is False:
        real = sorted({seconds(t) * clip['slow'] for t in s2.get('timestamps') or []})
        if len(real) < 4 or real[-1] - real[0] <= 1.0:
            s2['holds'] = None
            notes.append(f'G1c s2_flight_mode: a flight-mode fault rests on {len(real)} moment(s) spanning '
                         f'{(real[-1] - real[0]) if real else 0:.2f} s; glide pauses last up to 1 s, so rigid, synchronised '
                         f'or slow wings need at least 4 moments over more than 1 s; set to unknown')
    for name in ('s1_silhouette', 's4_attitude_variety'):            # G2: stills
        o = ext.get(name)
        if not o or o.get('holds') is None:
            continue
        cited = set(o.get('still_ids') or [])
        if not cited or not cited <= stills_served:
            notes.append(f'G2 {name}: cites {sorted(cited) or "no stills"}; served were {sorted(stills_served) or "none"}')
            withheld.add('S')
    return ext, notes, withheld


def flatten(ext: dict) -> dict:
    f = {k: ext.get(k) for k in ('birds_resolved', 'bird_span_px_median', 'birds_visible_estimate', 'predator_visible',
                                 'wingbeat_hz', 'waves_seen', 'wave_pulses')}
    for name in OBS:
        f[name] = (ext.get(name) or {}).get('holds')
    f['render_artefacts'] = sum(1 for a in ext.get('artefacts') or [] if a.get('kind') in RENDER_KINDS)
    return f


# ---- scoring

def score(ext: dict, clip: dict, stills_served: set[str], ruleset: dict | None = None) -> dict:
    ruleset = ruleset or json.loads(RULESET.read_text())
    gated, gate_notes, withheld = apply_gates(ext, clip, stills_served)
    fields = flatten(gated)
    results = [evaluate_rule(r, fields) for r in ruleset['rules']]
    axes = {}
    for axis in ('S', 'R'):
        rs = [r for r in results if r.axis == axis]
        d = ('withheld' if axis in withheld else 'flag' if any(r.outcome == 'fired' for r in rs)
             else 'needs_review' if any(r.outcome == 'unknown' for r in rs) else 'approve')
        rules = {r['id']: r for r in ruleset['rules']}
        unjudged = [r.rule_id for r in rs if r.outcome == 'out_of_scope' and rules[r.rule_id].get('approve_needs_scope')]
        reason = None
        if d == 'approve' and unjudged:                               # v0.4: S cannot approve on flock motion alone
            d, reason = 'needs_review', f'{", ".join(unjudged)} out of scope (birds not resolved); the rest is clear'
        axes[axis] = {'decision': d, 'label': LABELS[axis][d], 'reason': reason,
                      'fired': [r.rule_id for r in rs if r.outcome == 'fired'],
                      'unknown': [r.rule_id for r in rs if r.outcome == 'unknown'],
                      'out_of_scope': [r.rule_id for r in rs if r.outcome == 'out_of_scope']}
    return {'ruleset_version': ruleset['ruleset_version'], 'axes': axes, 'gates': gate_notes, 'fields': fields,
            'trace': {r.rule_id: r.trace for r in results}, 'gated': gated}


def card(result: dict, clip_id: str) -> str:
    g, lines = result['gated'], [f'clip {clip_id}  (ruleset {result["ruleset_version"]})']
    for axis, name in (('S', 'reads as starlings?'), ('R', 'passes as real footage?')):
        a = result['axes'][axis]
        lines.append(f'  {axis} {name:26s} {a["decision"]:12s} {a["label"]}' + (f'  ({a["reason"]})' if a.get('reason') else ''))
        for rid in a['fired'] + a['unknown']:
            o = g.get(next(n for n in OBS if n.split('_')[0] == rid.split('-')[0].lower()), {}) or {}
            tag = 'FIRED  ' if rid in a['fired'] else 'unknown'
            lines.append(f'      {tag} {rid}: {o.get("evidence", "")[:200]}  {o.get("timestamps") or ""}')
    for n in result['gates']:
        lines.append(f'  gate  {n}')
    f = result['fields']
    lines.append(f'  card  birds resolved {f["birds_resolved"]}, span {f["bird_span_px_median"]} px, ~{f["birds_visible_estimate"]} birds, '
                 f'wingbeat {f["wingbeat_hz"]} Hz, predator {f["predator_visible"]}, waves {f["waves_seen"]} ({f["wave_pulses"]} pulses)')
    for a in g.get('artefacts') or []:
        lines.append(f'  artefact {a["kind"]} {a["timestamps"]}: {a["description"][:160]}')
    return '\n'.join(lines)
