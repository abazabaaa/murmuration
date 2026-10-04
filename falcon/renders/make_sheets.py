"""Final contact sheets for the peregrine renders."""
import json
from PIL import Image, ImageDraw, ImageFont
ORDER = ['soar', 'glide', 'flap_top', 'flap_mid', 'flap_bottom', 'upstroke', 'upstroke_top', 'stoop_tuck', 'pullout_early', 'stoop_m']
LABEL = {'soar': 'Soar', 'glide': 'Glide', 'flap_top': 'Downstroke start (+36°)', 'flap_mid': 'Mid-downstroke',
         'flap_bottom': 'Downstroke end (−36°)', 'upstroke': 'Upstroke (hand flexed)', 'upstroke_top': 'Late upstroke',
         'stoop_tuck': 'Stoop, tucked', 'pullout_early': 'Stoop, early pull-out', 'stoop_m': 'Stoop, M-shape'}
TARGET = {'soar': 'b/L 1.9–2.4', 'glide': 'b/L ~2.0 (1.7–2.4)', 'flap_top': '+36° (Mills 2018)', 'flap_mid': 'full span',
          'flap_bottom': '−36°', 'upstroke': 'span 0.5–0.7 of full', 'upstroke_top': '—', 'stoop_tuck': 'w/L 0.26–0.36',
          'pullout_early': 'b/L 0.76', 'stoop_m': 'b/L 1.2–1.7, hand 52°'}
try:
    F = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 22); Fs = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 17)
except OSError:
    F = Fs = ImageFont.load_default()
met = json.load(open('silhouettes/metrics.json'))
full = met['soar']['span_over_L']

def sheet(kind, view, out, cols=5, tw=440, th=440, crop=None):
    rows = (len(ORDER) + cols - 1) // cols
    S = Image.new('RGB', (cols * tw, rows * (th + 64)), 'white'); d = ImageDraw.Draw(S)
    for i, n in enumerate(ORDER):
        im = Image.open(f'{kind}/{n}__{view}.png').convert('RGB')
        if crop: im = im.crop(crop)
        im.thumbnail((tw, th)); x, y = (i % cols) * tw, (i // cols) * (th + 64)
        S.paste(im, (x + (tw - im.width) // 2, y + 64))
        m = met[n]; b = m['span_over_L']
        d.text((x + 8, y + 6), LABEL[n], fill='black', font=F)
        d.text((x + 8, y + 36), f"b/L {b:.2f} ({b / full:.0%} of full)   target {TARGET[n]}", fill=(90, 90, 90), font=Fs)
    S.save(out)

sheet('silhouettes', 'top', 'sheet_silhouettes_top.png', crop=(150, 150, 1050, 1050))
sheet('silhouettes', 'front', 'sheet_silhouettes_front.png', crop=(150, 300, 1050, 900), th=300)
sheet('shaded', 'below', 'sheet_shaded_below.png', th=293)
sheet('shaded', 'above', 'sheet_shaded_above.png', th=293)
