# STORAGE BUDGET — drawn heron animations on the ESP32-P4 (measured 2026-11-05)
Device: 32 MB flash. Current Stage A layout: factory app partition 20 MB (partitions.csv).
Program allowance (MJPEG player app, Stage A class): ~3 MB.

Measured per-frame cost at 1024x600 (JPEG/MJPEG):
- Stage B painted clips (shelved): 54–60 KB/frame, 120 frames each ≈ 6.5–7.2 MB/clip → 8 clips = 54 MB (the old overflow)
- Pencil strike from video-gen, raw transcode 12 fps q5: 62 KB/frame; denoised q7: 51 KB/frame
- Canonical pencil still, q7: 62 KB (paper grain is the byte cost)

Scenarios for 8 animations (~6 s each) + program:
- Video-gen route, 12 fps full frames: 70 fr × ~51 KB ≈ 3.5 MB/clip → 28 MB + 3 MB program = ~31 MB — DOES NOT CLOSE (20 MB partition; even repartitioned ~31 MB leaves no headroom)
- Drawn-frames route (animator's economy: holds are ONE frame; strike ≈ 30 unique frames): ~30 × 51 KB ≈ 1.5 MB/clip → 12 MB + 3 MB = ~15 MB — CLOSES inside the existing 20 MB partition with ~5 MB headroom
Optional levers: flatter paper finish (~30 KB/frame), 10 fps for slow behaviors, repartition toward ~28 MB.

VERDICT: the budget closes under the drawn-frames pipeline; it does not close under video-gen. Same conclusion as the framing evidence (video-gen failed the wide framing twice: rubber neck/drift, then invented marsh scenery).

## Worked example (2026-11-05 13:01, Jimmy's question)
Per-drawing cost ~45 KB (measured across 3 assemblies). 2.5 MB cap per sequence (~55 drawings max).
- 24 poses/sequence: ~1.08 MB each -> x8 = 8.6 MB + plate ~0.05 MB + program ~3 MB = ~11.7 MB of the 20 MB partition. FITS, no repartition, each sequence under half its cap.
- 36 poses/sequence: ~1.6 MB each -> ~16 MB total. Still fits.
- 55 poses (at cap) x8: 23 MB total — the only tier that breaks the current partition.
Smoothness is no longer storage-bound; it is production-bound (each pose = one gated drawing). Going 12 -> 24 poses = one more breakdown round: a halfway frame in every gap of the existing chain.

## MEASURED program size (2026-11-05 13:25, Jimmy: "yes measure")
Stage A binary on the Studio (~/heron-living-loop/build/heron_living_loop.bin, built 2026-11-04 19:20): 11,556,688 B total. Embedded assets inside it: idle1.mjpeg 8,674,418 + idle2.mjpeg 1,011,709 + alert plate RGB565 (1024x600x2) 1,228,800 = 10,914,927 B. => PROGRAM CODE ALONE = 641,761 B ≈ 0.64 MB (LVGL + BSP incl. touch driver + JPEG decode + player). The earlier "~3 MB program" estimate was ~5x too fat; 3 MB now stands as the WORST case including speech.
Revised all-in estimate: code 0.64 + speech models ~1-2 MB (estimate) + 8 sequences 21.6 MB + plate ~0.1 = ~23.5-24.5 MB vs ~28 MB repartitioned -> closes with ~3.5-4.5 MB spare.
