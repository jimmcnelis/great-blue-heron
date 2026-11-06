# CHOREOGRAPHY INDEX — drawn-heron sequence set

Pass completed 2026-11-05. Method (Jimmy's Option 3 ruling, 14:08): the old Stage B
clips are **choreography, never footage** — each new drawn sequence inherits its
behavior's motion beats and real-life timings from the old clip + the movement
studies, then is drawn fresh: **HOME → behavior → HOME**, anchored on the locked
home frame (`gate1-strike/fresh/home_frame_approval.png`). Where a clip's timing
disagreed with the studies, **the studies won** and the disagreement is flagged in
each spec. No drawing was done in this pass.

Constants: playback always **12 fps**; storage = unique drawings × **~58 KB**
(measured, fresh strike build); every sequence starts AND ends on the exact home
frame; whole bird in frame at all times (no crop); durations vary per sequence.
Set as specced: **97.5 s** of authored sequences, **446 unique drawings** across
the eight (strike counted at its delivered 28).

## The set

| # | Sequence | Natural duration | Proposed | Ticks @12 | Unique drawings | Size | Confidence |
|---|---|---|---|---|---|---|---|
| 1 | **Strike** (separate rebuild, underway) | — | 5.0 s | 60 | 28 delivered | **1.63 MB actual** | delivered + gated; densification running (target ~47 drawings ≈ 2.7 MB) |
| 2 | [Listening](listening.md) — **REPLACES Miss (Jimmy, 2026-11-05)** | ~3 s up + 15 s hold + ~3 s down | ~21 s (pair) | ~72 + 180 hold | pose + grades TBD | small (hold = 1 frame) | design captured 2026-11-05; not drawn |
| 3 | [Stride](stride.md) | 7.0 s | 9.0 s | 108 | 29 | 1.68 MB | partial — return DECIDED 2026-11-05: honest two-turn return (~62 drawings / 3.60 MB) |
| 4 | [Flight](flight.md) | 9.0 s core (~10.0 w/ min. cruise) | 14.0 s | 168 | 106 | 6.15 MB | partial |
| 5 | [Preen](preen.md) | 10.0 s | 11.0 s | 132 | 96 | 5.57 MB | partial |
| 6 | [Stretch](stretch.md) | 7.0 s | 8.0 s | 96 | 73 | 4.23 MB | partial |
| 7 | ~~Courtship~~ **DROPPED by Jimmy 2026-11-05 14:22** (solves the budget; mostly authored + colony-behavior flag). Spec retained on disk for the record. | — | — | — | — | — | — |
| 8 | [Idle](idle.md) | 20.0 s (chart) | 25.0 s | 300 | 9 new (+ shared home) | 0.52 MB | partial |

Seven new sequences as specced: 24.24 MB (418 drawings). **After the courtship drop (Jimmy, 2026-11-05): six new sequences = 19.66 MB (339 drawings); set total with the strike = 21.29 MB delivered / ~22.4 MB densified, vs ~25.0 MB available — budget CLOSES with ~2.6-3.7 MB headroom.** **Stride return then DECIDED as honest turns (+1.92 MB over the backward-steps spec): six new = 21.58 MB; set = 23.21 MB delivered / ~24.28 MB densified vs ~25.0 MB — still closes, margin now ~0.7-1.8 MB.** The active set is SEVEN sequences: strike, listening, idle, stretch, stride, preen, flight. (Miss replaced by Listening, Jimmy 2026-11-05 23:30.)
Set total with strike as delivered: **25.87 MB**. With strike densified (≈2.7 MB): **≈26.9 MB**.
(The home drawing is shared by all sequences and stored once at integration;
per-sequence counts above include it where the worker counted it — a few × 58 KB
of slack in the set's favor, immaterial against the overage below.)

## ⚠ BUDGET — the set as specced runs OVER

Budget frame: ~28 MB repartitioned app partition (approved 2026-11-05 13:06).
Program: 0.64 MB code (measured) + speech reserve ≈ 2.36 MB → program envelope
≈ 3.0 MB, leaving a **sequence remainder of ≈ 25.0 MB**.

- Set as specced: 25.87 MB of sequences → **over the remainder by ≈ 0.9 MB**
  (device total ≈ 28.9 MB vs the 28 MB partition).
- Once the strike densifies (≈2.7 MB): **over by ≈ 1.9 MB** (device ≈ 29.9 MB).

**What causes it — four sequences are 85% of the new subtotal:**
flight 6.15 MB (14.0 s, motion-dense throughout), preen 5.57 MB (11.0 s),
courtship 4.58 MB (20.5 s), stretch 4.23 MB (8.0 s). Miss, stride, and idle
together cost only 3.71 MB.

**Levers, priced:**
- **Defer or drop courtship: −4.58 MB.** Solves the overage alone, with room to
  spare — and it is independently the weakest spec (mostly authored) with a
  behavior-source recommendation against it (below).
- Trim flight's cruise: each wingbeat ≈ 6 ticks ≈ 6 drawings ≈ **0.35 MB**.
- Return preen to the chart's 10.0 s from the proposed 11.0 s: ≈ **−0.5 MB**.
- Choosing stride's canonical turn return (option a) **adds ≈ +1.92 MB**
  (3.60 vs 1.68 MB) — if that option is picked, courtship's room is needed.

## Proposed production order

Strike is #1 and underway. For the rest — cheap and chart-strong first, the
long and the authored last, open decisions gated before their sequence starts:

2. **Miss** — 1.51 MB. Reuses the strike's chain, keys logic, and production
   template while they are hot; its chart is the strike chart's twin. The
   fastest proof that the choreography-spec → drawn-sequence pipeline works.
3. **Idle** — 0.52 MB, 9 drawings. Gives the player its living still early and
   proves the hold/event machinery every other sequence's timing table uses.
4. **Stretch** — 4.23 MB. Chart-complete choreography, single spot, one long
   true hold — a clean mid-size production.
5. **Stride** — 1.68 MB as specced, but **gated on Jimmy's return decision**
   (below) before any drawing starts.
6. **Preen** — 5.57 MB, 96 drawings. The long pose-to-pose haul; benefits from
   a practiced pipeline.
7. **Flight** — 6.15 MB, 106 drawings. Biggest and most complex; its airborne
   section is chart-authored (the clip crops the bird out of frame f56–79), so
   it wants the drawing crew at its fastest.
8. **Courtship** — LAST and conditional (see flags). Do not produce until
   Jimmy rules keep / defer / drop.

## Open decisions for Jimmy

1. **Budget overage ≈ 0.9 MB now, ≈ 1.9 MB after the strike densifies.**
   Recommended lever: defer/drop courtship (−4.58 MB). Alternatives priced above.
2. **Stride's return.** As specced: two authored **backward steps** — cheap
   (29 drawings total) but flagged by the spec itself as *not canonical heron
   behavior* (a design fiction, contained to 2 steps). The canonical
   alternative — walk out, turn, walk back, turn again (a single turn strands
   the bird facing left at home) — costs ≈ 62 drawings ≈ 3.60 MB and ~15 s,
   and requires the drawn-yaw-stop machinery no other sequence needs.
   Walking back facing left with no turn is a forbidden flip (study §8).
3. **Courtship: keep, defer, or drop?** The behavior deep-dive (§1.7) grades
   the Stretch Display a **colony / nest-site behavior** and recommends
   excluding plume-erection display from the solo creek roster ("plume
   erection displays belong to the colony, not the creek"). The spec is an
   authored solo echo of it: the clip itself contains no plume erection and
   no bill-snapping — both signature beats had to be authored. If kept, the
   spec recommends scheduling it rare / season-weighted.

## Cross-cutting findings

- **Every worker graded "partial" — none of the seven is a clean measure.**
  In every case the beat timings are measured and/or charted, but every
  departure/return is at least partly authored, because no old clip starts
  or ends on the home frame (they open on an upright alert bird) and four
  clips end mid-behavior (stride, flight, stretch, courtship — as flagged
  when the pass was ordered).
- **The studies won every clip conflict.** Headline rejections: the miss
  clip's slow decelerating descent, 41-frame head-down dwell, and second
  splash (splash belongs at contact only); the stride clip's head surfing
  ~1:1 with the body (no translational-saccade head-lock) and its
  freeze-less 1.4–2.4 s steps; the flight clip's permanently bent dangling
  legs (never trailing straight) and centre-frame landing with no water;
  the stretch clip turning out to be a both-wings **warble**, not the
  canonical same-side stretch — and containing no leg extension at all;
  the preen clip's single continuous sweep vs the chart's bout-and-pause
  structure (its draw-through and whole-body shake are absent entirely);
  the idle clip's continuous-breathing model, rejected with measurements
  (held fraction ≈ 0.24 vs the ≥ 0.92 gate; sway period ≈ 5–6 s; the clip
  doesn't even loop).
- **A recurring authored beat:** the study charts end at the idle base pose
  (neck_coil 0.85); every spec therefore closes with an authored settle from
  the hunting coil onto the exact deep home coil. Consistent across the set.
- **Agreements worth keeping:** the flight clip's first downstroke begins
  with the feet planted (liftoff ~f53–54) and its flare/fold/momentum-step
  landing shape matches the chart — the clip is a sound reference at its
  two ends even though its middle is unusable.
- **Idle sits exactly on the study's held-fraction gate** (276/300 ticks
  held = 0.92). No event may be added to idle without lengthening it.
- **Flight is the only sequence that leaves the waterline band**; stride is
  the only one whose horizontal displacement is content rather than error.

## Files

- [miss.md](miss.md) · [stride.md](stride.md) · [flight.md](flight.md) ·
  [preen.md](preen.md) · [stretch.md](stretch.md) · [courtship.md](courtship.md) ·
  [idle.md](idle.md) — per-sequence beat sheets, natural durations, key poses,
  departure/return choreography, size arithmetic, provenance (source MP4,
  clip bytes + md5, conversion route), study-vs-clip rulings, confidence.
- Sequence 1 (strike) is specified by its own rebuild in
  `gate1-strike/fresh/` (28 unique drawings / 60 ticks / 5.0 s / 1.63 MB
  delivered; densification to ~47 drawings in progress).
