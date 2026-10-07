"""Review the control clips and score the policy against its pre-registered expectations (controls.json).

    uv run python run_eval.py [--model gemini-3.8-flash] [--repeat 3] [--only page_calm,real_calm]
    uv run python run_eval.py --report          # re-score the runs already in runs/, no model calls

A control passes when none of its must_not_fire rules fired and all of its must_fire rules did, in the majority of
its repeats. Agreement is the share of repeats that reached the most common decision on each axis: a verdict that
flips between repeats is not a verdict.
"""
import argparse
import collections
import json
import subprocess
import sys

import engine
import gemini
from harness import BRIEF_SHA

HERE = gemini.HERE
CONTROLS = json.loads((HERE / 'controls.json').read_text())
KEY = json.loads((HERE / 'clips' / 'key.json').read_text())


def by_name():
    key = json.loads((HERE / 'clips' / 'key.json').read_text())
    return {v['name']: cid for cid, v in key.items()}


V01 = 'v0.1'                    # runs made before briefs were stamped (brief v0.1, which said some clips are renders)


def runs_for(cid, model=None, brief=BRIEF_SHA, mode='agentic'):
    out = []
    for d in sorted(gemini.RUNS.glob(f'*-{cid}-*')):
        r = d / 'run.json'
        if r.exists():
            j = json.loads(r.read_text())
            ext = d / 'extraction.json'
            if ext.exists():                                    # re-score with the current engine and ruleset
                res = engine.score(json.loads(ext.read_text()), KEY[cid], set(j['stills']))
                j['axes'], j['gates'], j['ruleset'] = res['axes'], res['gates'], res['ruleset_version']
            if ((model is None or j['model'] == model) and (brief is None or j.get('brief_sha', V01) == brief)
                    and (mode is None or j.get('mode', 'static') == mode)):
                out.append(j)
    return out


def report(model=None, brief=BRIEF_SHA, mode='agentic'):
    names = by_name()
    print(f'brief {brief}, model {model or "any"}, mode {mode or "any"}; every run rescored with the current engine and '
          f'ruleset (decisions at run time are in each run.json)')
    print(f'{"control":14s} {"runs":>4s}  {"S decision (agree)":28s} {"R decision (agree)":28s} expectation')
    for name, exp in CONTROLS['clips'].items():
        cid = names.get(name)
        rs = runs_for(cid, model, brief, mode) if cid else []
        if not rs:
            print(f'{name:14s} {"-":>4s}  not run'); continue
        line = f'{name:14s} {len(rs):4d}  '
        for axis in ('S', 'R'):
            c = collections.Counter(r['axes'][axis]['decision'] for r in rs)
            top, n = c.most_common(1)[0]
            line += f'{top:12s} ({n}/{len(rs)}) {",".join(sorted(set(sum((r["axes"][axis]["fired"] for r in rs), []))))[:12]:13s}'
        fired = [set(r['axes']['S']['fired'] + r['axes']['R']['fired']) for r in rs]
        bad = [rule for rule in exp.get('must_not_fire', []) if sum(rule in f for f in fired) > len(rs) / 2]
        miss = [rule for rule in exp.get('must_fire', []) if sum(rule in f for f in fired) <= len(rs) / 2]
        known = set(exp.get('must_fire', []) + exp.get('may_fire', []) + exp.get('must_not_fire', []))
        extra = sorted(rule for rule in set().union(*fired) if rule not in known and sum(rule in f for f in fired) > len(rs) / 2)
        pv = collections.Counter(r.get('prompt_version', 'b1') for r in rs)
        ok = not bad and not miss
        line += (('PASS' if ok else 'FAIL') + (f' fired {bad}' if bad else '') + (f' missed {miss}' if miss else '')
                 + (f'; unexpected {extra}' if extra else '') + (f'; MIXED prompts {dict(pv)}' if len(pv) > 1 else ''))
        print(line)
    report_added(model, brief, mode)
    print(f'ledger total ${gemini.spent():.2f} of ${gemini.CAP_TOTAL:.0f}')


def report_added(model=None, brief=BRIEF_SHA, mode='agentic'):
    """The stricter criteria of controls_added.json (registered 2026-10-07, after the first runs; see its 'registered')."""
    add = json.loads((HERE / 'controls_added.json').read_text())
    ruleset = json.loads(engine.RULESET.read_text())
    scoped = {r['id'] for r in ruleset['rules'] if r.get('approve_needs_scope')}
    names = by_name()
    runs = {n: runs_for(names[n], model, brief, mode) if n in names else [] for n in CONTROLS['clips']}
    rate = lambda rs, rule: sum(rule in r['axes']['S']['fired'] + r['axes']['R']['fired'] for r in rs) / len(rs)
    print(f'\nadded criteria (controls_added.json, registered {add["registered"][:10]}), rescored with ruleset {ruleset["ruleset_version"]}')
    for name in add['real']['clips']:
        rs = runs[name]
        if not rs:
            print(f'  {name:14s} not run'); continue
        r_ok = sum(r['axes']['R']['decision'] == 'approve' for r in rs)
        s_ok = sum(r['axes']['S']['decision'] == 'approve' or (r['axes']['S']['decision'] == 'needs_review' and not r['axes']['S']['fired']
                   and set(r['axes']['S']['unknown']) <= scoped) for r in rs)
        ok = r_ok > len(rs) / 2 and s_ok > len(rs) / 2
        print(f'  {name:14s} R approve {r_ok}/{len(rs)}, S approve or scope-only review {s_ok}/{len(rs)}  {"PASS" if ok else "FAIL"}')
    base = runs[add['variants']['base']]
    for name, target in add['variants']['targets'].items():
        rs = runs[name]
        if not rs or not base:
            print(f'  {name:14s} not run'); continue
        lift = rate(rs, target) - rate(base, target)
        rules = {x for r in rs for x in r['axes']['S']['fired'] + r['axes']['R']['fired']}
        coll = sorted(x for x in rules if x != target and rate(rs, x) > .5 and rate(base, x) <= .5)
        print(f'  {name:14s} {target} fires {rate(rs, target):.0%} vs {rate(base, target):.0%} on {add["variants"]["base"]}: lift {lift:+.0%}  '
              f'{"PASS" if lift >= add["variants"]["min_lift"] else "FAIL"}' + (f'; collateral {coll}' if coll else ''))
    for name, exp in CONTROLS['clips'].items():
        rs = runs[name]
        for field, want in (exp.get('card') or {}).items():
            if not rs:
                continue
            got = []
            for r in rs:
                ext = json.loads((gemini.RUNS / r['run'] / 'extraction.json').read_text())
                got.append(ext.get(field))
            n = sum(g == want for g in got)
            print(f'  {name:14s} card {field} = {want}: {n}/{len(rs)} {"PASS" if n > len(rs) / 2 else "FAIL"}  (reported {got})')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='gemini-3.8-flash')
    ap.add_argument('--mode', default='agentic', choices=['agentic', 'static'])
    ap.add_argument('--repeat', type=int, default=1)
    ap.add_argument('--only')
    ap.add_argument('--report', action='store_true')
    ap.add_argument('--brief', default=BRIEF_SHA, help=f'brief sha to report on (default: the current brief; {V01} for the first)')
    a = ap.parse_args()
    if not a.report:
        names = by_name()
        todo = a.only.split(',') if a.only else list(CONTROLS['clips'])
        for name in todo:
            if name not in names:
                print(f'{name}: no clip built yet, skipped'); continue
            have = len(runs_for(names[name], a.model, BRIEF_SHA, a.mode))
            for _ in range(max(0, a.repeat - have)):
                print(f'== {name} ({names[name]}) on {a.model}')
                r = subprocess.run([sys.executable, str(HERE / 'harness.py'), names[name], '--model', a.model, '--mode', a.mode], cwd=HERE)
                if r.returncode:
                    print(f'{name}: harness failed (exit {r.returncode}); stopping'); report(a.model); return
    report(a.model, a.brief, a.mode)


if __name__ == '__main__':
    main()
