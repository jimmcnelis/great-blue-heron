# WINGBEAT CALIBRATION — real-time cadence → slow-motion correction factor

Pass date: 2026-11-04. Purpose: close the one open measurement in
`ADDENDUM_REPORT.md` §4.1 / §6 — absolute GBH wingbeat frequency — and use it to
convert the Boga slow-motion renders' timings from render-seconds to estimated
real seconds. Method per Jimmy's ruling (2026-11-04 09:32): cadence is a
frequency measurement; the three real-time records set the true rate, and the
renders are corrected against it. All clips from
`~/workspace/heron/reference-footage/`. Working files (scripts, signals, strips,
validation overlays): `work/wingbeat/`.

## 1. Per-clip results

Two routes per clip, reconciled: (a) **signal** — the bird is held in an
anchor-interpolated crop (anchor positions read off probe/validation frames I
viewed), and the dark-silhouette signals (dark-pixel fraction, silhouette area,
bbox height/width) are FFT'd and peak-counted; (b) **eye** — dense every-frame
strips of those crops, cycles counted against the frame clock. Strips viewed
before filing: `work/wingbeat/{astroA,teagueA,shortsA}_strip.jpg`.

| Clip | Content (verified by viewing) | Window | Signal route | Eye route | Adopted |
|---|---|---|---|---|---|
| fb-astroland-winter-flight (29.82 fps) | GBH in steady flight toward/past camera, clean sky | t 15.5–18.5 s (~8 cycles) | FFT 2.65 Hz (dark/area/bh); peak-count 2.71–2.98 | clear full cycles, ≈2.5–2.7 Hz | **2.7 ± 0.2 Hz — cruise** |
| fb-teague-moment (30 fps) | GBH standing in a pond, takes off at ~30 s and climbs away from camera | t 30.3–33.0 s | FFT 2.69–3.13 Hz (dark/bw); peak-count 2.73–3.0 | full cycles at ~11-frame spacing in strip rows 1–6, ≈2.7–2.9 Hz | **2.85 ± 0.2 Hz — takeoff/early flight** |
| yt-shorts-EgEaJ4VkduE (29.97 fps) | **NOT a GBH** — white plumage, black primaries, neck flown extended (pelican-like); low descent to a lake surface | — | (bh peak spacing ~2.9 Hz, for the record) | species call made from the strip | **EXCLUDED from GBH pooling** |

Notes on the two GBH clips: they agree within 0.15 Hz despite different birds,
cameras, and flight phases — and the ordering is the biologically expected one
(takeoff beats a little faster than cruise). The Shorts bird is excluded on
species grounds, not convenience: a GBH cruises with the neck folded and is
blue-grey; this bird is white with black flight feathers and a straight neck.

**Method honesty:** a first pass with a greedy dark-blob tracker produced
plausible-looking numbers that validation overlays (`work/wingbeat/val_*.jpg`)
showed to be false — it locked onto the treeline in the Shorts, lost the Teague
bird at liftoff, and lost the Astroland bird after ~1.3 s. Those numbers were
discarded in full. Every figure above comes from crops whose contents I viewed
frame-by-frame in the dense strips.

## 2. Pooled real-time cadence

- **Cruise wingbeat: 2.7 ± 0.2 Hz** (cycle ≈ 0.37 s) — Astroland, n = 1 clip, ~8 cycles.
- **Takeoff wingbeat: 2.85 ± 0.2 Hz** — Teague, n = 1 clip, ~7 cycles.
- Working pooled statement: GBH flapping flight runs **≈2.6–2.9 Hz**, phase-dependent.

## 3. Calibration factor for the Boga renders

Addendum §4.1 measured the render-domain cycle in fb-boga-long-flight at
2.2–2.4 s (0.417–0.455 Hz, central 0.435 Hz). That clip is cruise flight, so it
calibrates against the cruise rate:

**Factor = 2.7 / 0.435 ≈ 6.2×** (extremes: 2.5/0.455 ≈ 5.5 to 2.9/0.417 ≈ 7.0).

Hypothesis checks:
- **120 fps → 24 fps = 5.0×: REJECTED.** It predicts a true cadence of
  5 × 0.435 ≈ 2.17 Hz, outside the measured 2.5–2.9 Hz — and the Boga files
  are in fact 29.97 fps renders, not 24.
- 120 fps → 29.97 fps = 4.0×: also rejected (predicts 1.74 Hz).
- **6.0× (e.g., 180 fps capture conformed to ~30 fps): FITS** — predicts
  2.61 Hz, inside the measured cruise range.

**Adopted conversion factor: ÷6.0**, with the measured range ÷5.5–7.0 carried
as the error band on every converted figure below.

## 4. Correction table — Boga render-seconds → estimated real seconds

Applies ONLY to the Boga set (fb-boga-*), under the stated assumption in §5.

| Item | Render-domain | Real (÷6.0) | Band (÷5.5–7.0) | Confidence |
|---|---|---|---|---|
| Long-flight wingbeat cycle | 2.2–2.4 s | **0.37–0.40 s (2.5–2.7 Hz)** | — | anchor |
| Stump-sunset landing balance phase (fb-boga-stump-sunset) | 35–39 s | **5.8–6.5 s** | 5.0–7.1 s | medium-high (sanity-checked, §5) |
| Flyby legs-down → contact (fb-boga-flyby-landing, render t ≈98→103 s) | ~5 s | **~0.8 s** | 0.7–0.9 s | medium — steep branch approach; NOT comparable to marksmith's shallow water glide (native 5.5 s legs-down→contact) |
| Tree-stretch wing-spread hold (fb-boga-tree-stretch) | ~3.0 s | **~0.50 s** | 0.43–0.55 s | medium |
| Tree-stretch fold after the hold | ~1.2 s | **~0.20 s** | 0.17–0.22 s | medium |

**NOT converted — Samrino pipeline (fb-samrino-*):** graceful-awkward balance
phase (9–10 render-s), its fold completion (~32 render-s), and the
fishing/swallow render timings keep their render-domain values. The Boga
factor must not be applied to them: different shooter, different pipeline
(24 fps renders of stated-120P sources — their by-construction factor would be
5.0× *if* that provenance holds, which is unverified; no Samrino conversion is
published here).

## 5. Assumptions and sanity check

- The factor is measured on ONE Boga clip (long-flight). Applying it across
  the Boga set assumes the photographer captured and conformed the whole set
  the same way — plausible for one shooter's series, unverified per clip.
  Every converted number is therefore a **calibrated estimate**, not a
  measurement.
- Sanity check against native-rate analogues: the converted stump-sunset
  balance phase (5.8–6.5 s real) sits between the two native brackets —
  marksmith's ~10 s of wing-assisted running on water and weber's ~2.5 s
  wings-up on a firm perch — and a snag-top landing needing several seconds of
  asymmetric correction is consistent with the addendum's phase structure.
  No contradiction.
- The stretch, converted, is a brief ~0.5 s symmetric wing-spread flash after
  landing — short, but the same order as the native-measured takeoff neck-fold
  (0.4–0.5 s, weber-duty), so not implausible.

## 6. Updated canon statement (replaces §4.1's UNRESOLVED)

**Wingbeat (GBH): cruise ≈2.7 ± 0.2 Hz (cycle ≈0.37 s), takeoff ≈2.85 ± 0.2 Hz
— RESOLVED by real-time calibration, 2026-11-04. The Boga slow-motion renders
run ≈6× slow (factor 6.0 adopted, measured range 5.5–7.0); their render-domain
timings convert to estimated real seconds by ÷6. The Samrino renders are a
separate pipeline and remain unconverted.**

Files: `work/wingbeat/track.py`, `ncc_track.py`, `anchor.py`, `eye_strip.py`,
`validate.py`, `*_sig.npz`, `*_strip.jpg`, `val_*.jpg`, `wingbeat_results.csv`.
