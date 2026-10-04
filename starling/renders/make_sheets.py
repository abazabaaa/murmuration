"""Final contact sheets for the starling renders (run from renders/)."""
import json
from PIL import Image, ImageDraw, ImageFont
ORDER = ['glide', 'flap_top', 'flap_mid', 'flap_bottom', 'upstroke', 'upstroke_top', 'bound']
LABEL = {'glide': 'Glide', 'flap_top': 'Top of downstroke', 'flap_mid': 'Mid-downstroke', 'flap_bottom': 'Bottom of downstroke',
         'upstroke': 'Mid-upstroke (hand flexed)', 'upstroke_top': 'Late upstroke', 'bound': 'Bound (wings folded)'}
TARGET = {'glide': 'b/L 1.8-2.2', 'flap_top': 'tip +12..+16 cm, 1.3-2.9 aft', 'flap_mid': 'full span',
          'flap_bottom': 'tip -14.5..-16.5 cm, ~6.3 aft', 'upstroke': 'span 0.40-0.60 of full',
          'upstroke_top': 'span 0.5-0.7 of full', 'bound': 'span 0.12-0.20 of full'}
TIP = ('flap_top', 'flap_bottom', 'upstroke_top')
try:
    F = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 22); Fs = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 17)
except OSError:
    F = Fs = ImageFont.load_default()
met = json.load(open('silhouettes/metrics.json'))
full = met['flap_mid']['width_m']

def sheet(kind, view, out, cols=4, tw=440, th=440, crop=None):
    rows = (len(ORDER) + cols - 1) // cols
    H = 90                                                        # three header lines
    S = Image.new('RGB', (cols * tw, rows * (th + H)), 'white'); d = ImageDraw.Draw(S)
    for i, n in enumerate(ORDER):
        im = Image.open(f'{kind}/{n}__{view}.png').convert('RGB')
        if crop: im = im.crop(crop)
        im.thumbnail((tw, th)); x, y = (i % cols) * tw, (i // cols) * (th + H)
        S.paste(im, (x + (tw - im.width) // 2, y + H))
        m = met[n]; b = m['span_over_L']
        tip = f"   tip {100 * m['tip_above_shoulder_m']:+.1f} cm, {100 * m['tip_aft_of_shoulder_m']:.1f} aft" if n in TIP else ''
        d.text((x + 8, y + 6), LABEL[n], fill='black', font=F)
        d.text((x + 8, y + 36), f"b/L {b:.2f} ({m['width_m'] / full:.0%} of full){tip}", fill=(60, 60, 60), font=Fs)
        d.text((x + 8, y + 60), f"target {TARGET[n]}", fill=(120, 120, 120), font=Fs)
    S.save(out)

# renders are 1200 px over 2.43 half-spans: the full span is 988 px wide, so keep x 80..1120
sheet('silhouettes', 'top', 'sheet_silhouettes_top.png', crop=(80, 200, 1120, 1000), th=400)
sheet('silhouettes', 'front', 'sheet_silhouettes_front.png', crop=(80, 180, 1120, 1020), th=356)
sheet('silhouettes', 'side', 'sheet_silhouettes_side.png', crop=(240, 180, 960, 1020), th=440)
sheet('shaded', 'below', 'sheet_shaded_below.png', th=293)
sheet('shaded', 'above', 'sheet_shaded_above.png', th=293)
