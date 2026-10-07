"""Gemini access for the review harness: key, client, prices and the spending ledger.

The key is read at run time, from $GEMINI_API_KEY or else from gcloud (the project's Gemini-only key), and is
kept in memory: it is never logged, printed or written. The Interactions client's automatic retries are turned
off, because a retried call is a second paid call that the ledger would not see.

Every call is recorded in runs/ledger.jsonl with its token usage and cost. A run is refused before it starts
if its worst-case cost would pass the per-run cap or take the total past the overall cap.
"""
import datetime as dt
import json
import os
import subprocess
from pathlib import Path

from google import genai
from google.genai._gaos.utils.retries import RetryConfig

HERE = Path(__file__).resolve().parent
RUNS = HERE / 'runs'
LEDGER = RUNS / 'ledger.jsonl'
PROJECT = 'gen-lang-client-0524741943'
KEY_ID = '80057b73-1044-461a-ac8e-4fbdbe481987'   # "Generative Language API Key": restricted to the Gemini API
CAP_RUN = 2.00                                     # USD, per run (all calls of one review)
CAP_TOTAL = 25.00                                  # USD, over all runs in the ledger

# USD per 1M tokens, from https://ai.google.dev/gemini-api/docs/pricing (read 2026-10-06). Output includes thinking.
# Each entry: (first day it applies, input, output, input above 200k-token prompts, output above 200k).
PRICES = {
    'gemini-3.8-flash': [('2026-09-02', .75, 3.75, .75, 3.75), ('2027-01-01', 1.50, 7.50, 1.50, 7.50)],
    'gemini-3.1-pro-preview': [('2026-01-01', 2.00, 12.00, 4.00, 18.00)],
}
SEARCH_USD = 14 / 1000                             # per Google Search query run by a Gemini 3 model (5000/month free; not counted)
TOKENS_PER_FRAME = {'low': 70, 'medium': 70, 'high': 280}   # video, per sampled frame (media-resolution page)
TOKENS_PER_IMAGE = {'low': 280, 'medium': 560, 'high': 1120, 'ultra_high': 2240}


def api_key() -> str:
    key = os.environ.get('GEMINI_API_KEY')
    if not key:
        key = subprocess.run(['gcloud', 'services', 'api-keys', 'get-key-string', KEY_ID, '--project', PROJECT,
                              '--format=value(keyString)'], capture_output=True, text=True, check=True).stdout.strip()
    if not key:
        raise RuntimeError('no Gemini API key: set GEMINI_API_KEY or log in with gcloud')
    return key


def client() -> genai.Client:
    c = genai.Client(api_key=api_key())
    c.interactions.sdk_configuration.retry_config = RetryConfig('none', None, False)
    return c


def price(model: str, prompt_tokens: int = 0, on: dt.date | None = None):
    rows = PRICES[model]
    day = (on or dt.date.today()).isoformat()
    row = [r for r in rows if r[0] <= day][-1]
    big = prompt_tokens > 200_000
    return (row[3], row[4]) if big else (row[1], row[2])


def usage_dict(usage) -> dict:
    if usage is None:
        return {}
    d = usage.model_dump(exclude_none=True) if hasattr(usage, 'model_dump') else dict(usage)
    return json.loads(json.dumps(d, default=str))


def cost(model: str, usage: dict) -> float:
    """USD for one call, from its usage. Thought and tool-use tokens are counted on top of the totals, so this
    errs high if the totals already include them."""
    tin = usage.get('total_input_tokens', 0) + usage.get('total_tool_use_tokens', 0)
    tout = usage.get('total_output_tokens', 0) + usage.get('total_thought_tokens', 0)
    pin, pout = price(model, usage.get('total_input_tokens', 0))
    searches = sum(g.get('count', 0) for g in usage.get('grounding_tool_count', []) or [] if 'search' in str(g.get('type', '')))
    return tin * pin / 1e6 + tout * pout / 1e6 + searches * SEARCH_USD


def bound(model: str, input_tokens: int, max_output_tokens: int, max_searches: int = 0) -> float:
    """Worst-case USD for one call: all of max_output_tokens spent, every search billed."""
    pin, pout = price(model, input_tokens)
    return input_tokens * pin / 1e6 + max_output_tokens * pout / 1e6 + max_searches * SEARCH_USD


def spent() -> float:
    if not LEDGER.exists():
        return 0.0
    return sum(json.loads(l)['usd'] for l in LEDGER.read_text().splitlines() if l.strip())


def check_budget(run_bound: float, run_spent: float = 0.0):
    if run_spent + run_bound > CAP_RUN:
        raise RuntimeError(f'run would cost up to ${run_spent + run_bound:.2f}, over the ${CAP_RUN:.2f} per-run cap')
    if spent() + run_bound > CAP_TOTAL:
        raise RuntimeError(f'total would reach ${spent() + run_bound:.2f}, over the ${CAP_TOTAL:.2f} cap')


def record(run_id: str, model: str, usage: dict, note: str = '') -> float:
    usd = cost(model, usage)
    RUNS.mkdir(exist_ok=True)
    with LEDGER.open('a') as f:
        f.write(json.dumps({'time': dt.datetime.now().isoformat(timespec='seconds'), 'run': run_id, 'model': model,
                            'usd': round(usd, 5), 'usage': usage, 'note': note}) + '\n')
    return usd
