# Generic headless runner: Blender --background --factory-startup --python run_headless.py -- JOB.json
# JOB.json = {"dir": "<scripts dir>", "scripts": ["a.py", ...], "globals": {...}, "after": "<python code>"}
import sys, json
job = json.load(open(sys.argv[sys.argv.index('--') + 1]))
g = dict(job.get('globals', {}))
g.setdefault('__name__', 'bird')
for k in ('VIEWS',):
    if k in g and isinstance(g[k], list): g[k] = tuple(g[k])
if isinstance(g.get('RES'), list): g['RES'] = tuple(g['RES'])
if isinstance(g.get('ONLY'), list): g['ONLY'] = tuple(g['ONLY'])
for f in job['scripts']:
    exec(compile(open(job['dir'] + f).read(), job['dir'] + f, 'exec'), g)
if job.get('after'):
    exec(job['after'], g)
