# Heron v1.1 → BOX-3 Port — FEASIBILITY REPORT (flash NOT yet done)

**Status: feasibility complete; flash is GATED.** The only viable architecture
is a distilled student decoder, which changes what "v1.1 on device" means —
per the port brief, that gets reported before anything is flashed. The candle
BOX-3 (MAC 7c:2c:67:99:f8:38) still runs the Jimmy portrait v2.1, untouched.
Portrait and Skunkflame v2 projects are intact on the Studio.

## The shipped build being ported

- Teacher = **model11f** (fine-tuned model11; the wrap-up's shipped render).
  Spark `~/heron/preview_heron_v1_1.mp4` md5 `5857d92ff02e2089a447dbb81d977767`;
  val (argmax, full res): cell 99.77% / **bird 99.59%** / fish 92.69%.
  (The preview copy on this VM, md5 c0e05f51…, is the earlier base-model
  render — superseded on the Spark by the 11f render at 20:33 UTC.)
- The 800×480 preview is a nearest-neighbor resize of the master grids,
  **not** a native render (the native variant model died mid-training and
  was not relaunched) — it is not cited anywhere in this report.

## Why the shipped decoder cannot go on the device (measured, not guessed)

Teacher decoder (from_lat + dec0 + dec_blocks + head of the 18.75M-param AE):

| | Teacher decoder | BOX-3 budget |
|---|---|---|
| Params | **9,644,556** | — |
| int8 weights | **9.64 MB** | app0 = **6,553,600 B** (default_16MB.csv) |
| Compute | **3.63 GMAC/frame** | portrait decoder ≈ 81 MMAC took 1,421 ms decode+paint |

It fails twice: the weights alone exceed the app partition by ~3.1 MB, and
at the portrait's measured on-device throughput the decode would take
roughly **25–65 s per frame**. No quantization trick fixes either number.
Live decode of the shipped AE is unworkable — full stop.

## Chosen architecture (fallback a + b from the brief, combined)

1. **Latent-trajectory playback (b):** the device carries the shipped
   episode's latent track — 2,024 frames × 128 dims, int8 ≈ **259 KB** —
   regenerated from model11f latents + the shipped sim's segment list
   (`episode_log_11.json`, regenerated 20:33 UTC with the 11f render).
   Same playback pattern as the portrait's rest-path tables.
2. **Distilled student decoder (a):** a small decoder trained on the Spark
   to map model11f latents → palette grids, at **half resolution**
   (120×160), upscaled 2× nearest on device to the native 320×240 panel.
   - 1,260,580 params → **1.26 MB int8**; **76.8 MMAC/frame**
   - Architecture: dense 128→32×15×20, then 3 nearest-upsample conv stages
     (32→24→16→16) + 1×1 head to 12 palette classes; GELU; argmax snap
     (the teacher's snap mode).
   - Trained on all 43,936 corpus latents against ground-truth grids
     downscaled 2×2 majority; second pass added oversampling of the motion
     kinds (strike/walk/takeoff/flyin/turn) that the first pass smeared.
3. **Ink layer procedural in C**, from the episode's event table
   (step/splash/drips entries in `episode_log_11.json`), same InkSim rules
   as the sim. Presence beats (APPROACH at frame 1533, SUSTAINED after) are
   the sim's scripted ones — **simulated; this unit has no sensor.**
4. Display: BSP init + sprite pipeline from `~/portrait-fw/`; no radios
   initialized, ever. Estimated firmware ≈ **2.0 MB** (weights 1.26 +
   latents 0.26 + code/display ~0.45) — ~31% of app0, same as the portrait.
   Student feature buffers (largest map 120×160×16 int8 ≈ 300 KB) go to
   PSRAM, as the portrait build already does for its large tensors.

## Fidelity (held-out val clips, half-res targets unless noted)

| Decoder | Cell | Bird | Fish |
|---|---|---|---|
| Teacher model11f, full res 240×320 | 99.77% | 99.59% | 92.69% |
| Teacher model11f, downscaled to 120×160 (the ceiling) | 99.77% | 99.59% | 92.90% |
| Student **f2**, float | 99.20% | **99.01%** | 88.75% |
| Student **f2**, int8-weights fake-quant | 99.17% | 98.98% | 88.39% |
| Student f (first pass), float — superseded | 99.09% | 98.87% | 88.88% |

The student sits 0.6 pt of bird accuracy under the half-res ceiling.
Int8 weight quantization costs ~0.03 pt — negligible. Full device-exact
activation requantization has **not** been simulated yet (the portrait's
device-exact gap was small: MSE 0.00091 vs 0.00073 float); it is a
flash-phase verification step, not an assumption.

**Visual gate (frames pulled and read, GT left / student right —
`student11f2_visual_check.png`):** idle, strike-with-fish, and stretch
frames are faithful — diagonal stance, stilt legs, fish in beak all read
cleanly. Known student defects, honestly: the **walk stepping-leg frame
still bunches into a brown mass** (the v1.1 rig's own weak spot, worse at
half res — more training did not fix it; it is a capacity/resolution
limit), flight frames carry a few stray speckle cells, and the head/plume
renders slightly heavier black than the teacher. The episode spends most
of its 2,024 frames in the idle/standing poses the student gets right.

## On-device rate estimate (NOT yet measured — no flash has happened)

Portrait calibration: ~81 MMAC decoder + paint = 1,421 ms/frame measured.
Student: 76.8 MMAC decode + a larger sprite push (320×240). Estimate
**1.2–1.8 s/frame all-in → ~0.55–0.85 fps**, the same class as the
portrait's measured 0.70 fps that Jimmy judged "working great."

What that does to the loop — a playback decision for the gate:

| Stride | Paints/loop | Loop length | Authored motion step |
|---|---|---|---|
| 1 (every latent) | 2,024 | ~50 min | 1/24 s — strikes take ~10 s to fire; too slow to read |
| **6 (recommended)** | 337 | **~8 min** | 0.25 s — beats read, idles unaffected (near-static) |
| 8 | 253 | ~6 min | 0.33 s — choppier |

This is a generated sim loop (latent trajectories + procedural ink), not
a video file and not a frame store — but it is **not** the full 24 fps
sim either. That is the honest meaning of "v1.1 on this device."

## If approved, the flash phase is

1. New Studio project `~/heron-fw/` cloned from `~/portrait-fw/`
   (platformio.ini identical: esp32s3box, default_16MB.csv,
   upload_port /dev/cu.usbmodem83401 — device confirmed present).
2. Export student f2 weights int8 (per-channel, portrait export recipe) +
   episode latent pack + event table as C headers; weights-checksum
   banner like the portrait's.
3. Flash, then verify: banner, weights checksum in flash, heap over
   ~10 min, zero panics, **measured** paint rate + realized loop period —
   reported back before the port is called done.

**Reflash path back:** `cd ~/portrait-fw && pio run -t upload` restores
the portrait exactly (its firmware is untouched on disk); Skunkflame v2
is `~/skunkflame-fw-v2/`, same command. The sealed spare stays sealed.

## Artifacts

- Spark `~/heron/port11/`: `distill.py` (training script),
  `student11f.pt` / `student11f2.pt` + stats JSONs, `distill_f.log` /
  `distill_f2.log`, `targets_half.npy`, visual-check sheets.
- This VM: `student11f_visual_check.png`, `student11f2_visual_check.png`
  (beside this report in `~/workspace/heron/`).
- One process note: the first f2 training attempt died silently after
  epoch 5 (no traceback; likely killed under GPU contention on the
  Spark). The retry under `setsid` completed cleanly; its numbers are
  the ones above.
