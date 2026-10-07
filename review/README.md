# Murmuration video review (Gemini)

An agent watches a short clip and reports what it sees. A fixed policy turns those reports into two verdicts:
**S**, does it read as starlings, and **R**, could it pass as real footage. The model observes and the engine
decides. The engine is plain code, so the same observations always give the same verdict, and every verdict can be
traced to the clause and the moment in the clip it rests on.

| file | what it is |
|---|---|
| `policy.md` | the policy in prose: clauses S0-S5, R1-R6, gates G1-G4, decisions, and what is uncompilable |
| `ruleset.json` | the policy compiled by hand into rules; each rule cites its clause |
| `engine.py` | three-valued rule evaluation (after `~/Downloads/method-policy`), gates, per-axis decision, card |
| `schema.py` | the Pydantic `Extraction` the reviewer must return, and the JSON-schema subset sent to the API |
| `brief.md` | what the reviewer is told; identical for every clip |
| `harness.py` | one review: stage A watch (agentic video + search + `get_frame` stills), stage B measure (stills + code + search, schema) |
| `controls.json` | expected outcomes on real footage and deliberately broken renders, registered before any run |
| `controls_added.json` | stricter criteria added after the first runs (dated): real clips must approve, page variants must beat the base page, card values checked |
| `test_engine.py` | offline probes of the gates (no API calls): `uv run python test_engine.py` |
| `run_eval.py` | runs the controls, repeats, and reports pass/fail and agreement |
| `make_clip.py` | builds blind clips: 1280x720, real speed, 30 fps, no duplicated frames, opaque ids (`clips/key.json` holds the names) |
| `capture_page.js` | frame-exact capture of the page in Chrome (`?halt&warm=T`), posted to a local upload server |
| `FINDINGS.md` | what the runs showed, each contradicting claim checked against code or pixels |
| `gemini.py` | client, prices, budget caps ($2 a run, $25 in all) and the cost ledger `runs/ledger.jsonl` |
| `smoke.py` | the API probes that established what works (fps, tools with video, function round trip, agentic mode) |

## Running

```bash
cd review
uv run python harness.py CLIP_ID                       # agentic video on gemini-3.8-flash (default)
uv run python harness.py CLIP_ID --mode static --model gemini-3.1-pro-preview
uv run python run_eval.py --repeat 3                   # the controls, agentic Flash
uv run python run_eval.py --report [--mode static --model gemini-3.1-pro-preview --brief v0.1]
```

The key is read at run time from `$GEMINI_API_KEY`, or from gcloud (the project's "Generative Language API Key"),
and only ever sent in the `x-goog-api-key` header. Each run writes to `runs/<run id>/` the model's responses, the
stills it asked for, its notes, the validated extraction, the engine's result and a card. Since 2026-10-07 it also
writes each request (`callNN_<stage>_request.json`, inline images replaced by their hash) and records in `run.json`
the hashes of the clip, the stills and the source files (brief, policy, ruleset, engine, schema, harness) and the
stage-B prompt version. The uploaded video and the frames the agent loaded from it are referenced, not stored.
Reports re-score saved extractions with the current engine; they never pool runs made on different briefs or modes,
and flag a pool that mixes stage-B prompt versions.

## Video modes

- **Agentic** (`processing: "agentic"`; Gemini 3.8/3.7/3.6 Flash and 3.5 Flash-Lite only): the model moves through
  the clip itself, loading stretches at the frame rate and resolution it picks (`processing_call` /
  `processing_result` steps; loaded footage bills as tool-use tokens). This is the default and what the review is
  for. With `resolution: "high"` it loaded about 9x more than without.
- **Static** (every model, including 3.1 Pro): every frame at a fixed rate. Kept for comparison; see FINDINGS.md for
  how Pro and Flash did with it.

## What the API allows (measured in `smoke.py`, October 2026)

- Static: up to 24-30 fps sampled; about 264 tokens a frame at `high`.
- Agentic video with Google Search, with a custom function, and with a response schema: yes (one transient 500).
- Code execution next to video: refused in both modes (400). Stage B therefore works from stills.
- Code execution with images: works on both models; Flash has once stopped with "too many tool calls", and the
  harness then retries stage B without it.
- `generation_config.tool_choice: "none"` did not stop Flash calling get_frame; the harness refuses late calls
  instead.
