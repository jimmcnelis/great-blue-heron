# Heron Movement Study — the real animal, as the foundation for v1.2

*Written 2026-11-02, after Jimmy's v1.1 verdict ("eating the fish is messy…
legs improved but still clunky… lots wrong still") and his follow-up ruling
(15:18): "the animations themselves can be mostly static. i'd rather it be
good but repetitive than janky but entirely random."*

*This is research + authoring groundwork. No model was built or trained.
The machine-usable companion is `movement-charts.yaml` — same content,
expressed as exact frame budgets for the pose-space rig.*

---

## 0. The design axiom (Jimmy, 2026-11-02 15:18) — and why it is also the animal truth

1. **Stillness is the default state.** A hunting great blue heron is a
   statue that occasionally explodes. Cornell: hunting birds "wade slowly
   or stand statue-like"; observers consistently describe minutes of
   motionlessness between events [1][2]. The animation should therefore
   be *mostly holds*: long, true holds, with a small number of very good
   actions between them.
2. **One polished signature cycle per behavior, repeated verbatim.** A
   canonical strike, a canonical step cycle, a canonical swallow. The
   audience will see them again; that is fine — repetition of a *good*
   cycle reads as character (limited animation ran on exactly this).
3. **Variation only as 2–3 discrete, hand-checked authored variants.**
   Never continuous random perturbation of motion — in v1/v1.1 the seeded
   random variation (random coil times, random sway phases, per-seed
   everything) is precisely where the jank lives. Variety comes from
   **scheduling** — which behavior, in which zone, after how long a
   hold — not from regenerating the motion.
4. **Charts use exact frame numbers.** Where the real animal varies, the
   range is noted in this study's text and the chart picks one canonical
   value.

**Grading used throughout:** [Documented] = a source below states it;
[Probable] = consistent across sources / standard anatomy, no species-
specific measurement located; [Canonical] = an animation decision made
for 24 fps readability, grounded in the graded facts but not itself a
measured animal number. Every sub-second timing in this study is
[Canonical] unless marked otherwise — see §12, honesty notes.

---

## 1. The anatomy that drives everything

- **The strike hinge.** Herons have one uniquely long cervical vertebra —
  the 6th — that acts as a hinge/lever: the neck folds into its S (or Z)
  kink at that point and then snaps straight, flinging the head like a
  spear-thrower (atlatl). It "starts off apparently slow, but then extends
  really, really fast" [3]. A 2026 comparative study of pelecanimorph
  cervical morphology confirms ardeids evolved specialized **mid-neck**
  vertebrae for "a rapid straightening of the neck to propel the head
  toward prey" [4]. Two consequences for the rig: (a) the strike is a
  *straightening of a folded lever*, not a telescoping neck — the head
  travels on the arc the hinge dictates and the last part of the path is
  the fastest; (b) the kink restricts sideways neck movement — herons
  strike **in the plane they are facing**, which is why aim (body + head
  orientation) matters so much before release [5].
- **Seize, usually; spear, sometimes.** "It is uncommon for the bill to
  actually stab or pierce the prey… the bill opens up at just
  one-thirtieth of a second before impact," working "like pincers or
  forceps" [6]. Larger prey may be impaled [1][7]. So the canonical catch
  is a **grab**: the bill must visibly open just before contact and close
  on the fish. (v1.1's bill never opens — see §3.)
- **Aim is visual and corrected late.** Reef Herons (close relatives)
  correct for water refraction "within a tenth of a second before they
  break the surface" [3]. GBH also hold their heads **slanted to the
  side for minutes at a time**, especially in sun — apparently to beat
  glare (Krebs & Partridge, 1972, via [3]). The aiming bird is not a
  statue with a neutral head: it fixates, tilts, and makes tiny late
  corrections.
- **The leg's "backward knee" is the ankle.** The visible mid-leg joint
  is the **intertarsal joint** (ankle). The true knee is hidden in the
  body plumage and bends forward; below the ankle is the
  tarsometatarsus (fused foot bones); the bird walks on its toes
  (digitigrade) [8]. Everything "clunky" about legs is usually a wrong
  fold at this joint — see §4.
- **Gaze mechanics (all birds).** Birds shift gaze in **saccades**:
  extremely fast head turns (lovebirds: mean ~930°/s, peaks 2,690°/s —
  the fastest vertebrate saccades recorded) separated by fixations in
  which the head is **stabilized in space** while the body moves
  (vestibulo-/opto-collic reflexes) [9][10]. While walking, birds make
  "translational saccades": the head **holds still in space** while the
  body walks underneath it, then thrusts quickly to a new hold [10].
  This one fact rewrites our idle, our walk, and our turn (§5, §8).

---

## 2. The hunt idle — stillness with a working head

**The animal.** Two hunting modes: stand-and-wait (motionless, neck
coiled, sometimes for many minutes) and slow stalking (§4). In
stand-and-wait the body does nothing. The *head* works: long fixations
on the water, broken by saccadic re-aims; occasional slow scans; the
head sometimes cocked sideways (glare) [3]; the neck held in the coiled
S — the loaded spring — the whole time [2][11].

**What v1.1 does vs what the animal does.**
- v1.1 idle = four perpetual sine waves (periods 3.3–6.9 s) on root,
  neck, plume, head — the bird **breathes like a metronome and never
  once holds still**. The animal is the opposite: stillness punctuated
  by events.
- v1.1 "head turns" ride `neck_sway` — a smooth 0.7 s sinus-ish slide of
  the neck top. Real gaze shifts are **saccades**: 2–4 frames of motion,
  then a hard fixation. A sliding head reads as a camera pan, i.e. as
  machinery.
- v1.1 look-back **snaps**: `look_back` animates 0→1 over ~0.45 s but the
  rig thresholds it at 0.5, so the head (beak, cap, plume, eye) flips
  direction in a single frame mid-"turn". That is the "flip the bird
  card" defect in miniature, already inside the idle.
- No head roll anywhere: v1.1 cannot do the animal's signature
  sideways-cocked glare-avoidance tilt [3].

**The v1.2 answer** (chart: `idle_hunt`): a 480-frame (20 s) authored
hold — zero root motion, neck coiled at hunting depth — containing only
discrete events at exact frames: blinks, two gaze saccades (3 frames
each), one head-roll tilt held and released, one slow scan. 2–3 variants
differ **only in the event script** (which frames, which direction),
never in continuous noise. Doze gets its own pose (§9), not a damped
idle.

---

## 3. The strike — a hinge snapping straight

**The animal, in phases.**
1. **Fixation.** Head locked on the prey; body still. May last seconds
   to minutes; the chart starts at the decision point.
2. **Coil deepen.** From the hunting crouch the neck sinks a little
   deeper into the S and the body rocks subtly forward over the feet —
   loading the hinge [3][4][11]. Short: the bird was already coiled.
3. **Loaded hold.** Full coil, absolute stillness, gaze nailed. This is
   the held anticipation the craft brief demands — and it is what the
   animal actually does before firing.
4. **Release.** The hinge straightens; the head accelerates along the
   unfolding arc — "starts off apparently slow, then extends really,
   really fast" [3]. At real speed the extension is on the order of a
   blink; bill-tip speeds in ardeids are reported above 2.5 m/s
   [Uncertain — secondary summary, §12]. At 24 fps the whole release
   must live in **4 frames**, with accelerating spacing and one smear
   frame (craft brief item 3).
5. **Bill opens, then contact.** The bill opens ~1/30 s before impact —
   i.e. on the **final approach frame** at 24 fps — and closes on the
   prey: a grab, not a stab [6].
6. **Withdrawal.** Head and prey come back up out of the water on a
   decelerating rise, ~0.5 s; water sheets off; the neck re-coils as it
   rises. On a miss, withdrawal is empty and is followed by a small
   head-shake and an immediate return to the loaded hold (the bird
   simply waits again).

**What v1.1 does vs what the animal does.**
- v1.1 coil **leaks**: `neck_coil` goes 1.0 → 0.92 over the 0.55 s
  before release while the body rocks forward — the load visibly drains
  (craft brief item 2 flags the same frames). The animal holds the coil
  *at* depth.
- v1.1 extension keys run strike_t−0.09 s → +0.03 s and interpolate
  through the rig's generic easing; spacing is roughly even. The
  animal's spacing is violently back-loaded: most of the distance in
  the last frames.
- **v1.1's bill cannot open at all** — there is no gape parameter; the
  fish is speared by a closed dagger by construction, then simply
  *appears* at f+0.30 s. Half the "messy eating" complaint starts here.
- v1.1 withdrawal is the same easing curve played politely back; the
  fish pops into `held` at a fixed angle hanging off the beak tip
  (see §6).

**The v1.2 answer** (chart: `strike`): 12 frames coil-deepen (last 4
frames settle *deeper*), 12 frames loaded hold (beak-tip movement
≤1 cell), 4 frames release with spacing 25/35/30/contact + smear on
frame 3, `beak_open` ramps on frame 3 and closes on contact frame 4,
12 frames withdrawal with the catch. Miss = one discrete variant,
identical until contact.

---

## 4. The stalk and the step cycle — why the legs read clunky

**The animal.** Stalking is "excruciatingly" slow: the bird lifts each
foot *deliberately, to avoid creating ripples*, places it, and freezes
again [2][11]. The sequence inside one step, from the anatomy (§1):

1. **Weight commit.** All weight settles onto the stance leg. The body
   does not bob; if anything it lowers a fraction and locks.
2. **Lift — the fold.** The free leg folds at the **ankle
   (intertarsal joint)**: the tarsometatarsus rotates up/back under
   the shin so the foot tucks close beneath the leg, toes hanging/
   pointing down. The foot rises **just clear of the surface** — a
   stalking heron lifts centimetres, not decimetres; a high lift
   makes splashes, silhouettes, and noise.
3. **Advance.** The folded leg swings forward *low*, toes trailing
   down, passing close under the body. The femur/knee do most of the
   reaching inside the plumage; externally the shin tilts forward and
   the folded foot travels beneath it.
4. **Place.** The foot unfolds late, comes down **toe-first**, and
   sets onto the bottom with the toes spreading as weight arrives.
   Placement is the delicate part — it takes as long as the swing.
5. **Body passes over.** Only now does the body translate forward,
   over the newly planted foot — and the **head does not translate
   with it**: the neck absorbs the advance so the head stays locked in
   space (the translational-saccade hold [10]), until the head itself
   makes a quick thrust to its next fixation point.
6. **Freeze.** Between steps, frequently, complete stillness. The
   step–freeze rhythm *is* the stalk.

**What v1.1 does vs what the animal does.**
- **The foot lifts 21 design units** (`fy` 86 → 65 at mid-swing) —
  nearly a quarter of the frame height. That is a marching-band step.
  It is the single biggest "clunk" in the walk.
- The swing is a **sine arc** (`sin^0.85`): up and down symmetric, foot
  carried flat at full width — the "boot" the v1 report admits. The
  real swing is a **fold**: ankle flexes, foot tucks, profile slims.
- The body **never stops**: `root_x` smoothsteps continuously and
  `root_y`/`body_tilt`/`neck_sway` ride sines phase-locked to the
  gait, so the head surfs along with the body. The animal's head is
  spatially locked while its body walks underneath it [10].
- Duty factor 0.62 with a fixed 1.6 s cycle and **no freezes at all**:
  a metronome march at constant tempo. The animal's tempo is
  step … freeze … step, and the freezes are where the hunting happens.
- Both legs IK with the same pole; the fold direction at the ankle is
  whatever the IK solver finds, not an authored fold.

**The v1.2 answer** (chart: `step_cycle`): one canonical 24-frame step
(12 frames of it the fold-and-place, authored), body advance tied to
the *planted* phase only, head-lock compensation authored as a neck
counter-track against `root_x`, foot lift capped at ~7 units, toes
down in swing (`leg_*.toe`, new). The freeze is **not in the cycle** —
it is the scheduler holding the idle between steps, which is exactly
Jimmy's axiom: the cycle stays perfect; the *scheduling* varies.

---

## 5. Head movements and the alert

**The animal.** All head motion is saccade-and-fixate [9][10]: a
2–4-frame snap (at our frame rate), then a fixation that can last
seconds; the head may roll sideways for glare [3]; blinks are
2–4 frames. A startle/alert is the same system at body scale: the
neck uncoils upward fast, the bird goes tall and *freezes*, gaze
locked on the disturbance — herons flush or freeze by species habit,
and the freeze is a held pose, not a ramp.

**What v1.1 does vs what the animal does.** `alert_clip` eases
`body_tilt` to −39° over 0.28 s and holds it with sine micro-motion
scaled to 0.22 — a smooth rise into a wobbling freeze. There is no
anticipation check, no snap, no settle (craft brief item 9). Idle
head turns slide (§2). `look_back` snaps the whole head drawing in
one frame — a saccade's *speed* with none of its *drawing* (no
intermediate orientation).

**The v1.2 answer** (charts: `alert`, `head_saccade`, `head_turn`):
takes built on the craft formula — 4-frame check/dip, 3-frame snap,
36-frame held accent, 18-frame settle — and head motion everywhere
rebuilt as saccades through the yaw orientations (§8): the head's
turn is *drawn* through 3/4 views in 3–6 frames, never slid and
never flipped.

---

## 6. Eating the fish — the full handling sequence (Jimmy's point 1)

This is where v1.1 is most wrong, so it gets the most space. The real
sequence after the grab, assembled from field accounts [7][12][13][14]:

1. **Secure.** The fish comes up **crosswise** in the bill, alive and
   thrashing. The heron gives it a few quick **shakes** — killing/
   stunning it and shaking off water and slime. (For large or spiny
   prey it may stab it again, or drop it in the shallows and re-grab
   it [7][14].)
2. **Dip (common, esp. larger fish).** The fish is **dunked back in
   the water** once or twice — washing off slime/debris and wetting it
   for the swallow [12]. ("Often dipped" per the task brief's field
   literature; frequency varies — graded [Probable].)
3. **The toss-flip.** The decisive move: with a flick of the head the
   fish is **released, tossed into the air, and re-caught** — rotated
   in flight so it comes down **head-first into the bill**, head
   pointing toward the throat [12][13][14]. This may take several
   tosses for a big fish; the St. Marks account describes repeated
   juggling until "the fish's head and tail were lined up for
   swallowing head-first in order to avoid the sharp tips of its
   fins" [7].
4. **Work it back.** Small jerking movements of the head walk the
   fish **down the bill toward the gape** — the fish is re-gripped
   progressively closer to the head, still head-first [7].
5. **Head back, neck up.** The heron tips its head back and
   straightens the neck toward vertical, letting gravity help [7][13].
6. **The swallow.** The fish slides down the gullet and you can
   *watch it go*: "the heron's neck had a large bulge… the heron
   stretched its neck, moved from side to side and the bass slid
   down. The bulge in its neck was gone" [7]. The elastic neck expands
   around the prey; the bulge **travels** from gape to body over a
   second or more, sometimes with visible shimmying [3][7].
7. **Settle.** A few beak-claps and swallowing motions, sometimes a
   drink (dip, point bill skyward, let water run down [13]-account),
   then the neck re-coils and the statue resumes.

**What v1.1 does vs what the animal does.** v1.1's entire handling is:
fish appears at the beak tip at a fixed angle → pendulum sway
(decaying sine — the one good ingredient) → a corpus-builder "toss
patch" teleports it through an arc → `fish_slide` slides it *along
the beak and into the face* over 0.45 s → fish deleted at gulp+0.5 s.
There is **no head-first reorientation** (the fish goes in at whatever
angle, visually sideways), **no dip, no work-back, no head-back, and
no traveling bulge** — the neck is inert while its contents teleport.
"Messy" is exact: five of the animal's seven phases are missing and
the two present are faked with slides.

**The v1.2 answer** (chart: `swallow`, two discrete variants — tiny
and big): every phase above, in order, at exact frames. New rig
support it requires (§11): `fish_orient` (the fish's alignment state:
crosswise → aligned head-first), `fish_grip` (position along the bill,
tip→gape — generalizing today's `fish_slide`, which slides position
without orientation), a true free-fish ballistic arc during the toss
(the rig already has `fish_x/fish_y/fish_free_ang` — the toss must be
*authored in the chart*, not patched by the corpus builder), and
`neck_bulge_pos`/`neck_bulge_amp` so the swallow is drawn traveling
down the neck while the fish itself is already inside.


---

## 7. Takeoff, flight, landing

**Takeoff — the animal.** From standing: a crouch, then a leap driven
by the legs *and* the first huge downstroke together — the downstroke
begins as the feet leave (or just before) [Canonical staging of a
documented coupling; cf. craft skill]. Two details v1.1 misses: on
liftoff the heron "sticks its neck straight out and then tucks it
back against its body in an S-shape" [15] — the fold is a *second*
beat, not the first — and the long legs **dangle** below the rising
body before swinging back to trail [1].

**Flight — the animal.** Slow, deep wingbeats — canonical **2.0 Hz**
(range ~1.8–2.4 across accounts [Probable]; Cornell says only "slow,
deep" [1][16]); cruise ~20–30 mph [16]; neck folded into the tight S
with the head drawn back to the shoulders; legs trailing **straight
behind, extending well beyond the tail** [1]; short glides
interspersed ("may glide for short distances" [16]; longer soaring
occurs at altitude but is not our shot). Downstroke is the power
stroke and the shorter half of the cycle; wingtips lag the root —
the wing bends through the beat (craft skill, from general flight
mechanics [Probable]).

**What v1.1 does.** `flap = 58·sin(2π·2.1·t)`: a 2.1 Hz **pure sine**
— equal halves, full amplitude from the first frame, no tip lag, no
glide, and it starts the instant `flying` flips. v1.1 did fix the
neck (fold blend) and legs (stream lines) — both stay. But the neck
folds *immediately* (no extended-neck liftoff beat) and the legs
animate straight to their trailing targets.

**Landing — the animal.** Descent in "circular sailings" (Audubon,
via [17]); legs **lowered and dangled well before touchdown** [1];
final approach is a braking flare — wings high, body pitching up —
then the feet meet the water/ground, the legs absorb, and the bird
often takes a small step or two to kill the momentum; the neck
unfolds from its S *after* the feet are planted, not before.

**What v1.1 does.** A flap frozen mid-sine at touch−0.3 s, wings
folding on a 0.5 s clock schedule, legs swinging down in the last
0.7 s (they do reach forward — keep), root overshoot +0.8 → −0.4
(keep — it's the right shape), plume decay (keep). Craft brief item 5
covers the fix; the chart in the YAML now also restores the
**dangling-legs approach** and the post-touch step.

**The v1.2 answer** (charts: `takeoff`, `flight_cycle`, `glide`,
`landing`): flap as an authored 12-frame cycle (5 frames down /
7 up) with `flap_tip` lagging 2 frames; amplitude envelope across
the takeoff (3 deep beats → cruise beats); the cruise cycle is a
**looping signature** the scheduler can repeat and interrupt with
the glide cycle — again, variety from scheduling, not from a sine
generator.

---

## 8. THE TURN — drawn progressively, or not at all (Jimmy's hard rule)

**The rule.** "If it is going to turn around the animation has to
draw it progressively, not flip the bird card over." No squash
sweep (v1/v1.1's `turn_clip` is literally an idle clip plus a
corpus-builder horizontal squash 1→−1), no mirror-flip, no
single-frame head swap (`look_back`'s threshold flip is the same
sin, smaller).

**How the real bird turns.** A standing heron turns the way birds
do everything visual: **gaze first**. The head saccades to the new
direction in a few frames — far faster than the body can follow
[9][10]. The body then rotates **on stepping feet**: a series of
short pivot steps, each foot re-placed a few degrees further around,
the body yawing continuously and more slowly beneath a head that is
meanwhile **held stable in space** — the head counter-rotates
against the body so the gaze stays nailed to the target until the
body arrives, then head and body realign [9][10]. Nothing in the
animal teleports, mirrors, or squashes; the rotation is *walked*.

**The drawn solution (the v1.2 rig contract).**
1. **A real `yaw` parameter** on the body (0–180°) and `head_yaw`
   relative to it. The rig must *draw* yaw, not fake it: body width
   narrows with cos(yaw), the tail swings to the far side, the neck
   base crosses the body midline, near/far legs exchange roles at
   90°, the folded-wing patch migrates across the body, the far eye
   appears at front view. This is pose-to-pose drawing in pose
   space: five **authored orientation stops** — 0° profile,
   45° three-quarter, 90° front, 135° three-quarter, 180° profile —
   each passing the filled-silhouette test, with the rig
   interpolating part positions between stops (never scaling a
   finished drawing).
2. **Choreography** (chart: `turn`): frames 0–3 head saccade to
   target; frames 4–66 body yaws through the stops on 4 short pivot
   steps (one per ~15 frames, using the step fold of §4 at small
   radius), head counter-stabilized so its world yaw stays on
   target; frames 60–72 head/body realign + settle (plume lag).
   Total 72 frames (3.0 s). Silhouette area within ±5% of idle on
   every frame — the anti-squash gate, carried over from craft
   brief item 8.
3. **Head-only turns** use the same machinery at neck scope:
   `head_yaw` travels through its own 3/4 stops in 6 frames
   (`head_turn` chart). `look_back` is retired as a rig concept:
   looking back is head_yaw ≈ ±150° **drawn**, with the neck
   curving — never a flag that flips the head drawing.

---

## 9. Rest: one leg, doze, and the tucked foot

**The animal.** One-legged rest is thermoregulation and rest: the
free leg is **drawn up and tucked into the belly feathers**, foot
held against the warm body — folded at the ankle, tarsus up under
the body, not vanished [18][19]. Grey Heron sleep posture (field
study): neck folded in an S with the nape against the back, head
horizontal, bill resting against the neck; daytime sleep is
intermittent, eyes opening/closing every few seconds [20]. GBH rest
similarly with neck retracted and head drawn back over the
shoulders [18].

**What v1.1 does.** `hide_near` fades the near leg **out of
existence** over 0.4 s (a flag threshold at 0.5: present, present,
gone) and the body drops 0.9 onto the remaining leg. A leg that
ceases to exist is the "clunky" complaint in its purest form.

**The v1.2 answer** (chart: `oneleg`): enter over 36 frames — weight
shift (12), free foot lifts and **folds up visibly** (24) ending
tucked forward under the belly, toes curled, still drawn; the hold
is an idle variant; exit is the same chart reversed *as authored
keys*, not a fade. Doze (chart: `doze`) is its own pose per §2:
neck fully retracted, head low and resting, long slow blink cycle —
never a damped awake idle.

---

## 10. Wing stretch and preen

**The stretch — the animal.** The canonical bird stretch, described
for GBH in the Kingbird ethogram and for Grey Heron in the field
study [21][22]: weight shifts to one leg, head/neck settle into the
tucked "perched" position, then the **wing and leg of the same side
extend together** — wing down-and-out with feathers fanning, leg
extended **back** until the segments align, toes stretching. Held
5–15 s in the Grey Heron observations [22]. A second GBH form
extends the neck fully and raises both wings above the horizontal
[21] (the "warble" of photo accounts).

**What v1.1 does.** A single wing slab rotates up-back on
`wing_amt` over 0.8 s, holds, returns. No leg, no weight shift, no
fan, no hold worth the name.

**The v1.2 answer** (chart: `stretch`): the same-side wing+leg
form, 168 frames (7 s) with a 48-frame full-stretch hold. The
two-wing neck-up form is variant B (120 frames).

**Preen — the animal.** Preening is nibbling: the bill works along
individual feathers, drawing them through the mandibles to re-zip
the barbs; sessions are bouts of short nibble bursts separated by
pauses and repositioning [23]. Heron specifics: the chest's
**powder down** is combed with the **pectinate (fringed) middle
claw** and worked into the plumage like a washcloth to remove fish
slime; the preen gland is vestigial in herons — powder, not oil, is
the medium [24][25]. Head-scratching is done by bringing the leg
straight up while the head lowers to meet it (documented in heron
maintenance ethograms [26]).

**What v1.1 does.** Nothing — no preen clip exists (both reports
admit it); craft brief item 10 specifies the cartoon version.

**The v1.2 answer** (charts: `preen`, `scratch`): pose-to-pose
bouts — reach (24f), nibble beats of 8 frames separated by 16-frame
holds, one feather drawn through the bill (20f), a wing half-opened
and nibbled under, a whole-body shake with ≥8 frames of plume
follow-through. The foot-comb chest beat goes in variant B as the
species-signature detail (foot raised to the chest, head down to
meet it — drawn carefully, it's the most heron-specific maintenance
move there is).

---

## 11. What the v1.2 rig must gain (flags for the build)

**New pose parameters** (in addition to the current vocabulary in
`great-blue-heron/species.yaml`):
- `yaw` — body orientation 0–180°, drawn (§8). **The big one.**
- `head_yaw` — head orientation relative to body, drawn through
  its own 3/4 stops; replaces `look_back` (retire the flag).
- `head_roll` — sideways cock of the head (glare/scan) [3].
- `beak_open` — gape 0–1; opens pre-contact in the strike, works
  the fish in handling, claps in the settle (§3, §6).
- `fish_orient` — fish alignment: crosswise ↔ head-first (§6).
- `fish_grip` — grip point along the bill, tip→gape (generalizes
  `fish_slide`, which moves position without orientation) (§6).
- `neck_bulge_pos`, `neck_bulge_amp` — the traveling swallow
  bulge (§6).
- `flap_tip` — wingtip flap angle, lagging `flap` (root) (§7).
- `leg_near.toe`, `leg_far.toe` — toe pitch: pointed/trailing in
  swing, flat at plant, curled in the one-leg tuck (§4, §9).

**Rig capabilities:**
- A **yaw-aware drawing path**: part placement as a function of
  yaw with five authored stops (§8); silhouette-area gate ±5%.
- The fish drawn from `(grip, orient, free-arc)` state in *all*
  phases — no corpus-builder toss patch; the toss is chart data.
- The neck tube accepts a **localized bulge** at `neck_bulge_pos`.
- Smear drawing at peak strike extension (already brief item 3).

**Corpus note:** v1.1 banked frame-aligned pose data
(`corpus11_poses`) — but in the *old* vocabulary (no yaw, no gape,
no bulge). It can seed nothing about the new mechanics; treat it as
v1.1's record, not v1.2's foundation.

---

## 12. Training implications — a small canon, scheduled well

Per Jimmy's axiom (§0), v1.2's corpus is **not** a distribution to
sample. It is a **canon**: a small set of authored cycles, each
admitted only after passing its quality gates, played verbatim.

**What the corpus should contain** (counts from `movement-charts.yaml`):
- ~20 clip instances total, ≈ 7,500 frames — against v1.1's
  43,936 frames of seeded variation. Fewer frames, every one of
  them checked.
- Per behavior: 1 canonical cycle + at most 2 discrete variants,
  where a variant differs in *script* (event order, direction,
  size class) and never in noise. Variants are authored and
  gate-checked individually, exactly like the canon.
- Loops must loop: step cycle, flight cycle, and glide return to
  their exact first pose (frame-exact loop points in the charts),
  so the pose-space model learns *cycles*, and the player can hold
  or repeat without drift.

**What the pose-space model must learn vs what stays authored.**
- *Learned:* the trajectory shapes of the canonical cycles and the
  transitions between them (idle→strike, stand→flight), in pose
  space, so playback can blend at cycle boundaries without melting
  (the portrait-v2.1 lesson: ride recorded trajectories, no
  straight-line latent cuts).
- *Authored, never learned:* the charts themselves (every key and
  frame budget), the yaw stops, the smear frames, the ink events,
  and all holds. A hold is a pose repeated — the model should learn
  that stillness is a destination, not interpolate through it.
- *Scheduling is the variety engine:* the behavior layer decides
  which cycle, in which zone, after how long a hold, tiny or big
  fish. Hold *durations* may stretch (repeating a held frame is not
  regenerating motion); motion itself never stretches.

**Quality gate per cycle** (before admission to the corpus):
silhouette test at every authored stop; spacing audit on the
tracked point named in the chart; held-fraction on idles; the
turn's ±5% area gate; fish-orientation readable in a freeze frame
at the swallow (head-first or the clip fails); loop-point pose
distance = 0 for cycles.

**Reference data that would most improve fidelity, if Jimmy wants
to go further:**
1. **Phone slow-motion from the dock/boat** — GBH are regulars on
   St. Leonard Creek (BirdNET has logged the species at the house).
   120/240 fps clips of (a) a strike, (b) a full catch→swallow,
   (c) 30 s of stalking, shot side-on at bird height, would convert
   every [Canonical] sub-second number in this study into a
   measured one. Even 3–4 good sequences beat any literature for
   *our* bird in *our* light.
2. **Frame-stepped public footage** (Cornell Macaulay Library hosts
   GBH video): a dedicated pass stepping through a swallow and a
   turn frame by frame would verify the toss rotation direction
   and the turn's step count, the two least-documented mechanics
   here.
3. Later, if wanted: pose-estimation (SLEAP/DeepLabCut-style) on
   that footage to extract joint tracks directly into chart keys —
   a phase-2 luxury, not a v1.2 dependency.

---

## 13. Honesty notes — what could not be verified

- **No frames were sampled from slow-motion footage in this pass.**
  All sources were text (Cornell, Audubon, journal articles,
  ethograms, field accounts). Sub-second phase timings (strike
  extension, toss airtime, saccade duration at 24 fps) are
  [Canonical] animation values consistent with the qualitative
  literature, not measurements.
- **Strike ballistics numbers** (bill-tip >2.5 m/s, ~50 m/s²) come
  from a single secondary summary of ardeid kinematics work and
  are graded [Uncertain]; the primary hinge mechanism itself is
  solid [3][4].
- **Wingbeat 2.0 Hz** is [Probable]: every source agrees on "slow
  and deep," and 1.8–2.4 Hz is the commonly reported band, but no
  primary kinematic paper for *A. herodias* was located in this
  pass (one encyclopedia's "25 beats/minute" is an outlier and was
  disregarded).
- **Dip-the-fish frequency** ("often") is [Probable] — attested in
  field accounts, not quantified.
- **Turn step count (4 pivot steps / 180°)** is [Canonical]: the
  gaze-first, body-walked-around mechanism is documented [9][10];
  the exact step count for a standing GBH was not found in the
  literature and should be the first thing checked against real
  footage (§12).
- The Grey Heron material (sleep, stretch timing) is a close
  congener (*Ardea cinerea*) used where GBH-specific sources were
  silent, and is flagged where used.

## Sources

1. Cornell Lab of Ornithology, *All About Birds* — Great Blue Heron
   identification & overview: specially shaped neck vertebrae;
   statue-like hunting; in flight neck in tight S, legs trailing
   well beyond tail, "very slow wingbeats."
   https://www.allaboutbirds.org/guide/Great_Blue_Heron/id
2. Audubon's GBH coverage / natural-history accounts of the stalk:
   feet lifted deliberately to avoid ripples; minutes motionless.
   (via search-surfaced accounts; see also [11])
3. Audubon Magazine, "More Than You Ever Wanted to Know About Heron
   Necks" — Clay Green (Texas State) & Peter Frederick (Florida):
   the 6th-vertebra hinge/atlatl; "starts off apparently slow, then
   extends really, really fast"; Krebs & Partridge head-tilt;
   reef-heron refraction correction within 0.1 s.
   https://www.audubon.org/magazine/more-you-ever-wanted-know-about-heron-necks
4. "The Peculiar Necks of Herons and Anhingas," *Integrative
   Organismal Biology* (2026), PMC — specialized mid-neck vertebrae
   for rapid neck straightening in ambush predation.
   https://pmc.ncbi.nlm.nih.gov/articles/PMC13014071/
5. van Grouw (2013), *The Unfeathered Bird*, via the woomera/heron-
   neck analysis: 6th vertebra elongated, pivots on the 7th; the
   kink trades lateral movement for strike speed.
   https://www.paperbarkwriter.com/is-an-aboriginal-woomera-like-a-herons-neck/
6. *The Science of Birds* podcast, GBH episode: ~20 cervical
   vertebrae; bill opens ~1/30 s before impact; grab > impale.
   https://podscripts.co/podcasts/the-science-of-birds/great-blue-heron
7. Friends of St. Marks NWR, field account of a GBH eating a
   foot-long bass: shook loose, dropped & re-grabbed, juggled until
   head-first "to avoid the sharp tips of its fins," head-swinging
   work-back, visible neck bulge traveling down.
   https://stmarksrefuge.org/blog/great-blue-herons/
8. Standard avian anatomy (digitigrade stance; intertarsal joint =
   ankle; knee hidden, bends forward; tarsometatarsus).
9. Kress, van Bokhorst & Lentink (2015), "How Lovebirds Maneuver
   Rapidly Using Super-Fast Head Saccades…," *PLOS ONE* — saccade
   speeds, stabilization between saccades, body rotates continuously
   beneath a stabilized head.
   https://pmc.ncbi.nlm.nih.gov/articles/PMC4481315/
10. Land (2018), "The Evolution of Gaze Shifting" — saccade-and-
    fixate across vertebrates; translational saccades (head-bobbing)
    in walking birds: head holds in space while the body walks
    under it.
11. Chesapeake Bay Foundation, "The Stalkers" — coil, stand
    motionless, strike; flight ~30 mph, neck coiled, legs trailing.
    https://www.cbf.org/resources/june-the-stalkers-great-blue-herons-and-their-kin/
12. Steve Creek Wildlife Photography — GBH tossing fish/tadpole:
    repeated tosses to reposition prey head-first before swallowing.
    https://stevecreek.com/great-blue-herons-tossing-fish-a-photographers-delight/
13. Central Ohio Metro Parks, "How to eat fish? Great blue herons
    have an answer" — stab, flip, swallow headfirst so fins don't
    catch in the throat.
    https://www.metroparks.net/blog/how-to-eat-fish-great-blue-herons-have-an-answer/
14. Field Notes (discovering-nature.net) — catch carried slowly to
    shallows, reoriented, head tipped up, swallowed; then dips for
    water and points bill skyward.
15. Way of Life, GBH account — on getting airborne the neck sticks
    straight out, then tucks back into the S; cruise 20–25 mph.
    https://www.wayoflife.org/reports/great_blue_heron.php
16. Cornell Lab GBH life history (via historicalechoes mirror) —
    grab small prey / impale larger, shake to relax spines; legs
    dangled when preparing to land.
17. Audubon, *Birds of America* (Wikisource) — landing descent in
    "circular sailings"; measured, regular steps while stalking.
18. One-legged rest / sleeping posture accounts (thermoregulation;
    tucked leg against the body; S-neck sleep) — general avian +
    heron sources via search.
19. Revell Photography, "Why Do Birds Stand on One Leg?" —
    one-legged stance: tucked foot, counter-current exchange,
    locked-joint steadiness.
20. Grey Heron individual behavior study, *J. Phys.: Conf. Ser.*
    1116 (2018) — sleep posture (S-neck, nape to back, bill on
    neck); body-care repertoire.
    https://iopscience.iop.org/article/10.1088/1742-6596/1116/5/052035/pdf
21. *The Kingbird* — GBH maintenance ethogram (Parker & Maxwell,
    via Black-crowned Night Heron literature): two stretch methods;
    same-side wing+leg; bill cleaning with pectinate claw.
22. Grey Heron study [20] — stretching 5–15 s per movement; wing,
    tail fan, head turn same direction, then leg/toes same side.
23. General preening mechanics (feather drawn through bill to
    re-zip barbs; bouts with pauses) — standard ethology.
24. Cornell Lab GBH facts (via species spotlights) — powder down
    on the chest combed with the fringed middle claw, used like a
    washcloth against fish slime.
25. NEBRASKAland / Colby Maine Birds — herons' powder down most
    extensive in waders; preen gland vestigial in herons.
26. Maxwell & Putnam (1968), "The Maintenance Behavior of the
    Black-crowned Night Heron," *Wilson Bulletin* — scratching:
    leg brought straight up, head lowered to meet it; stretch
    sequence (weight shift, head tucked, wing down-out, leg out).

*Frame budgets for every behavior named here: `movement-charts.yaml`.*
