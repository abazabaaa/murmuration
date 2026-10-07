"""What the reviewer may report: typed observations, validated with Pydantic on our side.

`Extraction` is the final answer of a review. Each judged clause of policy.md is an `Obs` whose `holds` says
whether the clause's requirement is met (True = fine, False = the fault is present, None = cannot be judged).
The engine reads these; the reviewer never states a verdict.

`api_schema()` turns a model's JSON schema into the subset the Interactions API documents (types, properties,
required, enum, items, anyOf, $defs/$ref, description, min/max), dropping the rest. The full constraints are
enforced locally with `model_validate_json`.
"""
from typing import Literal

from pydantic import BaseModel, Field

Confidence = Literal['low', 'medium', 'high']
TS = 'Moments in the clip as MM:SS.s, or MM:SS.ss for consecutive frames, e.g. "00:01.5".'


class Obs(BaseModel):
    holds: bool | None = Field(description='True if the clause is satisfied, False if its fault is present, null if it cannot be judged from this clip.')
    timestamps: list[str] | None = Field(description=TS)
    still_ids: list[str] | None = Field(description='Ids of get_frame stills (e.g. "s3") this judgement rests on; null if none.')
    evidence: str = Field(description='What was seen, concretely, in one to three sentences.')
    confidence: Confidence


class Artefact(BaseModel):
    kind: Literal['ghosting', 'popping', 'flicker', 'hard_edges', 'aliasing', 'duplicates', 'wrong_occlusion', 'compression', 'other']
    timestamps: list[str] = Field(description=TS)
    description: str


class Extraction(BaseModel):
    birds_resolved: bool | None = Field(description='Can individual birds\' outlines (wings, body, tail) be made out in stills? (policy S0)')
    bird_span_px_median: float | None = Field(description='Median wingtip-to-wingtip length of resolved birds, in pixels of the 1280x720 frame, measured from stills.')
    birds_visible_estimate: int | None = Field(description='Rough number of birds visible in a typical frame.')
    predator_visible: bool | None = Field(description='Is a raptor visible at any point?')
    wingbeat_hz: float | None = Field(description='Typical wingbeats per second, or null if it cannot be measured.')
    wingbeat_timestamps: list[str] | None = Field(description='Moments used to measure the wingbeat rate. ' + TS)
    s1_silhouette: Obs = Field(description='S1: resolved birds have the starling outline.')
    s2_flight_mode: Obs = Field(description='S2: rapid flapping in bursts with short glides or bounds; not rigid, not in unison, not slow and deep.')
    s3_flock_motion: Obs = Field(description='S3: the flock moves coherently and fluidly; no jitter, jumps, pass-throughs or independent movers.')
    s4_attitude_variety: Obs = Field(description='S4: resolved birds show varied attitudes; not identical copies.')
    s5_predator: Obs | None = Field(description='S5: the predator looks and behaves like a peregrine and the flock reacts. Null if no predator is visible.')
    waves_seen: bool | None = Field(description='Are there bands of darker or lighter birds travelling through the flock?')
    wave_pulses: int | None = Field(description='How many such pulses, if any.')
    r1_scale: Obs = Field(description='R1: birds\' apparent size is consistent with distance and the scene.')
    r2_tone: Obs = Field(description='R2: birds are near-black or dark grey silhouettes fitting the light; no colour casts, no see-through birds.')
    r3_numbers: Obs = Field(description='R3: the flock is large and dense enough for a murmuration.')
    r4_artefacts: Obs = Field(description='R4: no birds leave copies or trails, pop in or out, flicker or have stair-stepped edges; neighbours are not identical; nothing is wrongly in front.')
    artefacts: list[Artefact] | None = Field(description='Each artefact seen, or null if none.')
    r5_camera: Obs = Field(description='R5: the image shows some noise or grain, compression, motion blur on fast wings or softness, and exposure suited to the scene.')
    r6_scene: Obs = Field(description='R6: sky, light, horizon and haze agree, and the birds are lit by the same light at a plausible height and distance.')
    notes: str = Field(description='Anything else a reviewer of this clip should know, in a few sentences.')
    contradictions: list[str] | None = Field(default=None, description='Each place where a measurement you made in this '
                                             'step contradicts your notes: what the notes said, what you measured, and '
                                             'which you kept. Null if none.')


class Notes(BaseModel):
    """First stage: what was watched and which stills were inspected, before measuring."""
    observations: list[str] = Field(description='Concrete observations, each starting with its MM:SS.s timestamp.')
    stills_inspected: list[str] | None = Field(description='Ids of the get_frame stills you looked at.')
    open_questions: str | None = Field(description='What still needs measuring or checking in the stills.')


_KEEP = {'type', 'properties', 'required', 'enum', 'items', 'anyOf', '$defs', '$ref', 'description',
         'minimum', 'maximum', 'minItems', 'maxItems', 'format', 'additionalProperties', 'prefixItems'}


def api_schema(model: type[BaseModel]) -> dict:
    def clean(node):
        if isinstance(node, dict):
            out = {}
            for k, v in node.items():
                if k == 'const':                       # Literal with one value: express as an enum
                    out['enum'] = [v]
                elif k in ('properties', '$defs'):
                    out[k] = {name: clean(sub) for name, sub in v.items()}
                elif k in _KEEP:
                    out[k] = clean(v)
            return out
        if isinstance(node, list):
            return [clean(x) for x in node]
        return node
    return clean(model.model_json_schema())
