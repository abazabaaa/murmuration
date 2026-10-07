"""Agentic video review of one clip with Gemini (Interactions API), then a deterministic verdict.

    uv run python harness.py CLIP_ID [--mode agentic|static] [--model gemini-3.8-flash] [--max-stills 8]

Stage A, watch: the clip with Google Search and a get_frame tool that serves full-resolution stills and magnified
crops (ultra_high). In agentic mode (default; Gemini 3.8/3.7/3.6 Flash only) the model navigates the video itself,
loading stretches at the frame rate and resolution it chooses (processing_call/processing_result steps); in static
mode it gets every frame at 30 fps, 'high' resolution. It asks for stills, inspects them and writes timestamped
notes. Code execution is not offered here: the API refuses it next to video, in either mode.
Stage B, measure: the stills it saw and its notes, with code execution and Google Search, answering in the
Extraction schema (schema.py), validated locally with one retry.
Then engine.score() applies the policy's gates and rules, per axis.

Every call is checked against the budget before it is made and recorded in runs/ledger.jsonl after. History is
sent back in full each turn (store=False), with thought signatures as received. Everything a run sent and got back
(minus the key, which is never in the payload) is saved in runs/<run id>/.
"""
import argparse
import base64
import datetime as dt
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

from PIL import Image

import engine
import gemini
from schema import Extraction, api_schema

HERE = gemini.HERE
KEY = json.loads((HERE / 'clips' / 'key.json').read_text())
BRIEF = (HERE / 'brief.md').read_text()
BRIEF_SHA = __import__('hashlib').sha256(BRIEF.encode()).hexdigest()[:12]   # runs on different briefs are never pooled
PROMPT_VERSION = 'b3'      # stage-B wording: b1 until 2026-10-07; b2 let measurements overrule the notes (contradictions) and
                           # named the 8 px threshold; b3 drops the threshold (the one b2 real run then measured 8.7 px)
VIDEO_TOKENS_PER_FRAME = 264            # static: measured 2.0 s at 24 fps, 'high' -> 12683 input tokens (smoke.py fps)
AGENTIC_TOKENS_PER_S = 15000            # agentic: loaded media bills as tool-use tokens; 26k for 2 s at 1080p, 'high' (smoke.py agentic)
STILL_TOKENS = 2240                     # ultra_high image, upper bound
UPLOADS = gemini.RUNS / 'uploads.json'

GET_FRAME = {
    'type': 'function', 'name': 'get_frame',
    'description': 'Full-resolution still of the clip frame nearest a time (frames are 1/30 s apart), optionally '
                   'cropped to a box and magnified. Returns the image and a label with its id (cite it), the frame '
                   'number and its time, the box in pixels of the 1280x720 frame and the magnification. Asking again '
                   'for a frame and box already served returns a note, not a second copy.',
    'parameters': {'type': 'object', 'properties': {
        't': {'type': 'string', 'description': 'Time in the clip, seconds ("1.5") or "MM:SS.ss".'},
        'box_2d': {'type': 'array', 'items': {'type': 'number'}, 'minItems': 4, 'maxItems': 4,
                   'description': 'Optional crop [ymin, xmin, ymax, xmax], normalised 0-1000.'}},
        'required': ['t']}}


def clip_file(cid):
    return HERE / 'clips' / f'{cid}.mp4'


def upload(c, cid):
    """Upload once and reuse for 40 h (the Files API keeps files 48 h)."""
    cache = json.loads(UPLOADS.read_text()) if UPLOADS.exists() else {}
    e = cache.get(cid)
    if e and time.time() - e['at'] < 40 * 3600:
        try:
            f = c.files.get(name=e['name'])
            if str(f.state).upper().endswith('ACTIVE'):
                return f
        except Exception:
            pass
    f = c.files.upload(file=str(clip_file(cid)), config={'display_name': cid, 'mime_type': 'video/mp4'})
    while str(f.state).upper().endswith('PROCESSING'):
        time.sleep(1)
        f = c.files.get(name=f.name)
    cache[cid] = {'name': f.name, 'uri': f.uri, 'at': time.time()}
    gemini.RUNS.mkdir(exist_ok=True)
    UPLOADS.write_text(json.dumps(cache, indent=1))
    return f


def parse_t(t, dur):
    s = str(t).strip()
    m = re.match(r'^(\d{1,2}):(\d{1,2}(?:\.\d+)?)$', s)
    v = int(m[1]) * 60 + float(m[2]) if m else float(s)
    return min(max(v, 0.0), max(dur - 1 / 48, 0.0))


class Stills:
    """Serves get_frame calls from the clip file and remembers what it served."""

    def __init__(self, cid, out_dir, limit):
        self.cid, self.dir, self.limit, self.served = cid, out_dir / 'stills', limit, {}
        self.dir.mkdir(parents=True, exist_ok=True)
        self.dur = KEY[cid]['video_seconds']
        self.fps = KEY[cid]['out_fps']
        self.frames = round(self.dur * self.fps)

    def get(self, args):
        if len(self.served) >= self.limit:
            return [{'type': 'text', 'text': f'Still limit ({self.limit}) reached: finish with what you have.'}], None
        box = args.get('box_2d')
        if box and len(box) == 4 and max(abs(float(v)) for v in box) <= 1:
            return [{'type': 'text', 'text': f'box_2d {box} looks like 0-1 fractions; it is in 0-1000 (e.g. [450, 500, '
                                             f'600, 650]). No still was taken and none was counted.'}], None
        # By frame number, not by seeking: an output seek (-ss) takes the next frame at or after a rounded time, so
        # requests at 0.50/0.53/0.57/0.60 s once returned frames 15, 16, 18, 18, and two identical stills were read
        # as frozen wings (Codex review, 2026-10-07).
        n = min(max(round(parse_t(args.get('t', 0), self.dur) * self.fps), 0), self.frames - 1)
        t = n / self.fps
        sid = f's{len(self.served) + 1}'
        full = self.dir / f'{sid}_full.png'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(clip_file(self.cid)), '-vf', f'select=eq(n\\,{n})',
                        '-fps_mode', 'passthrough', '-frames:v', '1', str(full)], check=True)
        im = Image.open(full)
        W, H = im.size
        box = args.get('box_2d')
        mag = 1.0
        if box and len(box) == 4:
            y0, x0, y1, x1 = [min(max(float(v), 0), 1000) / 1000 for v in box]
            x0, x1 = sorted((x0 * W, x1 * W)); y0, y1 = sorted((y0 * H, y1 * H))
            if x1 - x0 < 32: x0, x1 = max(0, (x0 + x1) / 2 - 16), min(W, (x0 + x1) / 2 + 16)
            if y1 - y0 < 32: y0, y1 = max(0, (y0 + y1) / 2 - 16), min(H, (y0 + y1) / 2 + 16)
            px = tuple(round(v) for v in (x0, y0, x1, y1))
            im = im.crop(px)
            mag = min(8.0, 1024 / max(im.size))
            if mag > 1:
                im = im.resize((round(im.size[0] * mag), round(im.size[1] * mag)), Image.LANCZOS)
            else:
                mag = 1.0
        else:
            px = (0, 0, W, H)
        same = [k for k, v in self.served.items() if v.get('frame') == n]
        if any(self.served[k]['box_px'] == px for k in same):
            full.unlink()
            k = next(k for k in same if self.served[k]['box_px'] == px)
            return [{'type': 'text', 'text': f'That is frame {n} ({int(t // 60):02d}:{t % 60:05.2f}) with the same box as '
                                             f'still {k}, already served; frames are 1/{self.fps:g} s apart. No still was '
                                             f'taken and none was counted.'}], None
        path = self.dir / f'{sid}.png'
        im.save(path)
        label = (f'still {sid}: frame {n} of {self.frames}, time {int(t // 60):02d}:{t % 60:05.2f}, box x {px[0]}-{px[2]} '
                 f'y {px[1]}-{px[3]} px of the {W}x{H} frame, shown at {mag:.1f}x ({im.size[0]}x{im.size[1]} px)'
                 + (f'; same frame as {", ".join(same)}' if same else ''))
        self.served[sid] = {'t': t, 'frame': n, 'box_px': px, 'magnification': mag, 'size': im.size, 'label': label,
                            'path': str(path)}
        return [image_block(path), {'type': 'text', 'text': label}], sid


def image_block(path):
    return {'type': 'image', 'mime_type': 'image/png', 'resolution': 'ultra_high',
            'data': base64.b64encode(Path(path).read_bytes()).decode()}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def scrub(node):
    """A request body with inline media replaced by its hash and size, so it can be saved beside the response."""
    if isinstance(node, dict):
        return {k: ({'sha256': hashlib.sha256(v.encode()).hexdigest()[:16], 'base64_chars': len(v)}
                    if k == 'data' and isinstance(v, str) and len(v) > 256 else scrub(v)) for k, v in node.items()}
    if isinstance(node, list):
        return [scrub(x) for x in node]
    return node


def text_of(steps):
    outs = [s for s in steps if s.get('type') == 'model_output']
    return ''.join(b.get('text', '') for b in (outs[-1].get('content') or []) if b.get('type') == 'text') if outs else ''


class Run:
    def __init__(self, cid, model, max_stills, mode='agentic'):
        self.cid, self.model, self.mode = cid, model, mode
        self.id = f'{dt.datetime.now():%Y%m%d-%H%M%S}-{cid}-{model.split("-")[1]}-{mode}'
        self.dir = gemini.RUNS / self.id
        self.dir.mkdir(parents=True)
        self.spent, self.calls, self.c = 0.0, [], gemini.client()
        self.stills = Stills(cid, self.dir, max_stills)
        self.sources = {f: sha(HERE / f) for f in ('brief.md', 'policy.md', 'ruleset.json', 'engine.py', 'schema.py', 'harness.py')}
        self.sources['clip'] = sha(HERE / 'clips' / f'{cid}.mp4')     # hashed at the start: the files this run used

    def call(self, stage, body, input_tokens, max_out, searches):
        gemini.check_budget(gemini.bound(self.model, input_tokens, max_out, searches), self.spent)
        t0 = time.time()
        for attempt in range(3):                                      # agentic video returns the odd transient 500
            try:
                it = self.c.interactions.create(model=self.model, store=False, timeout=900, **body)
                break
            except Exception as e:
                if attempt == 2 or not any(code in str(e) for code in ('Error code: 500', 'Error code: 503')):
                    raise
                print(f'  {stage}: server error ({str(e)[:60]}); retrying in {15 * (attempt + 1)} s')
                time.sleep(15 * (attempt + 1))
        n = len(self.calls) + 1                                       # what was sent, images by hash (provenance, v0.4)
        (self.dir / f'call{n:02d}_{stage}_request.json').write_text(json.dumps(scrub(body), indent=1, default=str))
        usage = gemini.usage_dict(it.usage)
        usd = gemini.record(self.id, self.model, usage, note=stage)
        self.spent += usd
        steps = [s.model_dump(mode='json', exclude_none=True) for s in it.steps or []]
        self.calls.append({'stage': stage, 'status': it.status, 'usd': round(usd, 5), 'seconds': round(time.time() - t0, 1),
                           'usage': usage, 'step_types': [s['type'] for s in steps]})
        n = len(self.calls)
        (self.dir / f'call{n:02d}_{stage}.json').write_text(json.dumps({'status': it.status, 'steps': steps, 'usage': usage}, indent=1))
        print(f'  call {n} {stage:8s} {it.status:15s} ${usd:.4f} {time.time() - t0:5.0f}s  {[s["type"] for s in steps]}')
        return it.status, steps, usage

    def stage_a(self, video, max_turns=10):
        prompt = BRIEF.replace('{max_stills}', str(self.stills.limit)) + (
            '\n\nGo through the whole clip, then ask for stills where you want to look closely. When you have looked at '
            'them, write your notes: numbered observations, each starting with its MM:SS.s timestamp and citing still ids '
            'where they apply, grouped under S0-S5 and R1-R6, and a short list of what should be measured on the stills.')
        history = [{'type': 'user_input', 'content': [video, {'type': 'text', 'text': prompt}]}]
        secs = KEY[self.cid]['video_seconds']
        video_tokens = round(secs * (AGENTIC_TOKENS_PER_S if self.mode == 'agentic' else 30 * VIDEO_TOKENS_PER_FRAME))
        out_so_far = 0
        for turn in range(max_turns + 2):
            closing = turn >= max_turns - 1                           # tool_choice 'none' is ignored: refuse calls instead
            gen = {'thinking_level': 'high', 'thinking_summaries': 'auto', 'max_output_tokens': 12000}
            est = video_tokens + len(self.stills.served) * STILL_TOKENS + len(prompt) // 3 + out_so_far
            status, steps, usage = self.call('watch', {'input': history, 'tools': [{'type': 'google_search'}, GET_FRAME],
                                                       'generation_config': gen}, est, 12000, 5)
            out_so_far += usage.get('total_output_tokens', 0) + usage.get('total_thought_tokens', 0)
            history += steps
            calls = [s for s in steps if s['type'] == 'function_call']
            if status != 'requires_action' or not calls:
                notes = text_of(steps)
                if not notes.strip():
                    raise RuntimeError(f'stage A ended ({status}) without notes')
                return notes, history
            for s in calls:
                if closing:
                    result = [{'type': 'text', 'text': 'No more stills or turns: write your notes now from what you have seen.'}]
                else:
                    result, _ = self.stills.get(s.get('arguments') or {})
                history.append({'type': 'function_result', 'name': s['name'], 'call_id': s['id'], 'result': result})
        raise RuntimeError('stage A: the model kept asking for stills after it was told to write its notes')

    def stage_b(self, notes):
        content = []
        for sid, s in self.stills.served.items():
            content += [{'type': 'text', 'text': s['label']}, image_block(s['path'])]
        prompt = (BRIEF.replace('{max_stills}', str(self.stills.limit)) +
                  '\n\n## Your notes from watching the clip\n\n' + notes +
                  '\n\n## Now measure and answer\n\nThe stills you inspected are above, each with its label. Use code '
                  'execution on them to measure what can be measured (for example the wingtip-to-wingtip length of '
                  'resolved birds, converted to pixels of the 1280x720 frame using each still\'s box and magnification; '
                  'how many birds a frame holds; how much their body axes vary), and Google Search for any fact you '
                  'need. Use code execution at most four times. Then answer in the JSON schema. Every judgement cites '
                  'timestamps from your notes and, for S1 and S4, the still ids it rests on.\n\nYour notes were written '
                  'while watching, before anything was measured. Where a measurement contradicts them, the measurement '
                  'wins: judge from the measurement, and list each contradiction in `contradictions` (what the notes '
                  'said, what you measured, which you kept).')
        content.append({'type': 'text', 'text': prompt})
        body = {'input': [{'type': 'user_input', 'content': content}],
                'tools': [{'type': 'code_execution'}, {'type': 'google_search'}],
                'response_format': {'type': 'text', 'mime_type': 'application/json', 'schema': api_schema(Extraction)},
                'generation_config': {'thinking_level': 'high', 'thinking_summaries': 'auto', 'max_output_tokens': 16000}}
        est = len(self.stills.served) * STILL_TOKENS + len(prompt) // 3 + 4000
        try:
            status, steps, _ = self.call('measure', body, est, 16000, 5)
        except Exception as e:
            if 'too many tool calls' not in str(e):
                raise
            print('  measure: model made too many tool calls; retrying without code execution')
            body['tools'] = [{'type': 'google_search'}]
            status, steps, _ = self.call('measure', body, est, 16000, 5)
        raw = text_of(steps)
        try:
            return Extraction.model_validate_json(raw), raw
        except Exception as err:
            print(f'  answer failed validation ({str(err)[:120]}...); one retry')
            body['input'] = body['input'] + steps + [{'type': 'user_input', 'content': [{'type': 'text', 'text':
                f'Your answer failed validation:\n{err}\nReturn the corrected JSON only.'}]}]
            body['tools'] = []
            status, steps2, _ = self.call('fix', body, est + 8000, 16000, 0)
            raw = text_of(steps2)
            return Extraction.model_validate_json(raw), raw

    def review(self, video_part):
        notes, _ = self.stage_a(video_part)
        (self.dir / 'notes.md').write_text(notes)
        ext, raw = self.stage_b(notes)
        (self.dir / 'extraction.json').write_text(ext.model_dump_json(indent=1))
        result = engine.score(ext.model_dump(mode='json'), KEY[self.cid], set(self.stills.served))
        card = engine.card(result, self.cid)
        (self.dir / 'result.json').write_text(json.dumps({k: v for k, v in result.items() if k != 'gated'}, indent=1, default=str))
        (self.dir / 'card.txt').write_text(card)
        (self.dir / 'run.json').write_text(json.dumps({
            'run': self.id, 'clip': self.cid, 'model': self.model, 'mode': self.mode, 'brief_sha': BRIEF_SHA,
            'prompt_version': PROMPT_VERSION,
            'navigation_steps': sum(c['step_types'].count('processing_call') for c in self.calls), 'ruleset': result['ruleset_version'],
            'usd': round(self.spent, 4), 'calls': self.calls,
            'stills': {k: {**{kk: vv for kk, vv in v.items() if kk != 'path'}, 'sha256': sha(v['path'])}
                       for k, v in self.stills.served.items()},
            'sources': self.sources,
            'axes': result['axes'], 'gates': result['gates']}, indent=1, default=str))
        return result, card


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('clip')
    ap.add_argument('--model', default='gemini-3.8-flash', choices=list(gemini.PRICES))
    ap.add_argument('--mode', default='agentic', choices=['agentic', 'static'])
    ap.add_argument('--max-stills', type=int, default=12)
    a = ap.parse_args()
    if a.mode == 'agentic' and 'flash' not in a.model:
        raise SystemExit(f'agentic video is Flash-only (3.8/3.7/3.6 Flash); {a.model} needs --mode static')
    run = Run(a.clip, a.model, a.max_stills, a.mode)
    f = upload(run.c, a.clip)
    video = {'type': 'video', 'uri': f.uri, 'mime_type': 'video/mp4', 'resolution': 'high',
             'processing': 'agentic' if a.mode == 'agentic' else {'type': 'static', 'fps': 30}}
    print(f'run {run.id}  {a.mode} {a.model}  (ledger before: ${gemini.spent():.2f})')
    _, card = run.review(video)
    print(card)
    print(f'run cost ${run.spent:.3f}; ledger total ${gemini.spent():.2f} of ${gemini.CAP_TOTAL:.0f}')


if __name__ == '__main__':
    main()
