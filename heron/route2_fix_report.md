# Route 2 — FIX 1 (plate-neural, naturalist fine-art)

Jimmy's pick (2026-11-03): "Route 2 wins — fix its texture and the swallow
head." Same four target poses from the same kept pose data
(`art2/targets/` + `poses_art2.json`), rendered unretouched by the fixed
decoder. Proof checkpoint in `art2/route2/out/` is the "before" for every
number below; identical measurement code (`art2/measure_fix.py`) ran on
both.

## Diagnosis

### 1. Texture — soft wash + checkerboard
Two separate causes, both confirmed in the proof code and outputs:
- **Checkerboard:** the shared decoder upsamples with
  `ConvTranspose2d(..., 2, stride=2)` — the classic checkerboard source
  (uneven kernel overlap prints a period-2 grid). Measured on the proof
  renders: the swallow crop's high-frequency residual correlates 0.47
  with a pure (−1)^(i+j) checkerboard (natural texture ≈ 0).
- **Wash:** plain L1 + a 0.3-weight Sobel term lets the decoder average
  away fine detail. Measured: proof renders carry a body-region
  high-frequency energy of 0.011–0.014 against a corpus median of
  0.067 — only ~17–21% of the plates' texture survives decoding.
- Compounding: the proof's random 12% val split (2 samples) picked the
  checkpoint at step 800 of 4000 while train loss kept falling — early
  checkpoint on a noisy signal.

### 2. Swallow head — missing
Not a conditioning failure: the target swallow's head channel carries
2,923 px at master scale — the geometry reaches the decoder. It is a
**corpus hole**, verified numerically: the only two swallow training
samples (plates a/b) toss the head BACK (pose pitch ≈ −0.87), while the
target holds the head LEVEL (pitch +0.02) on a straight upright neck
(coil ≈ 0.03). At pitch ≈ 0 the straight-neck neighbourhood contains no
head at all — the nearest sample is the strike (pitch +0.50, head down).
The head is also only ~1.3% of crop pixels, so plain L1 treats it as
noise. The decoder did the statistically reasonable thing and omitted it.

### 3. Identity drift
The proof corpus' 20 plates vary in crest treatment (front_a carries
crest tufts the proof front render turned into twin horns) and the
decoder averages what it is given. The fix is corpus discipline: every
new plate was generated against an accepted plate as reference with the
markings spelled out identically (slate body, white face, black brow
into ONE occipital plume, yellow-orange dagger bill, rusty thighs,
black shoulder patch, shaggy breast plume), and each was eyeball-QA'd
before annotation; one front plate with a crown spike was rejected and
regenerated.

## What changed

**Architecture (train_decoder_fix.py):**
- Transposed-conv upsampling → resize-convolution (nearest upsample +
  3×3 conv) at all four upsampling stages.
- Loss: + high-frequency residual term (weight 0.3), Sobel gradient
  weight 0.3 → 0.5, and pixel weights multiplied by (1 + 2·headmask)
  so head-region pixels count ~3× in rgb and alpha loss.
- Validation: named holdout instead of random split — held out:
  plate_swallow_d (level-head swallow, the defect under test),
  plate_rest_e, plate_front_c, plate_flight_down_c. 32 train / 4 val.

**Corpus (+16 plates, 36 total):** a level-head swallow family —
six plates, heads LEVEL on straight vertical necks, fish bulge measured
at bulge_pos 0.36 / 0.64 / 0.69 / 0.77 / 0.90 plus one smooth-neck
post-swallow (the target sits at 0.44, pitch +0.02: now bracketed in
both dimensions) — plus rest ×2, front ×2 (crest-clean), three-quarter,
walk, coil, a head-down strike reach, and flight up/down with clean
spread wings. All annotated through the same grounding → build_kp →
build_sample path; plume is its own channel everywhere (plume law);
legs annotated as thin sticks (hip at the true hip under the skirt).
One plate (swallow_e) arrived facing left and was mirrored to the
corpus' right-facing convention before annotation. Bulge scalars were
measured off the finished plates, not copied from generation prompts
(the generator consistently placed bulges lower than asked).

**Training:** 6,000 steps, batch 6, AdamW lr 2e-4, OneCycle — same
optimizer recipe as the proof; best checkpoint by named-holdout val.

## Results (before → after)

Shipped checkpoint: step 6000 (`last.pt`). The val-best checkpoint
(step 600, val 0.0848 vs 0.0858 — inside noise on 4 holdout samples)
renders noticeably paler; on the target poses it keeps only 23–29% of
corpus texture against the step-6000 model's 38–71%, so the deliverable
is the step-6000 model. Its renders are in `art2/route2/out_last/`;
the step-600 renders are kept in `art2/route2/out_best/` and both
checkpoints are on the Spark (`~/art2route2_fix/ckpt/`).

**Texture** — body-region high-frequency energy (mean |lum − blur5(lum)|
inside the target torso+wing region; corpus median over all 36 plates
= 0.0672):

| pose | proof | fix | % of corpus (proof → fix) |
|---|---|---|---|
| rest | 0.0113 | 0.0331 | 17% → 49% |
| front | 0.0143 | 0.0480 | 21% → 71% |
| swallow | 0.0116 | 0.0254 | 17% → 38% |
| flight | 0.0129 | 0.0423 | 19% → 63% |

**Checkerboard** — (−1)^(i+j) correlation of the HF residual (1.0 =
pure checkerboard): swallow 0.468 → −0.002; rest/front/flight were
≤0.078 and are now ≤0.002. **The checkerboard is gone on all four.**

**Swallow head** — the head is drawn now: white face, brow and bill
read clearly in the sheet and the 100% crop, where the proof had a
headless neck with a detached bill-dash. Region numbers (head channel
from the kept target masks): decoder-alpha occupancy (fraction of
head-polygon pixels with alpha > 0.5) 0.031 → 0.041, mean alpha
0.034 → 0.046. Read those with the calibration: the head polygon is
the skull-box hull plus the bill triangle — mostly empty corners — and
the front pose (head undisputed in both models) scores 0.49 (proof) /
0.32 (fix) on the same scale, so ~0.3 is roughly "solid head" here and
the swallow head is present but SOFT, not solid. A darkness-based
occupancy actually falls (0.167 → 0.071) because the proof's grey
smudge was darker than the fix's correctly white face; alpha + eyes
are the honest witnesses. Front head alpha occupancy falls too
(0.487 → 0.315): the fix's front head is smaller and paler, with a
two-dot crest remnant — the twin-horn artifact is reduced, not gone.

**Legs (protected invariant)** — median drawn width vs the target
mask's stick width, master px (scanline measure, ±40 px search around
the mask line; both models measured identically):

| pose | proof (near/far) | fix (near/far) | mask sticks |
|---|---|---|---|
| rest | 9.5 / 5.0 | 9.5 / 7.0 | 6.0 / 5.5 |
| front | 9.0 / 6.5 | 7.5 / 7.5 | 7.0 / 6.0 |
| swallow | 13.0 / 8.5 | 11.0 / 8.0 | 6.5 / 6.0 |
| flight | not measurable | not measurable | 5.0 / 5.0 |

No regression: equal or narrower than the proof in five of six
standing measurements, and the front far leg — missing in the proof —
is drawn. Legs are still ~1.3–1.7× the geometric stick width, as they
were in the proof; "thin separated sticks" holds relative to the
proof, not yet to the mask ideal. Flight's trailing legs are too
faint/displaced for the scanline measure in every model, proof
included.

**Identity** — face-region mean RGB across the standing poses:
proof spreads 0.52–0.75 (and the flight face doesn't register at
all); the fix holds 0.67–0.69 in all three, torso 0.56–0.58. The
black shoulder patch lands in the swallow render. Same bird, more
consistently.

**Training curve honesty:** named-holdout val bottomed at step 600
(0.0848) and sat at 0.085–0.089 for the remaining 5,400 steps while
train loss fell 0.063 → 0.009 — this corpus + architecture reaches
its generalization ceiling early and memorizes after. (Val numbers
are not comparable to the proof's 0.0907: the loss function changed.)

## Limits

- **Texture character, not just quantity.** The surviving texture is
  a charcoal-like speckle, strongest on the front (71% of corpus
  energy) where the body reads as a grainy bell. The plates' grouped
  hatch/wash masses — the rigging study's "texture as grouped masses"
  — are not what the decoder learned; it learned high-frequency
  energy. At 1024×600 the speckle reads as grain, not as feather
  structure.
- **Heads are present but soft.** Alpha in the head regions stays
  low; faces are rendered in near-paper tones, so heads — the front's
  especially — read pale and small at a glance, with a residual
  two-dot crest on the front view.
- **Flight is still the weakest pose.** Head and long bill are drawn
  but displaced from the conditioning channel (region-locked metrics
  read 0.000 in all three models, proof included); the folded neck
  partially dissolves and the trailing legs are faint. Two new flight
  plates were not enough mass for this pose family.
- **Legs:** improved parity (both front legs drawn, swallow legs
  narrower) but still ~1.3–1.7× mask width.
- **Corpus notes:** swallow_h's fish bulge is cream-toned in its
  source plate (the other five bulges are grey); rest_e's paper is
  warm-toned and it carries a small reddish shoulder spot. Neither
  was rejected — variation the decoder averages over — but they are
  in the training data as-is.
- **Next levers, if Jimmy wants another round:** more flight and
  front plates (the two thin families); texture bound to parts as
  drawn geometry (hatch overlays in the style pack, per the rigging
  study) instead of hoping a pixel loss discovers it; a lower final
  LR or earlier stop does nothing — the ceiling is data, not steps.
