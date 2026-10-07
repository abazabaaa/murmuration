"""Offline regression probes for the evidence gates (no API calls). Each case edits one saved extraction the way the
two Codex reviews did (scratchpad codex_review/{astra,sol}/gate_probes) and checks the engine no longer lets it through.

    uv run python test_engine.py
"""
import copy
import json
from pathlib import Path

import engine

HERE = Path(__file__).resolve().parent
FIXTURE = json.loads((HERE / 'tests' / 'page_calm_060034.json').read_text())   # a saved page_calm run with a 'rigid' claim
EXT, STILLS, CLIP = FIXTURE['extraction'], set(FIXTURE['stills_served']), FIXTURE['clip']
OBS_UNKNOWN = {'holds': None, 'timestamps': None, 'still_ids': None, 'evidence': 'cannot tell', 'confidence': 'low'}


def rigid(ts):
    return {'holds': False, 'timestamps': ts, 'still_ids': None, 'evidence': 'wings rigid, no flapping', 'confidence': 'high'}


def score(**change):
    e = copy.deepcopy(EXT)
    e.update(birds_resolved=True, bird_span_px_median=9.0)            # resolved and consistent (G4), unless a case says otherwise
    e.update(change)
    return engine.score(e, CLIP, STILLS)


CASES = [
    # name, change, rule that must NOT fire (or must fire), expected
    ('rigid claim with rate null, 2 moments over 0.6 s', dict(wingbeat_hz=None, s2_flight_mode=rigid(['00:01.0', '00:01.6'])),
     'S2-flight-mode', False),
    ('rigid claim with rate null, 4 moments over 2 s', dict(wingbeat_hz=None, s2_flight_mode=rigid(['00:00.5', '00:01.0', '00:01.5', '00:02.5'])),
     'S2-flight-mode', True),
    ('rigid claim, 4 moments spanning exactly 1 s', dict(wingbeat_hz=None, s2_flight_mode=rigid(['00:00.0', '00:00.33', '00:00.66', '00:01.0'])),
     'S2-flight-mode', False),
    ('zero rate, moments outside the clip', dict(wingbeat_hz=0, wingbeat_timestamps=['00:10.0', '00:10.5', '00:11.0', '00:11.5'],
                                                 s2_flight_mode=rigid(['00:00.5', '00:01.0', '00:01.5', '00:02.5'])),
     None, None),
    ('12 Hz rate from moments outside the clip', dict(wingbeat_hz=12, wingbeat_timestamps=[f'00:{10 + k / 30:05.2f}' for k in range(8)]),
     None, None),
    ('artefact at 99:99, R4 unknown', dict(artefacts=[{'kind': 'ghosting', 'timestamps': ['99:99'], 'description': 'sentinel'}],
                                          r4_artefacts=OBS_UNKNOWN), 'R4-artefacts', False),
    ('artefact at 00:02.0, R4 unknown', dict(artefacts=[{'kind': 'ghosting', 'timestamps': ['00:02.0'], 'description': 'trail'}],
                                            r4_artefacts=OBS_UNKNOWN), 'R4-artefacts', True),
]

S_CASES = [                                                            # (v0.4) scope: name, change, rule, fired?, S decision
    ('resolved, own span 2.5 px, S1 fault', dict(birds_resolved=True, bird_span_px_median=2.5,
                                                 s1_silhouette={**EXT['s1_silhouette'], 'holds': False}),
     'S1-silhouette', False, 'needs_review'),
    ('resolved, own span 9 px, S1 fault', dict(birds_resolved=True, bird_span_px_median=9.0,
                                               s1_silhouette={**EXT['s1_silhouette'], 'holds': False}),
     'S1-silhouette', True, 'flag'),
    ('unresolved, everything else clear', dict(birds_resolved=False, bird_span_px_median=3.0,
                                               s3_flock_motion={**EXT['s3_flock_motion'], 'holds': True}),
     'S3-flock-motion', False, 'needs_review'),
    ('scope unknown, S1 holds', dict(birds_resolved=None, s1_silhouette={**EXT['s1_silhouette'], 'holds': True}),
     'S1-silhouette', False, 'needs_review'),
]


def main():
    bad = 0
    for name, change, rule, want in CASES:
        r = score(**change)
        fired = set(r['axes']['S']['fired'] + r['axes']['R']['fired'])
        if rule is None:                                               # the rate itself must be withheld
            ok = r['fields']['wingbeat_hz'] is None
            got = f'wingbeat_hz -> {r["fields"]["wingbeat_hz"]}'
        else:
            ok = (rule in fired) == want
            got = f'{rule} {"fired" if rule in fired else "did not fire"}'
        bad += not ok
        print(f'{"ok  " if ok else "FAIL"} {name:48s} {got}')
        for g in r['gates']:
            if 'G1c' in g or 'G3 a' in g or 'G3 w' in g or 'no flapping' in g or 'rests on' in g:
                print(f'       {g[:150]}')
    for name, change, rule, want, decision in S_CASES:
        base = dict(s2_flight_mode={**EXT['s2_flight_mode'], 'holds': True}, s4_attitude_variety={**EXT['s4_attitude_variety'], 'holds': True},
                    s3_flock_motion={**EXT['s3_flock_motion'], 'holds': True})
        r = score(**{**base, **change})
        S = r['axes']['S']
        ok = (rule in S['fired']) == want and S['decision'] == decision
        bad += not ok
        print(f'{"ok  " if ok else "FAIL"} {name:48s} {rule} {"fired" if rule in S["fired"] else "did not fire"}; '
              f'S {S["decision"]}{" (" + S["reason"] + ")" if S.get("reason") else ""}')
        for g in r['gates']:
            if g.startswith('G4'):
                print(f'       {g[:150]}')
    n = len(CASES) + len(S_CASES)
    print(f'{n - bad}/{n} passed')
    raise SystemExit(bool(bad))


if __name__ == '__main__':
    main()
