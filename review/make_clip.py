"""Build review clips the same way for every source, under an opaque id, so the reviewer can't tell page from real by format.

    uv run python make_clip.py page  NAME FRAMES_DIR PREFIX [--src-fps 60]          # PNG frames from capture_page.js
    uv run python make_clip.py video NAME FILE START DUR [--delogo x:y:w:h]          # real footage

Every clip: centre crop to 16:9, scale to 1280x720 (Lanczos), real speed, 30 fps, H.264 CRF 12 (near-lossless: small
birds smear under heavy compression), no audio. A 30 fps camera maps frame for frame and 60 fps page captures drop
every other frame, so both kinds sample real time 30 times a second and neither has duplicated frames (the v1 format,
0.5x at 24 fps, gave camera clips a duplicate every few frames and page clips none: a tell). The key (id -> source,
settings) goes to clips/key.json, which is never sent.
"""
import argparse
import json
import secrets
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLIPS = HERE / 'clips'
KEY = CLIPS / 'key.json'
W, H, OUT_FPS, SLOW = 1280, 720, 30, 1.0   # v2: real speed; v1 was 24 fps at 0.5x, which padded 30 fps cameras with duplicate frames


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate',
                          '-of', 'json', str(path)], capture_output=True, text=True, check=True).stdout
    s = json.loads(out)['streams'][0]
    num, den = map(int, s['r_frame_rate'].split('/'))
    return s['width'], s['height'], num / den


def chain(w, h, delogo=None, keep_rows=None):
    f = [f'crop={w}:{keep_rows}:0:0'] if keep_rows else []   # drop rows below an overlay (a camcorder timecode)
    h = keep_rows or h
    cw, ch = (w, round(w * 9 / 16)) if w * 9 <= h * 16 else (round(h * 16 / 9), h)
    f += [f'delogo={delogo}'] if delogo else []
    f += [f'crop={cw}:{ch}:{(w - cw) // 2}:{(h - ch) // 2}', f'scale={W}:{H}:flags=lanczos',
          f'setpts={1 / SLOW}*PTS', f'fps={OUT_FPS}']
    return ','.join(f)


def encode(inputs, vf, out):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-an', '-vf', vf, '-c:v', 'libx264', '-crf', '12',
                    '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(out)], check=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='kind', required=True)
    p = sub.add_parser('page'); p.add_argument('name'); p.add_argument('dir'); p.add_argument('prefix')
    p.add_argument('--src-fps', type=float, default=60); p.add_argument('--source', default='')
    v = sub.add_parser('video'); v.add_argument('name'); v.add_argument('file'); v.add_argument('start', type=float)
    v.add_argument('dur', type=float); v.add_argument('--delogo'); v.add_argument('--keep-rows', type=int); v.add_argument('--source', default='')
    a = ap.parse_args()

    CLIPS.mkdir(exist_ok=True)
    key = json.loads(KEY.read_text()) if KEY.exists() else {}
    if any(e['name'] == a.name for e in key.values()):
        raise SystemExit(f'{a.name} already built; delete its entry from {KEY} first')
    cid = secrets.token_hex(4)
    out = CLIPS / f'{cid}.mp4'
    if a.kind == 'page':
        first = sorted(Path(a.dir).glob(f'{a.prefix}_*.png'))
        want = [f'{a.prefix}_{k:04d}.png' for k in range(len(first))]
        if [p.name for p in first] != want:                          # the encoder reads prefix_0000.. in order
            raise SystemExit(f'{a.prefix}_*.png in {a.dir} are not exactly {want[0]}..{want[-1]}: '
                             f'{sorted(set(p.name for p in first) - set(want))[:5]}')
        w, h, _ = probe(first[0])
        encode(['-framerate', str(a.src_fps), '-i', str(Path(a.dir) / f'{a.prefix}_%04d.png')], chain(w, h), out)
        src_fps, dur = a.src_fps, len(first) / a.src_fps
        meta = {'frames_dir': str(a.dir), 'prefix': a.prefix, 'frames': len(first), 'size': [w, h]}
    else:
        w, h, src_fps = probe(a.file)
        encode(['-ss', str(a.start), '-t', str(a.dur), '-i', str(a.file)], chain(w, h, a.delogo, a.keep_rows), out)
        dur = a.dur
        meta = {'file': str(a.file), 'start': a.start, 'size': [w, h], 'delogo': a.delogo, 'keep_rows': a.keep_rows}
    sample_hz = min(OUT_FPS / SLOW, src_fps)                     # distinct real-time samples per second
    key[cid] = {'name': a.name, 'kind': a.kind, 'source': a.source, 'real_seconds': dur, 'video_seconds': dur / SLOW,
                'slow': SLOW, 'out_fps': OUT_FPS, 'src_fps': src_fps, 'sample_hz': sample_hz, 'nyquist_hz': sample_hz / 2,
                'size': [W, H], **meta}
    KEY.write_text(json.dumps(key, indent=1))
    print(cid, json.dumps(key[cid]))


if __name__ == '__main__':
    main()
