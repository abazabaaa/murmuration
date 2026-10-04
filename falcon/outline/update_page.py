# Rewrite the `const FALCON = {...};` table in murmuration.html from peregrine-outline.json.
#   uv run --no-project python falcon/outline/update_page.py [--html murmuration.html] [--json ...]
# Only the table is replaced; pushFalcon and the draw call are hand-written in the page.
import argparse, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ap = argparse.ArgumentParser()
ap.add_argument('--html', default=os.path.join(ROOT, 'murmuration.html'))
ap.add_argument('--json', default=os.path.join(HERE, 'peregrine-outline.json'))
a = ap.parse_args()
d = json.load(open(a.json))


def nums(v):                                       # 0.087 -> .087, -0.07 -> -.07, 0.0 -> 0
    out = []
    for x in v:
        s = ('%.3f' % x).rstrip('0').rstrip('.')
        s = '0' if s in ('', '-0', '0') else s.replace('0.', '.', 1) if s.startswith(('0.', '-0.')) else s
        out.append(s)
    return '[' + ','.join(out) + ']'


lines = ['const FALCON = {',
         f"  halfSpanM: {d['halfSpanM']}, aOriginM: {d['aOriginM']},      // metres: full-spread half-span; model y of a = 0",
         '  keys: [' + ', '.join(f"'{k}'" for k in d['keys']) + '],',
         '  knots: ' + nums(d['knots']) + ',' + ' ' * 22 + '// the tuck at which each key is reached',
         '  wing: [']
lines += [f"    {nums(d['wing'][k])}," for k in d['keys']]
lines += ['  ],', f"  body: {nums(d['body'])},", f"  tail: {nums(d['tail'])},", f"  tailFan: {nums(d['tailFan'])},", '};']
src = open(a.html).read()
m = re.search(r'^const FALCON = \{.*?^\};', src, re.S | re.M)
open(a.html, 'w').write(src[:m.start()] + '\n'.join(lines) + src[m.end():])
print('FALCON table:', len(d['keys']), 'keys x', len(d['wing'][d['keys'][0]]) // 2, 'wing points; body',
      len(d['body']) // 2, 'tail', len(d['tail']) // 2, '-', len('\n'.join(lines)), 'characters')
