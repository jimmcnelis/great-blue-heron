# Stage B Manifest — living loop, full behavior set

Built 2026-11-04 night, after Stage A passed on the real board.

## ⚠ VERDICT: GATE — storage. Jimmy's decision needed before any flash.

Everything Stage B needs is built and verified **except** the one thing
that cannot be engineered around inside the rules: **the full clip set
does not fit the board's flash at the mandated quality.**

- All 9 clips at PIL/libjpeg **q80, 12 fps** (the proven Stage A route):
  **59,013,180 bytes** of MJPEG + ≈2.5 MB app binary ≈ **61.5 MB total**.
- The board has **32 MB** of flash. The current app partition is 20 MB;
  grown to the maximum sane size (31 MB factory, 0x10000 offset, ~1 MB
  tail margin) it holds 32,505,856 B — the payload still overflows it
  by **≈29 MB**.
- At the brief's quality floor, **q75**, the behavior set measures
  ≈43.6 MB (stride ratio q75/q80 = 0.884, measured) → total ≈55.8 MB.
  Still ≈23 MB over a max-grown partition.
- Fitting flash would require the behaviors to shrink to ≈22.5 MB —
  **≈46% of their q80 size, i.e. roughly q50 or ≈5–6 fps**. The brief
  forbids dropping below q75 or 12 fps silently, so the build stops
  here and the choice goes to Jimmy (options below).

The Stage A project in this folder is **untouched and still builds and
flashes exactly as proven**. Stage B assets live in `stageb_clips/`;
the Stage B player is complete as `stageb_player_draft.c` (not wired
into the build). Nothing in this state should be flashed as "Stage B".

## Clips — encoded and verified (all 120 frames @ 12 fps, 1024×600)

Route (proven in Stage A; the ffmpeg MJPEG encoder is a known failure
on this chip): frames extracted at 12 fps (every 2nd frame of the
24 fps sources), background-normalized, then PIL/libjpeg
`quality=80, subsampling=1, optimize=True`
(`tools/clip_convert_stageb.py`). Nightstalk is excluded from the
device set (no light sensor in the kit — playlist-only, per spec).
The catch does not exist (closed by Jimmy).

| Clip | Source (final/anim/) | Bytes | Avg frame | Max frame | md5 |
|---|---|---|---|---|---|
| preen | preen_attempt1.mp4 | 6,435,722 | 53,631 | 59,918 | `d63260bf75a786541eca0a88a9b13205` |
| stride | stride_attempt2.mp4 | 9,836,559 | 81,971 | 85,028 | `51d9a6a0f1b03fd8ee2d5fff4e7b4b2e` |
| strike | strike_attemptA.mp4 | 7,202,580 | 60,022 | 63,805 | `63b01064b65bb2b45ea13beda99b52ac` |
| stretch | stretch_attempt1.mp4 | 6,843,508 | 57,029 | 72,647 | `d04835f445fc2c30e3a0914e0eca7c76` |
| flight | flight_attempt1.mp4 | 6,221,598 | 51,847 | 67,831 | `3f59f64ce18bfc7f646431fef05a7cb9` |
| miss | miss_attempt1.mp4 | 6,771,964 | 56,433 | 61,364 | `7a49c6ac04e7df9213b0e6f2387676ea` |
| courtship | courtship_attempt1.mp4 | 6,015,122 | 50,126 | 60,501 | `669ed179562a0dc3a4dabf17d10a9e38` |
| **behaviors** | | **49,327,053** | | **85,028** | |
| idle1 (Stage A file, reused as-is) | attempt1.mp4 | 8,674,418 | 72,287 | 77,128 | `c17afe8f5cfa00b78ba7cb45252fa2fa` |
| idle2 (Stage A file, reused as-is) | attempt2.mp4 | 1,011,709 | 84,309 | 86,196 | `910e8fdad928203cc6a609c5926c2048` |
| **all clips** | | **59,013,180** | | **86,196** | |
| idle1_norm (option asset, not in build) | attempt1.mp4, normalized | 6,520,692 | 54,339 | 56,956 | `29bfb138e90a3fe23a8496dd76722fb7` |

**Verification, every behavior clip:** SOI/EOI scan consumes the blob
exactly (120 frames, zero trailing bytes); first-frame SOF parses to
1024×600 with components **(id1: H2 V1), (id2: 1,1), (id3: 1,1)** — the
only 4:2:2 layout the ESP32-P4 JPEG driver recognizes (root-caused from
Espressif's v5.5.5 source during Stage A); every 12th frame decodes
standalone at 1024×600; largest single frame anywhere is 86,196 B, so
Stage A's 128 KB player input buffer needs no change.

## Background normalization — applied to all 7 behavior clips

Method (`tools/clip_convert_stageb.py`): per-clip background B =
border-pixel median over sampled frames; target P = the approved
plate's border median **(247, 232, 210)**. Each pixel is pulled toward
`P + (pixel − B)·0.35` (level lifted to paper, deviation damped —
grain cut) with a smoothstep weight on RGB distance from B: full
weight ≤12, zero ≥45. Per-clip B is used for the whole clip (no
frame-to-frame flicker).

Bird protection, proven two ways:
- **Numeric** (preen frames 0/60/119): max |Δ| over every pixel ≥45
  RGB units from B is **0.000** — the bird is bit-identical; near-
  background pixels lift by ≈5 levels on average.
- **By eye**: normalized stills (frames 0/60/119) of all 7 clips were
  viewed — plumage, plume strands, rusty thighs, bills and rings are
  intact everywhere; backgrounds sit on clean paper that matches the
  plate. No clip needed the ship-unnormalized fallback.

Border statistics (RGB mean / std, sampled frames). For preen, strike
and miss the border is pure background and lands on the plate target;
for stride, stretch, flight and courtship the bird (or stride's drawn
water) crosses the borders, so border std stays high before and after
— those four were judged on the median estimate + the stills above.

| Clip | B (median) | Before mean | Before std | After mean | After std |
|---|---|---|---|---|---|
| preen | (241, 227, 207) | (240.4, 226.8, 206.2) | (4.2, 4.6, 5.3) | (247.0, 231.4, 208.6) | (2.5, 2.6, 3.0) |
| strike | (240, 227, 207) | (239.5, 226.6, 206.5) | (5.1, 5.5, 5.8) | (246.9, 231.2, 208.8) | (3.9, 4.2, 4.4) |
| miss | (239, 227, 207) | (238.9, 226.0, 207.0) | (4.1, 4.1, 4.2) | (247.2, 231.1, 209.1) | (2.8, 2.6, 2.6) |
| stride | (245, 232.5, 215.5) | bird/water in border | ≈(43, 41, 37) | stills-verified | — |
| stretch | (243, 229, 213) | bird in border | ≈(20, 18, 17) | stills-verified | — |
| flight | (243, 232, 211) | bird in border | ≈(47, 44, 38) | stills-verified | — |
| courtship | (241, 228, 209) | bird in border | ≈(32, 30, 27) | stills-verified | — |

The idles were **not** re-encoded (brief: reuse the Stage A files).
A normalized idle1 variant was encoded for the option math below
(6,520,692 B — saves 2,153,726 B) and sits in `stageb_clips/` ready.

## Partition math (bytes)

| Item | Bytes |
|---|---|
| Behavior clips (7, q80) | 49,327,053 |
| idle1 + idle2 (current) | 9,686,127 |
| App binary (Stage A-derived estimate, incl. 1.23 MB plate) | ≈2,500,000 |
| **Total payload** | **≈61,513,180 (58.7 MiB)** |
| Current factory partition (20M) | 20,971,520 → over by ≈40.5 MB |
| Max sane factory (31M, 0x10000 offset, ~1 MB tail) | 32,505,856 → over by ≈29.0 MB |
| Same payload at q75 (measured ratio 0.884) | ≈55.8 MB → over max by ≈23.3 MB |
| Behavior budget inside max partition (with idle1_norm swapped in) | 22,473,455 = 45.6% of q80 size → ≈q50 or ≈5–6 fps |

## Options for Jimmy

**A. microSD streaming — recommended.** The board has a TF (microSD)
slot, SDIO 3.0 (Waveshare's docs for this exact board, SKU 32510:
"TF Card Slot — SDIO 3.0"; Waveshare ships an SDMMC demo for it).
All 9 clips at full q80 (59.0 MB) live as files on a FAT card; the
firmware shrinks to ≈2.6 MB in the existing 20M partition. The draft
player's frame source swaps from embedded blobs to file reads;
scheduler, crossfade, decode and display are unchanged. Pros: full
accepted set at full quality; room for nightstalk later; clip updates
become file swaps, no reflash. Cons: needs a microSD card (any ≥1 GB;
not in the kit order — a small purchase) and one proof flash of the
SD mount path (new code, vendor-supported but unproven on this unit).
Fallback behavior if the card is missing/unreadable: stay on the boot
plate and log it — the portrait degrades to a still, never a brick.

**B. Flash-only subset bag.** Grow factory to 31M and swap in
idle1_norm: ≈22.5 MB of behavior budget → at most 3 behaviors at q80,
e.g. preen+strike+flight (19.86 MB, 2.6 MB spare) or
preen+strike+stretch (20.48 MB). Loses stride (Jimmy's "looks great"
walk), miss, and courtship from the device. Bag tickets re-weight to
the subset in the follow-up build.

**C. Trimmed device cuts.** All 7 behaviors cut to ≈4 s windows
(48 frames) ≈19.7 MB + idle1_norm + idle2 + binary ≈29.7 MB — fits
31M. But a 4 s window is not the accepted 10 s signature cycle; the
scheduler's law is that cycle internals are never altered. Listed for
completeness; not recommended.

**D. Waive the floors.** Behaviors at ≈q50 or ≈6 fps would fit flash
(≈22.5 MB budget). Visible degradation of approved art — only Jimmy
can choose this knowingly.

## Player — design notes (`stageb_player_draft.c`, complete, unbuilt)

- **Proven core untouched**: BSP display start, plate widget, decoder
  engine config, `jpeg_decoder_process` 7-arg call, BGR element order,
  SOI/EOI scan, skip-on-error — all Stage A, byte for byte where it
  matters.
- **Scheduler**: direct port of `living_loop_scheduler.py` — 14-ticket
  bag (preen×3, stride×3, strike×2, stretch×2, miss×2, flight×1,
  courtship×1), draw without replacement, refill reshuffles until the
  first ticket ≠ last behavior played (64-attempt cap, a formality at
  ≤3/14 odds). Idle holds 20–90 s built exactly as the reference:
  idle1 10 s blocks sprinkled while ≥30 s remains (50% coin), idle2
  tiles the remainder, unit order shuffled. Opens on a hold; a hold
  follows every draw.
- **Crossfade**: 4 frames (≈0.33 s at 12 fps) at every unit join —
  including plate→first-hold: at player start the plate is copied into
  a frame buffer and the widget re-pointed at the copy, so the "from"
  side of the first fade is the plate itself. Blends run in a third
  PSRAM buffer (RGB565 channel-expand → lerp → repack); the shown
  buffer is never written, and the decode slot logic never targets the
  shown or blend buffer. After the last fade step the real frame is
  presented exactly, so no blend rounding persists.
- **Random/logging**: `esp_random()` seeds everything; the seed value,
  every draw (`draw #N: <behavior> (M ticket(s) left in bag)`), every
  hold (`idle hold: H s` + per-unit starts), refills and reshuffles
  are logged on serial — a full evening's behavior can be audited from
  the log alone.
- **Buffers**: in 128 KB (max frame 86,196 B ✓), out ×2 + blend ×1 at
  OUT_BUF_BYTES (1,490,944 B each) ≈ 4.6 MB of the 32 MB PSRAM.
- The draft assumes embedded symbols; under option A only the cursor
  changes (file-backed spans). Frame counts in the tables are the
  verified offline counts.

## Serial-log expectations (follow-up build, whichever option)

```
heron_living_loop: heron living loop — STAGE B (shuffle-bag + crossfade)
heron_living_loop: random seed (esp_random): <value>
heron_living_loop: boot plate on screen (1024x600 RGB565)
heron_living_loop: decoder buffers: in 131072 B, out … + … B, blend … B (PSRAM)
heron_living_loop: player task running — living loop is live
heron_living_loop: bag refilled (14 tickets)
heron_living_loop: idle hold: <20–90> s
heron_living_loop: unit start: idle2 — … (then idle1 blocks, shuffled)
heron_living_loop: draw #1: <behavior> (13 ticket(s) left in bag)
heron_living_loop: unit start: <behavior> — 120 frames @ 12 fps, … bytes embedded, crossfade in
heron_living_loop: <behavior>: JPEG header 1024x600
heron_living_loop: <behavior>: decoded frame size 1228800 bytes (expect 1228800)
… draws continue; "bag emptied — reshuffle" after draw #14 …
```
(Under option A the per-unit line reads "bytes on card" — set at
integration time.)

## Known risks

1. **Blend cost unmeasured on-device.** One blend pass is 614,400 px of
   integer lerp; expected tens of ms on the P4, inside a 83 ms frame
   period already shared with a ~10–20 ms HW decode. If a fade frame
   overruns, the fade simply runs a touch long (DelayUntil slips, no
   tearing) — judged by eye on the first flash.
2. **Option A is new code on this unit.** SDMMC mount + FAT reads are
   vendor-demo'd for this board but not yet proven in this project;
   it gets its own one-shot proof (mount + first clip) before the full
   loop is trusted. Card must be inserted before power-up in the
   current case (slot access is a bench operation).
3. **App binary size is an estimate** (≈2.5 MB from Stage A's build:
   6.8 MB total − 4.31 MB of Stage A clips). Option B/C margins should
   be re-checked against the real Stage B link before flashing; option
   A makes the point moot.
4. **idle1 remains the unnormalized Stage A file** unless an option
   swaps in idle1_norm; its grain against normalized behaviors is the
   exact mismatch the crossfade exists to soften.

## Files

| File | Bytes | md5 | Route |
|---|---|---|---|
| `STAGE_B_MANIFEST.md` | this file | — | Spark → Studio text pull |
| `tools/clip_convert_stageb.py` | 5,179 | `b56af748ce2ae32d9d089fd06d6356b9` | Spark → Studio |
| `stageb_player_draft.c` | 20,603 | `05e55374c2a7d4dfea7534188485ae5a` | Spark → Studio |
| `stageb_clips/*.mjpeg` (8 files) | 55,847,745 total | table above (+ idle1_norm) | Spark → card/Studio |

Stage A files (`main/*`, `partitions.csv`, `sdkconfig.defaults`) are
unchanged; `partitions.csv` still says 20M — growth belongs to the
option Jimmy picks, not to this gate.
