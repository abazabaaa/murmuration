"""Smoke tests that settle what the docs leave open, for a few cents. Results go to runs/smoke/.

    uv run python smoke.py fps        # is static fps above 1 honoured? tokens per frame at 'high'; what fps 30 does
    uv run python smoke.py tools      # response_format + google_search + code_execution + thinking 'high', per model
    uv run python smoke.py function   # a function declaration next to built-in tools (python-genai #2761)
    uv run python smoke.py stream     # store=False + stream=True: what the events carry
"""
import json
import sys
import time

import gemini

CLIP = gemini.HERE / 'clips' / 'smoke_2s.mp4'   # 2.0 s, 30 fps, 1920x1080, real murmuration (Strumpshaw Fen)
OUT = gemini.RUNS / 'smoke'
MODELS = ['gemini-3.1-pro-preview', 'gemini-3.8-flash']


def upload(c):
    f = c.files.upload(file=str(CLIP))
    while f.state and str(f.state).upper().endswith('PROCESSING'):
        time.sleep(1)
        f = c.files.get(name=f.name)
    return f


def video(f, fps, resolution='high'):
    return {'type': 'video', 'uri': f.uri, 'mime_type': 'video/mp4', 'resolution': resolution,
            'processing': {'type': 'static', 'fps': fps}}


def call(c, name, model, body, input_bound, max_out, max_searches=0):
    gemini.check_budget(gemini.bound(model, input_bound, max_out, max_searches))
    t0 = time.time()
    try:
        it = c.interactions.create(model=model, store=False, **body)
    except Exception as e:  # report the API's answer; nothing was billed if it was refused
        print(f'{name:28s} {model:24s} ERROR {type(e).__name__}: {str(e)[:300]}')
        return None
    usage = gemini.usage_dict(it.usage)
    usd = gemini.record(f'smoke-{name}', model, usage, note=name)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f'{name}_{model}.json').write_text(json.dumps(it.model_dump(mode='json', exclude_none=True), indent=1))
    steps = [s.type for s in (it.steps or [])]
    print(f'{name:28s} {model:24s} {it.status:10s} in {usage.get("total_input_tokens")} out {usage.get("total_output_tokens")} '
          f'thought {usage.get("total_thought_tokens")} tool {usage.get("total_tool_use_tokens")} ${usd:.4f} {time.time() - t0:.0f}s steps {steps}')
    return it


def fps(c, f):
    for model in MODELS:
        for n in (1, 24):
            call(c, f'fps{n}', model, {
                'input': [video(f, n), {'type': 'text', 'text': 'In one sentence: what is in this video?'}],
                'generation_config': {'thinking_level': 'low', 'max_output_tokens': 400}}, 2 * n * 280 + 200, 400)
    call(c, 'fps30', MODELS[1], {
        'input': [video(f, 30), {'type': 'text', 'text': 'In one sentence: what is in this video?'}],
        'generation_config': {'thinking_level': 'low', 'max_output_tokens': 400}}, 2 * 30 * 280 + 200, 400)
    print(f'expected input tokens for 2.0 s at fps 1 / 24 / 30 at high (280 per frame): 560 / 13440 / 16800 plus the prompt')


SCHEMA = {
    'type': 'object',
    'properties': {
        'birds_visible_estimate': {'type': 'integer', 'description': 'Rough count of birds visible at 00:01.'},
        'species_guess': {'type': 'string'},
        'wingbeat_hz_from_literature': {'type': ['number', 'null'], 'description': 'Typical European starling wingbeat frequency, from a web search.'},
        'source_url': {'type': ['string', 'null']},
        'wingbeat_period_ms': {'type': ['number', 'null'], 'description': 'Computed with code execution from the frequency.'},
    },
    'required': ['birds_visible_estimate', 'species_guess', 'wingbeat_hz_from_literature', 'source_url', 'wingbeat_period_ms'],
}


def tools(c, f):
    import base64
    still = {'type': 'image', 'mime_type': 'image/png', 'resolution': 'ultra_high',
             'data': base64.b64encode((gemini.HERE / 'clips' / 'smoke_still.png').read_bytes()).decode()}
    ask = ('Estimate how many birds are visible{at} and guess the species. Search the web for the typical '
           'wingbeat frequency of the European starling, give the source URL, and {calc} convert '
           'it to a wingbeat period in milliseconds.')
    for model in MODELS:
        # video + search + schema (code execution refuses video)
        call(c, 'tools_video', model, {
            'input': [video(f, 1), {'type': 'text', 'text': ask.format(at=' at 00:01', calc='')}],
            'tools': [{'type': 'google_search'}],
            'response_format': {'type': 'text', 'mime_type': 'application/json', 'schema': SCHEMA},
            'generation_config': {'thinking_level': 'high', 'max_output_tokens': 8192}}, 2 * 280 + 400, 8192, 5)
        # still image + search + code execution + schema
        call(c, 'tools_image', model, {
            'input': [still, {'type': 'text', 'text': ask.format(at=' in this frame', calc='use code execution to ')}],
            'tools': [{'type': 'google_search'}, {'type': 'code_execution'}],
            'response_format': {'type': 'text', 'mime_type': 'application/json', 'schema': SCHEMA},
            'generation_config': {'thinking_level': 'high', 'max_output_tokens': 8192}}, 2240 + 400, 8192, 5)


def function(c, f):
    decl = {'type': 'function', 'name': 'get_frame', 'description': 'Return a full-resolution still of the video at a time.',
            'parameters': {'type': 'object', 'properties': {'t_seconds': {'type': 'number'}}, 'required': ['t_seconds']}}
    for model in MODELS:
        call(c, 'function', model, {
            'input': [video(f, 1), {'type': 'text', 'text': 'Call get_frame for t = 1.0 s so you can look closely at the birds.'}],
            'tools': [{'type': 'google_search'}, decl],
            'generation_config': {'thinking_level': 'low', 'max_output_tokens': 1024}}, 2 * 280 + 300, 1024, 1)


def stream(c, f):
    model = MODELS[1]
    gemini.check_budget(gemini.bound(model, 2 * 280 + 200, 400))
    events, final = [], None
    for ev in c.interactions.create(model=model, store=False, stream=True, input=[video(f, 1), {
            'type': 'text', 'text': 'In one sentence: what is in this video?'}],
            generation_config={'thinking_level': 'low', 'max_output_tokens': 400}):
        d = ev.model_dump(mode='json', exclude_none=True)
        events.append(d)
        if d.get('event_type', d.get('type', '')).endswith('completed') or 'interaction' in d and d['interaction'].get('usage'):
            final = d
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'stream_events.json').write_text(json.dumps(events, indent=1))
    kinds = [e.get('event_type', e.get('type')) for e in events]
    usage = (final or {}).get('interaction', {}).get('usage', {}) if final else {}
    usd = gemini.record('smoke-stream', model, usage, note='stream')
    print(f'stream: {len(events)} events {sorted(set(map(str, kinds)))}; final usage {usage}; ${usd:.4f}')


def roundtrip(c, f):
    """Answer the get_frame call from the 'function' test with a still, sending the history back statelessly."""
    import base64
    decl = {'type': 'function', 'name': 'get_frame', 'description': 'Return a full-resolution still of the video at a time.',
            'parameters': {'type': 'object', 'properties': {'t_seconds': {'type': 'number'}}, 'required': ['t_seconds']}}
    png = base64.b64encode((gemini.HERE / 'clips' / 'smoke_still.png').read_bytes()).decode()
    for model in MODELS:
        prev = json.loads((OUT / f'function_{model}.json').read_text())
        call_step = next(s for s in prev['steps'] if s['type'] == 'function_call')
        history = [{'type': 'user_input', 'content': [video(f, 1), {'type': 'text', 'text':
                    'Call get_frame for t = 1.0 s so you can look closely at the birds.'}]}] + prev['steps'] + [
                   {'type': 'function_result', 'name': 'get_frame', 'call_id': call_step['id'], 'result': [
                       {'type': 'image', 'data': png, 'mime_type': 'image/png', 'resolution': 'ultra_high'},
                       {'type': 'text', 'text': 'Still at 1.0 s, 1920x1080.'}]}]
        it = call(c, 'roundtrip', model, {
            'input': history, 'tools': [{'type': 'google_search'}, decl],
            'generation_config': {'thinking_level': 'low', 'max_output_tokens': 1024}}, 2 * 280 + 2240 + 400, 1024, 1)
        if it:
            outs = [s for s in it.steps if s.type == 'model_output']
            print('   ', ''.join(getattr(b, 'text', '') or '' for b in (outs[-1].content if outs else []))[:300])


def agentic(c, f):
    """Agentic video (processing 'agentic', Flash only): which settings and tools it combines with."""
    model = MODELS[1]
    av = {'type': 'video', 'uri': f.uri, 'mime_type': 'video/mp4', 'processing': 'agentic'}
    ask = ('Pick one bird you can see clearly and measure its wingbeat frequency in beats per second. Say which '
           'moments you inspected, at what frame rate and resolution you loaded them, and how big the bird is in pixels.')
    gen = {'thinking_level': 'high', 'thinking_summaries': 'auto', 'max_output_tokens': 8192}
    decl = {'type': 'function', 'name': 'get_frame', 'description': 'Return a full-resolution still of the video at a time.',
            'parameters': {'type': 'object', 'properties': {'t_seconds': {'type': 'number'}}, 'required': ['t_seconds']}}
    call(c, 'agentic_plain', model, {'input': [av, {'type': 'text', 'text': ask}], 'generation_config': gen}, 20000, 8192)
    call(c, 'agentic_high', model, {'input': [{**av, 'resolution': 'high'}, {'type': 'text', 'text': ask}],
                                    'generation_config': gen}, 20000, 8192)
    call(c, 'agentic_search_schema', model, {
        'input': [av, {'type': 'text', 'text': 'Estimate how many birds are visible at 00:01 and guess the species. Search '
                       'the web for the typical wingbeat frequency of the European starling and give the source URL.'}],
        'tools': [{'type': 'google_search'}],
        'response_format': {'type': 'text', 'mime_type': 'application/json', 'schema': SCHEMA},
        'generation_config': gen}, 20000, 8192, 5)
    call(c, 'agentic_function', model, {
        'input': [av, {'type': 'text', 'text': 'Call get_frame for t = 1.0 s so you can look closely at the birds.'}],
        'tools': [{'type': 'google_search'}, decl], 'generation_config': gen}, 20000, 8192, 1)
    call(c, 'agentic_code', model, {
        'input': [av, {'type': 'text', 'text': ask + ' Use code execution for the arithmetic.'}],
        'tools': [{'type': 'code_execution'}], 'generation_config': gen}, 20000, 8192)


if __name__ == '__main__':
    c = gemini.client()
    f = upload(c)
    print('uploaded', f.name, f.mime_type, f.state, f'spent so far ${gemini.spent():.4f}')
    for what in sys.argv[1:]:
        globals()[what](c, f)
    print(f'ledger total ${gemini.spent():.4f}')
