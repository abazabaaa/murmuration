"""The same pixel measurements on any clip, real or rendered, so variants of the page can be compared with footage.

    uv run python pixel_metrics.py CLIP_ID_OR_MP4 [...] [--frames 15,105] [--json out.json]

Method (after the two Codex reviews, scratchpad/codex_review/*/report.md), identical for every clip:
- Background: for each frame, the per-pixel median of the frames up to BG_T before and after it, each shifted to undo
  the camera's pan. Birds move several px a frame against the scene, so the median is the sky (clouds and scenery
  included) behind them. A plain median over the whole clip fails on real footage, where the camera pans to follow
  the flock (about 180 px over real_calm's 4 s) and cloud edges then read as birds; a spatial median fails on the
  page, where it counts the photographed sky's own texture as birds.
- Camera pan: frame-to-frame translation by phase correlation on the ground band (rows below GROUND), which is still
  scenery in every clip, accumulated over the clip.
- Birds: pixels darker than the background by at least THR grey levels, above row Y_MAX (scenery below is ignored),
  grouped 8-connected. Groups larger than 200 px or 25 px across are counted as merged masses, not birds.
- Blob span: largest distance between a blob's pixel centres, plus 1 (not the anatomical wingspan). Contrast: the
  blob's deepest darkening over the background there (near-black decodes to 0, so 1.0 means as dark as the
  format allows). Count: blobs per frame (a census only where birds are apart).
- Extent: P5-P95 box of blob centres. Densest cell: the 32x32 px cell with the most bird pixels.
- Shape change: for isolated blobs matched to the next frame, the best IoU after shifting by up to 1 px.
- Sky change: mean |difference| between consecutive frames over pixels with no bird in either frame, after shifting
  the second frame by the camera's motion (phase correlation): noise, compression and cloud motion together; 0 means a
  frozen backdrop. Camera motion: the median per-frame shift, in px.
"""
import argparse
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
W, H, THR, Y_MAX, GROUND, BG_T = 1280, 720, 12, 560, 600, 8


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-vf', 'format=gray', '-f', 'rawvideo', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)


def q(a, ps=(10, 50, 90)):
    return [round(float(v), 2) for v in np.percentile(a, ps)] if len(a) else None


def blobs(res, bg):
    mask = (res >= THR).astype(np.uint8)
    mask[Y_MAX:] = 0
    n, lab, st, cen = cv2.connectedComponentsWithStats(mask, connectivity=8)
    out, merged = [], 0
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if a > 200 or max(w, h) > 25:
            merged += a
            continue
        yy, xx = np.nonzero(lab[y:y + h, x:x + w] == i)
        pts = np.stack([xx, yy], 1).astype(np.float32)
        span = float(np.sqrt(((pts[:, None] - pts[None]) ** 2).sum(-1)).max()) + 1 if len(pts) > 1 else 1.0
        r = res[y:y + h, x:x + w][yy, xx]
        k = int(np.argmax(r))
        out.append({'c': cen[i], 'span': span, 'area': int(a), 'pts': np.stack([xx + x, yy + y], 1),
                    'contrast': float(r[k] / max(bg[y + yy[k], x + xx[k]], 1))})
    return out, mask, merged


def iou_pairs(fa, fb):
    if not fa or not fb:
        return []
    ca, cb = np.array([b['c'] for b in fa]), np.array([b['c'] for b in fb])
    da = np.sqrt(((ca[:, None] - ca[None]) ** 2).sum(-1)); np.fill_diagonal(da, 1e9)
    dab = np.sqrt(((ca[:, None] - cb[None]) ** 2).sum(-1))
    out = []
    for i, b in enumerate(fa):
        j = int(np.argmin(dab[i]))
        if dab[i, j] > 6 or da[i].min() < 10 or int(np.argmin(dab[:, j])) != i or min(b['area'], fb[j]['area']) < 3:
            continue
        A = np.zeros((40, 40), bool); B = A.copy()
        for M, bl in ((A, b), (B, fb[j])):
            p = bl['pts'] - np.round(bl['c']).astype(int) + 20
            p = p[(p >= 0).all(1) & (p < 40).all(1)]
            M[p[:, 1], p[:, 0]] = True
        best = max((A & np.roll(np.roll(B, dy, 0), dx, 1)).sum() / max((A | np.roll(np.roll(B, dy, 0), dx, 1)).sum(), 1)
                   for dy in (-1, 0, 1) for dx in (-1, 0, 1))
        out.append(float(best))
    return out


def pan(v):
    t = np.zeros((len(v), 2))
    for k in range(1, len(v)):
        (dx, dy), _ = cv2.phaseCorrelate(v[k - 1][GROUND:], v[k][GROUND:])
        t[k] = t[k - 1] + (dx, dy)
    return t


def shifted(frame, d):
    return cv2.warpAffine(frame, np.float32([[1, 0, d[0]], [0, 1, d[1]]]), (W, H), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REPLICATE)


def background(v, t, k):
    js = [j for j in range(k - BG_T, k + BG_T + 1, 2) if 0 <= j < len(v) and j != k]
    return np.median(np.stack([shifted(v[j], t[k] - t[j]) for j in js]), axis=0)


def measure(path, frames):
    v = load(path)
    t = pan(v)
    out = {'frames': len(v)}
    per = {}
    for k in frames:
        bg = background(v, t, k)
        res = np.maximum(bg - v[k], 0)
        bl, mask, merged = blobs(res, bg)
        c = np.array([b['c'] for b in bl]) if bl else np.zeros((0, 2))
        cells = cv2.boxFilter(mask.astype(np.float32), -1, (32, 32), normalize=True)
        dark = cv2.boxFilter(res * (mask > 0), -1, (32, 32), normalize=True)
        iy, ix = np.unravel_index(np.argmax(cells), cells.shape)
        per[k] = {'blobs': len(bl), 'merged_px': int(merged), 'span': q([b['span'] for b in bl]),
                  'contrast': q([b['contrast'] for b in bl]),
                  'contrast_3to8px': q([b['contrast'] for b in bl if 3 <= b['span'] <= 8]),
                  'extent_px': [round(float(a), 0) for a in (np.percentile(c[:, 0], 95) - np.percentile(c[:, 0], 5),
                                                            np.percentile(c[:, 1], 95) - np.percentile(c[:, 1], 5))] if len(c) else None,
                  'densest_cell_fill': round(float(cells[iy, ix]), 3), 'densest_cell_darkening': round(float(dark[iy, ix]), 2)}
        bg1 = background(v, t, k + 1)
        per[k]['iou_next'] = q(iou_pairs(bl, blobs(np.maximum(bg1 - v[k + 1], 0), bg1)[0]))
    out['per_frame'] = per
    sky, shift = [], []
    for k in range(0, len(v) - 1, 4):
        a, b = v[k], v[k + 1]
        b = shifted(b, t[k] - t[k + 1])
        bga = background(v, t, k)
        clear = (np.abs(bga - a) < 4) & (np.abs(bga - b) < 4)
        clear[Y_MAX:] = False
        clear[:8] = clear[:, :8] = clear[:, -8:] = False
        sky.append(float(np.abs(a - b)[clear].mean()))
        shift.append(float(np.hypot(*(t[k + 1] - t[k]))))
    out['sky_change'] = round(float(np.median(sky)), 3)
    out['camera_shift_px'] = round(float(np.median(shift)), 2)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('clips', nargs='+')
    ap.add_argument('--frames', default='15,105')
    ap.add_argument('--json')
    a = ap.parse_args()
    key = json.loads((HERE / 'clips' / 'key.json').read_text())
    frames = [int(x) for x in a.frames.split(',')]
    allres = {}
    for c in a.clips:
        path = HERE / 'clips' / f'{c}.mp4' if c in key else Path(c)
        name = key[c]['name'] if c in key else path.stem
        r = measure(path, frames)
        allres[name] = r
        for k, p in r['per_frame'].items():
            print(f'{name:16s} f{k:<4d} blobs {p["blobs"]:5d}  span {p["span"]}  contrast {p["contrast"]} (3-8 px {p["contrast_3to8px"]})  '
                  f'extent {p["extent_px"]}  densest cell {p["densest_cell_fill"]:.2f} / {p["densest_cell_darkening"]:.1f}  '
                  f'merged {p["merged_px"]} px  iou {p["iou_next"]}')
        print(f'{name:16s} sky change {r["sky_change"]}  camera motion {r["camera_shift_px"]} px/frame')
    if a.json:
        Path(a.json).write_text(json.dumps(allres, indent=1))


if __name__ == '__main__':
    main()
