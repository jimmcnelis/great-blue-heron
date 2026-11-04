# Route 3 — part-composite proof (no neural decoder)

**Pipeline (the only steps, in order):** rembg `isnet-general-use` alpha per
donor → part masks = hand-keypointed polygons ∩ rembg alpha (neck = tube
around the spine keypoints; legs = segment tubes, with a disclosed fallback to
the bare tube where rembg dropped the thin legs) → per-part thin-plate-spline
warp, scipy `RBFInterpolator(kernel='thin_plate_spline', smoothing=1.5)`,
fit target→source and applied with `cv2.remap` → alpha feather (5 px Gaussian
on each part's alpha, so the softening lands on part boundaries) → global
color harmonization for the IR donors only (below) → alpha-over composite in
rig draw order (far leg, far wing, tail, torso, wing, neck, head, near leg) on
blank white → standing legs clipped at the waterline (master y = 493).
No other post-processing. No retouching. Seams are left visible; see the
`crop_*_100pct.png` files in `out/` — they are unmodified 100% crops of the
masters at the neck/torso and wing joins.

Builder: `route3_build.py` (this folder). Donor keypoints were read off
50 px grid overlays of each donor frame and are stored in the builder.

## Donor map

| Pose | Part | Donor | Notes |
|---|---|---|---|
| rest, swallow, flight | torso, folded wing, tail, head+bill, both legs | `reference/real-heron-b.jpg` (643×900 still, standing profile, neck extended) | One donor supplies every profile part in all three poses. |
| rest, swallow | neck | same frame, neck tube on spine (302,418)→(332,128) | Donor neck is near-straight; rest's coil (0.85) and swallow's straight-but-short spine are both produced by the warp, not by the photograph. |
| swallow | neck bulge | same neck part, target tube widths widened by the kept r4 rule: `widths *= (1 + 0.80·0.95·fish_profile(s − 0.44))` (`maskrender.fish_profile`, s = 1 − t along the spine) | Same deformation the rig/mask routes use. |
| flight | near + far wing | `reference/footage/kayak-heron-night-05.mp4` @ **t = 12.7 s** (IR, frontal braking fan), right half of the fan only | IR monochrome + motion-blurred. Color-matched to the body's slate by the global harmonization below — disclosed compromise, see below. Far wing = same part, target poly scaled 0.92 about the root, rotated −14°, darkened ×0.80 (per rig spec). |
| flight | everything else | `real-heron-b.jpg` | Neck folded to the flight spine by TPS; legs warped to trailing (hip/knee/foot) targets, no waterline clip. |
| front | **all parts** | `reference/footage/patio-heron-night-03.mp4` @ **t = 16 s** (IR, frontal stand on the dock; crop x 1000–1280, y 250–720 of the 1280×720 frame) | The only real frontal body source in the corpus. IR-derived texture, colorized only by the global harmonization below. |
| — | (not used) | `real-heron-a.jpg` (S-neck perch, warm sunset cast), sunrise-04 color flight frames (~60 px bird), day-02 color frames (~200 px bird) | A was held in reserve as alternate neck/torso and not needed; its warm cast differs from B and mixing donors per-part would add a second harmonization problem. The color flight frames are too small to supply a wing at master size (would be ~5–8× upscale). |

**Global harmonization (disclosed):** IR parts (front pose entire bird,
flight wings) are grayscale. Each IR pixel's gray value was multiplied
channel-wise by (mean RGB of donor-B torso) / (mean gray of donor-B torso)
= ×[0.882, 0.950, 1.168], i.e. a single global white-balance/slate tint
anchored on the color donor's torso. No local color work anywhere.

## Upscaling factors (target part bbox area vs donor part bbox area, sqrt)

>1 = the part is enlarged beyond its photographed size; <1 = downscaled.

| Part | rest | front | swallow | flight |
|---|---|---|---|---|
| torso | 0.55 | 1.20 | 0.55 | 0.52 |
| wing | 0.53 | 1.34 | 0.54 | 0.68 (far 0.63) |
| neck | 0.87 | 1.45 | 0.58 | 0.81 |
| head | 0.76 | 1.01 | 0.76 | 0.76 |
| tail | 0.54 | 1.53 | 0.53 | 0.50 |
| leg near | 0.99 | **3.22** | 1.75 | 1.25 |
| leg far | 1.64 | **2.91** | 1.20 | 1.13 |

Profile parts from donor B are comfortably *down*scaled — B is a genuinely
high-resolution donor. Everything frontal is upscaled, legs worst (~3×),
because the frontal bird is ~100 px wide in its only source frame.

## Compromises (all disclosed, none hidden)

1. **Flight wing is IR + motion-blurred + frontal.** The fan at night-05
   t≈12.7 s is a braking fan seen head-on, blurred by the wingbeat. Mapped
   onto the profile raised-wing outline it reads as a smooth slate slab —
   the feather detail is blur, not plumage. Its slate color is the global
   tint, not photographed color. The sunrise color alternative is a ~60 px
   bird; using it would trade blur for a ~6× upscale. I chose blur.
2. **Front pose is IR-derived and luminance-blown.** The patio bird is
   overexposed IR (near-white body). A global white-balance tint cannot
   invent the slate plumage tones that were never recorded; the composite
   stays pale blue-grey no matter the tint anchor.
3. **TPS correspondence is fragile.** First pass at the flight wing used
   interior control points and the spline folded the fan into swirls; the
   shipped pass uses outline-only control points ordered to match the
   target `wing_poly` semantics (root → leading edge → tip → fingered
   trailing edge → root). Same for the front head: the donor's
   downward-hanging frontal bill is mapped to the rig's front `bill_poly`
   downward spike (its pts 9–10) — the only correspondence that doesn't
   fold. These are judgment calls a full build would have to re-make per
   donor frame.
4. **One profile donor for three poses.** Rest/swallow/flight bodies are
   the same photographed feathers re-warped. Where a pose differs strongly
   from the donor stance (rest's deep neck coil from a straight neck),
   the texture is stretched/compressed accordingly — visible in rest's
   neck, which is thinner and smoother than the torso's plumage.
5. **Legs are the weakest profile part too.** In donor B the legs are
   thin, dark and partly grass-occluded; rembg kept them only partially,
   so the leg tubes partly sample shadowed grass-edge pixels. On the
   masters they read as dark sticks — accurate to the donor, not lifelike.
6. **Far-wing and tail are approximations.** Far wing reuses the near
   wing's fan texture (rig's own approximation); tail is a 3-point sliver
   of donor B's rear body feathers, not a photographed tail fan.

## Per-pose honest read

- **rest** — The best of the four. A real heron, real feathers, correct
  slate. Faults, all visible: a white notch tears at the front of the
  neck base where the warped neck tube fails to meet the breast; the
  coiled neck is visibly smoother/thinner than the torso (texture
  stretched from a straight donor neck); the folded wing double-registers
  against the wing already present in the torso texture (dark shoulder
  patch appears in both layers, offset). Legs are dark sticks ending at
  the waterline as designed.
- **swallow** — The neck **tears**: its warped bottom end comes to a point
  and stops short of the breast, leaving a white wedge gap at the join
  (see `crop_swallow_100pct.png`). The fish bulge is present in the tube
  widths but reads as a shapeless thickening, because the donor neck had
  to compress ~290 px of length into ~166 px — the bulge and the
  compression are indistinguishable. Head and body are clean; legs splay
  per the rig pose and look pasted at the hips.
- **flight** — Silhouette works; the wing does not bear inspection. The
  IR fan becomes a smooth grey slab with a bite-shaped alpha notch on its
  leading edge and a hard straight clip where the far wing exits behind
  it. The folded neck warps into a thin wavy ribbon (donor neck feathers,
  designed to hang vertically, smeared horizontal). Trailing legs and
  tail merge into one dark streak. It is a heron-shaped collage, not a
  flying heron.
- **front** — **Indefensible, shown anyway.** A pale blue-white blob torso,
  a neck collapsed to a ~10 px dark-streaked ribbon, the head+bill reduced
  to a small hook at the top, legs as two grey wisps (2.9–3.2× upscale of
  ~6 px-wide IR legs). It does not read as a frontal heron. The cause is
  corpus, not code: the only frontal source is a ~100 px-wide,
  luminance-blown IR frame, and no warp recovers information that was
  never photographed.

## Limits

What breaks first in motion: this route re-warps every part from scratch on every frame, so nothing is temporally stable — the alpha-feathered seams will swim frame to frame as each TPS field is re-solved from slightly different keypoints, and the neck–torso tear already visible in the still swallow pose will open and close like a hinge whenever the coil changes, because the neck and torso are independent warps that only agree at the shared spine-base point, not along a shared edge. Texture stretching is the second failure: a part photographed in one configuration (the donor-B neck nearly straight) is rubber-sheeted into configurations it never had (rest's deep coil, flight's folded neck), so feather detail smears along the bend and compresses across it, worst exactly where the eye looks — the neck. Third, the corpus is the ceiling: there is exactly one usable high-resolution profile donor, one ~100 px-wide blown-out IR frontal, and one motion-blurred IR wing fan, so any pose the donors don't already resemble (front, extreme coil, spread wing in profile) is manufactured by the warp, not photographed. Cost to a full build: a donor library per part per orientation — at minimum several clean frames each of profile / three-quarter / frontal bodies, necks in coil / S / extended states, folded and spread wings in color, and legs in stance and trail — plausibly 30–60 curated, keypointed donor frames before motion even starts, plus per-frame re-warp cost and a seam-management pass this proof deliberately did not build.
