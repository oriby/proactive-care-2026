# Heat–Medication Risk Graph — Demo

A precomputed, sourced knowledge graph (medications → mechanisms → outcomes, plus
comorbidities and today's heat/pollen conditions) with a deterministic traversal engine.
Paste a free-text patient intake, it detects and highlights keywords, traverses the graph,
scores the heat outcome as a percentage (the Heat Vulnerability Score), and shows a short
summary with a recommended monitoring workflow — outside the graph, never fed back into scoring.

## Quick start

Just open `index.html` in a browser — no server needed. The intake box is pre-filled with an
example under a bold **MEDICAL DETAILS** title (edit or replace the text directly). Press
**Parse & run** and, step by step: the recognized keywords are highlighted in the text, the graph lights up (start nodes first, then the edges draw in
toward the mechanisms and the outcomes, each node lighting as its edge arrives), the Heat
Vulnerability Score counts up, and the summary panel shows a spinner ("Generating summary…")
before the summary appears. The summary is **templated locally** from the parsed intake (no
model is called). Set `prefers-reduced-motion` in your OS to skip the animation.

`server.py` (a small Flask proxy to the Anthropic API) is no longer used by the page. It is
left in place in case you want to wire a real model back in: the page would POST a bare
prompt plus the retrieved facts as a separate `context` field to `/api/summarize`.

## How the graph works

- **Nodes** (`NODES` in `index.html`): five categories — medication, comorbidity, climate
  (heat/pollen/duration), mechanism, outcome. Every non-outcome node carries a `source`
  field (CDC, Lancet, CDC SVI) so every flag traces back to something real.
- **Edges** (`EDGES`): weighted, directed, mostly static risk weights. A few (age,
  current heat level, pollen level, multi-day exposure) resolve dynamically in
  `effectiveWeight()` based on the parsed intake.
- **Traversal** (`runTraversal`): plain BFS, two hops — `medication/comorbidity → mechanism
  → outcome`, plus direct `comorbidity/heat/pollen → outcome` edges. No embeddings, no
  similarity search — exact graph reachability, so every flag is auditable.
- **Scoring** (additive points → sigmoid percentage): for each outcome, every *distinct* edge
  on the paths leading to it — including the medication/comorbidity → mechanism edges upstream
  of it — contributes `(weight − 1) × 15` points (like Charlson / CHA₂DS₂-VASc). The summed
  points are then mapped to a 0–100% risk index with a logistic curve,
  `100 / (1 + e^(−0.08 · (points − 50)))` — 50 points = 50%, flattening toward 0% and 100% so
  complex patients stay distinguishable. Tune `POINTS_PER_WEIGHT`, `SIGMOID_MIDPOINT` and
  `SIGMOID_STEEPNESS` in `index.html`. The weights are hand-assigned, clinically-informed
  judgment calls, **not** statistically calibrated, so the percentage is a relative risk
  index, not a probability — say so when presenting it.
- **Threshold**: the "Heat Vulnerability Score" card flags the patient when the Heat-risk
  percentage exceeds `FLAG_THRESHOLD` (70%, a constant in `index.html`).
- **Intake highlighting**: when you press Parse, the keywords the parser recognized
  (medications, comorbidities, age 65+, heat-forecast terms) are highlighted in the intake text in
  their node-category colors (a mirrored backdrop behind the textarea paints them). Editing the text
  clears the highlights (their positions would be stale). The text is displayed in lowercase (CSS
  `text-transform`) for readability; parsing is case-insensitive either way. Keep the `FORECAST`
  line: it separates the medical details from the forecast for the parser.
- **Layout and edge routing**: columns run left to right in `COLUMNS` order — Comorbidities,
  Medications, Mechanisms, Risk outcome, Climate. Each edge is classified by *column skip*
  (difference of its endpoints' column indices). Skip 1 (adjacent columns) is one simple
  bezier. Skip ≥ 2 is routed through a **bus lane** reserved above all columns as three cubic
  segments (up-and-out, across, down-and-in), so it never passes through a node of an
  intermediate column; these edges are drawn dashed and lighter. `NODES`/`EDGES` are not
  affected — this is purely visual. Track spacing and lane constants (`LANE_*`) sit above
  `drawAllEdgesBase()`; the `.graph-wrap` padding-top must clear the lowest track.
- **Node summaries**: clicking a graph node shows a 2–3 line summary with inline `[ref link]`
  citations under the graph. In this demo every `[ref link]` — and both entries in the summary's
  REFERENCE list — points at the single `PLACEHOLDER_REF_URL` (a CDC cardiovascular-disease page).
  Replace it with real per-node sources before any real use.

## Extending it

- Add a medication or comorbidity: add an entry to `NODES`, its dictionary aliases in
  `MED_DICT`/`COMO_DICT`, and its edges in `EDGES` with a real source.
- Swap keyword matching for something smarter: `parseIntake()` and `matchDict()` are the
  only two functions that touch raw text — everything downstream just consumes the
  `parsed` object they return.
- Wire a real heat/pollen feed: replace the fixed `DEFAULT_POLLEN_KEY` and the regex-based
  `heatKey`/`consecutiveDays` detection with calls to NWS HeatRisk
  (`mapservices.weather.noaa.gov/experimental/rest/services/NWS_HeatRisk/ImageServer`) and
  an AirNow/pollen API.

## What this intentionally does not do

No diagnosis, no dosing guidance, no automated messaging to patients or caregivers. Every
score is a flag for a clinician to review, not a clinical decision — the summary's workflow
ends with contacting the nurse/pharmacist/clinician per facility protocol.
