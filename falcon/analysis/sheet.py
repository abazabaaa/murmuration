"""Contact sheet of pose renders: sheet.py DIR VIEW OUT [cols]"""
import sys, json, glob
from PIL import Image, ImageDraw
d, view, out = sys.argv[1:4]; cols = int(sys.argv[4]) if len(sys.argv) > 4 else 5
order = ['soar', 'glide', 'flap_top', 'flap_mid', 'flap_bottom', 'upstroke', 'upstroke_top', 'stoop_tuck', 'pullout_early', 'stoop_m']
met = json.load(open(f'{d}/metrics.json'))
fs = [(n, f'{d}/{n}__{view}.png') for n in order if glob.glob(f'{d}/{n}__{view}.png')]
T = 400; rows = (len(fs) + cols - 1) // cols
sheet = Image.new('RGB', (cols * T, rows * (T + 30)), 'white')
for i, (n, f) in enumerate(fs):
    im = Image.open(f).convert('RGB').resize((T, T))
    x, y = (i % cols) * T, (i // cols) * (T + 30)
    sheet.paste(im, (x, y + 30))
    m = met.get(n, {})
    ImageDraw.Draw(sheet).text((x + 4, y + 2), f"{n}  b/L {m.get('span_over_L', 0):.2f}", fill='black')
    ImageDraw.Draw(sheet).rectangle((x, y + 30, x + T - 1, y + 30 + T - 1), outline=(200, 200, 200))
sheet.save(out)
