# Heron Behavior Deep Dive — ethology + mimicry design for the creature engine

*Written 2026-11-03 (overnight learning track B, Jimmy's directive 2026-11-03
00:09: "mimicking animal behavior, deep dive on heron behavior and movement").*

*Purpose: extend — not repeat — `heron-movement-study.md` (2026-11-02) and
`movement-charts.yaml`. The movement study is the anatomy/timing foundation
and remains in force. This document adds what it lacked: **proportions,
frequencies, daily and seasonal structure, social signals, two missing
behaviors, and the scheduling mathematics** that turn a chart canon into a
believable animal. Grading follows the study's convention: [Documented] =
a source in §5 states it; [Probable] = consistent across sources, no
species-specific measurement; [Estimate] = our design number derived from
graded facts; [Canonical] = an authored animation value.*

*Headline findings, for the impatient: (1) the real bird strikes about
**4 times an hour while hunting** and succeeds **~56%** of the time — our
proposed device pacing is hotter and more accurate than the animal;
(2) "herons spend 90% of waking hours hunting" is unsourced folklore —
the one real GBH time budget found puts hunting at **30–50%** of the day;
(3) after any strike, hit or miss, the bird **relocates** before hunting
again — our charts return to idle in place, and that is a visible lie;
(4) we are missing the **body shake** as a standalone behavior and the
hot-day **gular-flutter / delta-wing** posture entirely.*

---

## 1. Verified behavior facts (with corrections to the movement study)

### 1.1 Hunting modes and their proportions

- **Two modes dominate to near-exclusion.** Across studies, Great Blue
  Herons forage "almost exclusively" by **Stand and Wait** and **Walk
  Slowly**; the more energetic ardeid tactics (running, open-wing,
  canopy) belong to other species (Reddish Egret, Tricolored Heron)
  [Documented — Hodgens et al. 2004; Kent estuarine assembly study,
  Tampa Bay 1975–79]. Our roster is right to have no chase behavior.
- **Within a hunt, standing dominates walking.** Focal sampling at two
  San Juan Island sites found herons "spent most of their time standing
  and walking slowly," with standing the larger share [Documented —
  UW San Juan strike-rate study, abstract]. No clean published
  percentage split for GBH was found; treat **stand:walk ≈ 70:30 to
  85:15 of hunting time** as [Estimate] from the qualitative record.
- **Step rate while stalking is very low.** The White-bellied Heron
  (a large *Ardea* congener) hunted at a mean of **4.03 steps/min**
  [Documented — RSPN monograph, citing its own field data]; general
  texts give herons "≤60 paces/min" as an upper bound, not a norm
  [Documented — Meyerriecks via Wikipedia]. Our step cycle with
  scheduler freezes is compatible; the design number to hold in mind
  is **single-digit steps per minute, in bursts separated by freezes**
  [Estimate].
- **Foraging speed reference (congeners):** Great Egret foraging
  speed ≈ **0.04 m/s**, Snowy Egret ≈ 0.13 m/s [Documented — Kent].
  A GBH stalk is a near-zero-velocity behavior with occasional steps,
  not a slow continuous walk. This validates the charts'
  step–freeze–step structure and forbids any "cruise walk" state.
- **Most captures happen in very shallow water:** 86.9% of successful
  captures at depths ≤20 cm [Documented — Hodgens et al. 2004].
  Device translation: the bird should hunt where our scene reads
  knee-deep-or-shallower; deeper-water strikes are the exception.

### 1.2 Strike rates, success, and what follows a strike

- **Strike rate ≈ 4 strikes/hour of foraging observation** (828
  attempts in 202 h of monitored foraging, Arkansas tailwaters)
  [Documented — Hodgens et al. 2004]. Site quality moves this a lot:
  prey-rich rocky shore birds struck more often than tidal-flat birds
  [Documented — UW San Juan]. Design band: **one strike per
  10–20 min of active hunting** [Estimate].
- **Strike success ≈ 56%** overall (467/828) [Documented — Hodgens];
  Krebs (1974) measured ~41% capture success for solitary adults on
  intertidal fish; one exceptional bird in deep water took 28 of 31
  (~90%) [Documented — Godin 1977, citing Krebs]. Success varies
  with tide phase, depth, and site (San Juan: higher success behind
  the tideline and in deeper water, and during higher/flood tides in
  one study; more strikes but lower success on the ebb in another) —
  **site-dependent, do not hard-code a tide→success rule**; a mild
  tide→strike-*rate* effect is defensible [Probable].
  → **Correction to our pacing assumptions:** the presence contract's
  ~75% fishing success is too kind. The animal misses nearly half
  the time. `strike_miss` must be a first-class, common outcome
  (~40–45% of strikes), not a rare variant.
- **Post-strike relocation [CORRECTION — missing from our charts].**
  "After a strike, successful or not, herons often walk quickly away,
  generally more than 2–3 m, before resuming a stealthy search"
  [Documented — Warrick 1992, Oregon thesis]. Our swallow chart ends
  by returning to `idle_hunt` **in place**. The animal doesn't: the
  strike advertises the spot and disturbs the prey field, so the bird
  moves. Add a `relocate` beat after swallow/settle and after a miss:
  a short sequence of **brisk** steps — notably, the one fast walk in
  the repertoire — to a new stand, then stealth resumes. This also
  gives the scheduler a natural, *caused* reason to change thirds on
  the device.
- **Prey size reality check:** 87% of captured prey ≤14 cm long
  [Documented — Hodgens]. Our tiny:big fish ratio should be heavily
  tiny-dominant; the big-fish struggle variant is a rare event
  (~1 in 8 catches) [Estimate from the size distribution].

### 1.3 The daily rhythm

- **Crepuscular emphasis, not crepuscular-only.** GBH are most often
  seen hunting at dawn and dusk [Documented — Cornell via Oneida Lake
  account; multiple naturalist sources], feed by day, and feed at
  night opportunistically — rod-dense retinas support low-light
  hunting, especially under moonlight or near artificial light
  [Documented — Cornell]. They are **not** nocturnal specialists:
  the night default is roosting/dozing, with hunting as the
  moonlit exception [Probable].
- **Midday is maintenance-and-loaf time.** The consistent field
  picture: a midday bird on a log or bank, preening, stretching,
  resting — hunting resumes toward evening [Probable — consistent
  across naturalist accounts; White-bellied congener showed a
  bimodal morning-weighted activity pattern, Documented for that
  species].
- **Tide can override clock.** In tidal habitat, foraging tracks
  water level (prey concentrated in shallows) at least as much as
  time of day [Documented — UW San Juan; Chesapeake naturalist
  sources]. Our creek is tidal: the scheduler should take the tide
  band as a first-class hunting-probability input alongside light —
  it already computes tide for the plates, so this is free.

### 1.4 The time budget — and a folklore correction

- **The only real GBH activity budget located:** Brandman (1976),
  cited in the White-bellied Heron monograph: GBH spent **30–50% of
  time hunting** [Documented, secondhand citation]. Comparators:
  Goliath Heron 58% hunting (Mock & Mock 1980); White-bellied Heron
  72.5% foraging / 23.1% roosting / 1.6% bathing / 1.5% preening in
  a November sample [Documented, congener].
- **"Herons spend ~90% of their waking hours hunting"** circulates
  widely (NEBRASKAland-derived, repeated by dozens of sites) with
  **no citable study behind it**. Flagged as folklore; do not use.
  → **Scheduling consequence:** hunting is a *plurality* state, not
  the day. Resting/loafing and maintenance together rival it. A
  device bird that is always either hunting or asleep is wrong;
  the third state — awake, upright, doing nothing in particular,
  occasional maintenance — needs real schedule share [Estimate].

### 1.5 Maintenance behavior — bouts, order, and the missing shake

- **Maintenance behaviors come in bouts with a typical internal
  order.** The classic ardeid maintenance ethogram (Maxwell &
  Putnam 1968, Black-crowned Night Heron) lists preening, scratching,
  care of feet, **shaking**, stretching, bill-wiping, sleeping,
  throat pulsation, yawning as one repertoire. A GBH photo-documented
  sequence runs **stretch → shake → preen** [Documented — Henson
  photo account]. Our canon schedules `stretch` and `preen` as
  independent events; schedule them as a **bout**: stretch first,
  shake as the hinge, preen after, with the option of stopping early
  (a bout can be just a stretch) [Estimate, grounded in the order
  evidence].
- **The body shake is a distinct behavior, and we don't have it**
  [CORRECTION]. Maxwell & Putnam: the bird erects its contour
  feathers and "shakes vigorously while rapidly moving the wings in
  and out"; a shaking session lasts **5–10 seconds**. GBH accounts
  describe the whole body shaking "like a dog," plumes rippling,
  used after immersion, after flight, and to resettle feathers
  generally [Documented — Maxwell & Putnam 1968; A-Z Animals /
  photographer accounts]. Our charts embed a 12-frame shake inside
  `preen` and a settle inside `swallow` — both too small. Author a
  standalone `body_shake` at **120–240 frames (5–10 s)**: feather
  erection ramps first (the silhouette visibly puffs — a plume-law
  friendly event), 3–5 shake oscillations with wing in-out beats,
  then a settle where the plumage re-lays over ≥1 s. This is also
  the behavior Jimmy's local-bird clips show as the feather ruffle —
  the footage already agrees with the literature.
- **Yawning** is in the maintenance repertoire [Documented —
  Maxwell & Putnam]. A rare single-beat idle variant (bill opens
  wide, head tips) — cheap, characterful, exactly the kind of thing
  that reads as alive because it is *purposeless*. [Probable for GBH
  specifically; family ethogram documents it.]

### 1.6 Heat behavior — entirely missing from our canon [CORRECTION]

- **Gular flutter + drooped-wing cooling.** In hot weather a GBH
  stands with wings held out and drooped in a bowl/"delta"
  configuration, bill open, throat tissues visibly fluttering —
  evaporative cooling, the avian pant [Documented — Seagrove Walks
  field account with photographs; Volusia Naturalist; consistent
  secondary sources]. A related full **delta-wing sunning** posture
  (facing the sun, wings drooped into a dish) is reported for GBH
  since Audubon's era [Documented — multiple naturalist sources].
- Device translation: a **summer-midday signature** — trigger:
  season = summer AND light = full day AND (device-side temperature
  proxy: hot day). It is a *held posture with one continuous
  micro-motion* (throat flutter), a deliberate exception to the
  no-continuous-motion rule, justified because the animal's flutter
  is genuinely continuous. Needs `beak_open` held ~0.4 and a throat
  flutter treatment (new pose param or a neck-base micro track) —
  flagged as a rig item, like the bulge was.

### 1.7 Social signals (mostly colony — but one belongs on the creek)

- **Upright and Spread Wing display** — the foraging-ground threat:
  neck nearly fully extended and tilted slightly back, head and bill
  above horizontal, wings drooped away from the body (often
  asymmetric, near wing lower), body plumes erected, held a long
  time while slowly approaching a rival [Documented — Hancock &
  Kushlan, quoted in Feathered Photography's documented encounter].
  On a one-bird device it has no trigger — **until** the engine's
  multi-character work (heron↔fish is the seed; a second heron is
  the obvious growth). Bank it as the heron↔heron seed behavior;
  do NOT schedule it solo.
- **Territorial upright toward intruders generally:** feeding
  territories are defended with head-back, wings-out, bill-skyward
  approaches, "even toward people" [Documented — Cornell]. Device
  translation, carefully: a *person arriving* is a legitimate mild
  trigger for the freeze-tall alert (already have), never for the
  full display — the display is for rivals, not watchers.
- **Colony repertoire (context only; our bird is solo on a creek):**
  Stretch Display (neck up, bill skyward, plumes erected, then head
  lowered with a moan), Landing Call, Greeting Ceremony, bill-clap
  duets, stick transfer [Documented — Mock/Vennesland tradition via
  Birds Outside My Window; WBU]. The one exportable element: the
  **Stretch Display's plume-erection + bill-skyward silhouette** is
  a plausible rare solo echo in breeding season — but honest
  grading says it is a nest-site behavior. Recommendation: exclude
  from the creek roster; note as colony content if a rookery scene
  is ever built.
- **Alarm escalation is a ladder, not a switch** [Documented —
  Vennesland 2000, via call literature]: a slowly increasing
  disturbance first draws a low call; continued disturbance
  escalates to the harsh *frawnk*; the *Awk* scream (mean 2.3 s)
  belongs mostly to colonies. Posture translation for our silent
  bird: **freeze-tall first; only sustained/escalating disturbance
  → flight.** Our presence contract already suppresses flight
  while watched; the ladder justifies grading the alert: brief
  presence = gaze + neck-up check; sustained approach = full
  alert freeze; repeated provocation = the rare flush. The current
  single `alert` chart becomes step two of three.

### 1.8 Chesapeake seasonality for a resident creek bird

- **Year-round resident** in the Chesapeake region; the Bay hosts
  more than half the Atlantic coast's breeding population; birds
  leave only when ice locks up food [Documented — Inside Annapolis;
  CBF; VA parks]. Our device bird never migrates away for the
  winter — correct as designed.
- **Phenology (Chesapeake):** pairs form **March–April**; nesting
  **February–April** in Virginia accounts (eggs hatch ~28 days,
  young leave the nest ~60 days); colonies active through early
  summer; **post-breeding dispersal from late August**; northern
  migrants pass through from late September, locally raising heron
  density in autumn [Documented — NPN species account; Inside
  Annapolis; VA parks].
- **Device-relevant seasonal deltas:**
  - *Feb–Apr:* breeding plumage — elongated plumes, richer bare-part
    colors (an **art** note: plume mass grows; schedule unaffected).
    Plume erection displays belong to the colony, not the creek.
  - *May–Jul:* peak foraging demand (feeding young, offstage) —
    hunting share at its annual high [Estimate from breeding
    energetics; Documented that summer = peak foraging activity,
    Maryland spotter's guide].
  - *Aug–Oct:* dispersal season — the creek bird is joined/passed by
    strangers in reality; for the device, a slightly higher flight
    frequency and the season's one plausible second-heron glimpse
    [Estimate]. (Autumn is also when Jimmy's footage and the
    project's fall-first art already live.)
  - *Nov–Jan:* the quiet quarter — more standing, more one-leg
    rest, hunting compressed into the short day's best light; if a
    hard freeze came, the real bird would leave; our creek doesn't
    freeze on the device, so: longer dozes, lower event rates
    [Estimate].

### 1.9 Small confirmations and refinements (no correction, worth banking)

- **Foot-stirring** is a documented ardeid tactic (Meyerriecks 1966,
  *The Auk*) and feet are used for "vibrating water surfaces, raking
  litter and paddling" in family-level accounts — but **GBH-specific
  evidence is thin**. Status: keep out of the core canon; if used,
  a rare stalk variant flagged experimental [Probable, family-level].
- **Drinking** (dip bill, raise skyward, let water run down) is
  already in the movement study §6 as a settle option; promote it
  to a named roster beat after big fish and on hot days
  [Documented in study sources].
- **Defecation etiquette** exists (territorial birds leave the
  feeding spot — Science of Birds, from the primary literature)
  and is exactly the kind of fact the device should *know but not
  show*. Noted here only so nobody "discovers" it later as content.
- **Strike kinematics gap stands:** still no primary high-speed
  kinematic paper for *A. herodias* with frame counts. Popular
  accounts put the strike "under a fifth of a second"; secondary
  summaries repeat bill-tip >2.5 m/s and ~50 m/s² [Uncertain, as
  graded in the study]. The chart's 4-frame release at 24 fps
  (167 ms) remains a defensible [Canonical] value. Jimmy's future
  slow-motion dock footage is still the best fix, unchanged.

---

## 2. Proposed roster (signature-cycle terms)

Durations: cycle length from `movement-charts.yaml` where a chart
exists; new charts marked ◆. Frequency = design target for the creek
device, derived from §1 — [Estimate] unless noted. "Watched" rates
assume the presence contract's audience effect is wanted (see §3.4).

| Behavior | Chart | Duration | Frequency (unwatched / watched) | Triggers / conditions | Season |
|---|---|---|---|---|---|
| Hunt idle (stand-and-wait) | `idle_hunt` | 20 s cycle, held indefinitely | the default day state; bouts of 10–45 min | light = dawn/day/dusk; tide mid–low raises priority | all year; share peaks May–Jul |
| Stalk step | `step_cycle` | 1 s/step, freeze-gated | bursts within hunt bouts; single-digit steps/min [Doc.] | in hunt bout; repositioning | all year |
| Strike (catch) | `strike` + `swallow` | 2.2 s + 3.5–6.3 s handling | ~55–60% of strikes [Doc. 56%] | fish event in middle third; hunt bout active | all year |
| Strike (miss) | `strike_miss` | ~2.5 s + head-shake | ~40–45% of strikes | same as strike | all year |
| — strike rate overall | scheduler | — | 1 per 15–40 min unwatched; 1 per 4–12 min watched (audience rate, §3.4) | fish availability model; tide band low/mid ↑ | all year |
| Post-strike relocate ◆ | new (brisk step_cycle run) | 3–6 s | after ~every strike, hit or miss [Doc.] | completion of swallow or miss-shake | all year |
| Drink ◆ (roster promotion) | from swallow settle | ~4 s | after big fish; hot afternoons | big catch; summer heat | all year, ↑ summer |
| Maintenance bout ◆ (wrapper) | `stretch` → `body_shake` → `preen` | 7 s + 5–10 s + 10 s, early-stop allowed | 2–5 bouts/day; midday-weighted | light = day; follows long hunt bouts; after flight | all year |
| Body shake ◆ | new | 5–10 s [Doc.] | inside most maintenance bouts; standalone after flights/immersion events | bout hinge; landing; post-strike if soaked | all year |
| Preen | `preen` (+powder-comb variant) | 10 s/bout-segment | inside maintenance bouts | as bout | all year |
| Stretch | `stretch` (+warble variant) | 7 s (2 s variant form) | bout opener; occasionally standalone after long holds | long stillness preceding | all year |
| Scratch | `scratch` | 2 s | rare; inside preen bouts | bout context | all year |
| Yawn ◆ | new (single beat) | ~2 s | very rare; 0–2/day | doze edges, post-alert settle | all year [Probable] |
| One-leg rest | `oneleg` | 36 f enter + hold | daily; long holds, midday & cold mornings | rest state; low light or loaf context | all year, ↑ winter |
| Doze | `doze` | enter 4 s + hold | night default; midday naps rare | light = night; room-empty long | all year |
| Night hunt (moonlit) ◆ | `idle_hunt` + `strike` at night plates | bout 5–15 min | rare: only on brightest moon bucket (m3), a few nights/month | moon = m3 AND tide favorable | all year |
| Gular flutter / delta-wing ◆ | new held posture | holds of 1–5 min | hot summer middays only | season = summer AND full-day light AND hot-day flag | Jun–Aug |
| Alert (ladder step 2) | `alert` | 2.5 s + hold | on disturbance events | presence rising edge; sudden sound (mic kit) | all year |
| Freeze-check (ladder step 1) ◆ | head/neck micro-chart | 1–3 s | the common response; most presence events end here | any mild disturbance | all year |
| Takeoff / flight / landing | `takeoff`, `flight_cycle`, `glide`, `landing` | ~4 s + crossing + 5 s | 0–3 flights/day unwatched; suppressed while watched | long absence urge; ladder step 3 (rare flush); dusk reposition [Estimate] | ↑ Aug–Oct dispersal |
| Foot-stir ◆ (experimental) | stalk variant | ~3 s | very rare, if ever | shallow mid-tide stalk | all year [family-level only] |
| Upright spread-wing display | banked, not scheduled | held 10 s+ | never solo | second-heron event only (future multi-character) | territorial, any season |

---

## 3. Scheduling guidance

### 3.1 The stillness budget

The animal's own numbers, assembled: within a hunt idle, held
fraction ≥0.92 of frames (chart gate). Within a hunting bout,
standing:walking ≈ 70:30–85:15 [Estimate]. Across the whole day,
hunting itself is only 30–50% [Documented, Brandman] — the rest is
rest and maintenance, which are *also* mostly still. Net design
target for the device:

> **≥90% of all displayed frames are a held pose** (no bird-region
> motion beyond the authored micro-events inside `idle_hunt`).
> Motion is rationed: a typical watched hour contains a handful of
> steps, at most a few strikes, and one maintenance bout at most.
> If a proposed schedule produces visible activity more often than
> ~once per 2–3 minutes while watched, it is animatronic, whatever
> the chart quality. [Estimate, derived from all of §1]

### 3.2 Inter-event intervals: heavy tails, hard floors

- Real behavior is **bursty**: events cluster inside bouts, and
  bouts are separated by long quiet. Uniform-random intervals are
  the signature of a machine (they produce suspiciously regular
  spacing and no clusters); fixed intervals are worse. Draw
  inter-bout gaps from a **heavy-tailed distribution**
  (lognormal-shaped), with a **hard floor** (never two hunts
  within X minutes of a catch) and a **soft ceiling** (hunger
  eventually wins — a very long fast raises strike probability).
  This is the standard ethological picture (bout structure is how
  ethograms are analyzed) and it is cheap to implement honestly.
- **Refractory rules create memory:** after a big fish, a longer
  settle and a lower strike rate (satiation); after two misses, a
  relocate is mandatory; after a maintenance bout, no second bout
  for hours. A creature with consequences reads as alive; a
  creature that samples behaviors independently reads as a jukebox.
- **No repeats of the rarest items:** yawn, warble stretch, foot-stir
  — at most once per day each, and never on consecutive days at the
  same hour. Rarity is a property of the *schedule*, protected by
  explicit caps, not left to dice (dice eventually produce three
  yawns in an afternoon, and the spell breaks).

### 3.3 Condition the probabilities on the world the engine already knows

The creature engine's behavior system takes presence / light / time
as first-class inputs. Add **tide** and **season** at the same rank —
for a tidal-creek heron they are not garnish:

- **Light:** dawn/dusk → hunt weight high; full day → maintenance
  and loaf weight rises, hunt continues at lower weight; night →
  doze dominant, hunt only via the moon gate below.
- **Tide:** falling-to-low water raises strike-rate and hunt-bout
  probability (prey concentrating); high water lowers both
  (site-dependent in the literature — keep the effect mild, on
  *rate*, never on success) [Probable].
- **Moon:** night hunting only when the moon-illumination bucket is
  the brightest (m3) — the plates already encode this bucket, so
  behavior and art agree for free.
- **Season:** the §1.8 deltas (summer hunt share up + gular
  behavior unlocked; autumn flight rate up; winter everything
  slower and rarer; spring = plumage art note only).
- **Presence:** arrival → ladder step 1 (freeze-check) almost
  always, step 2 (alert) sometimes, step 3 (flush) almost never
  while watched. Sustained presence shortens inter-event gaps
  modestly (the audience effect, §3.4) but never converts the bird
  into a performer: it does not hunt *for* the watcher, it merely
  lives slightly faster in company — and flights stay suppressed,
  as the contract already rules.

### 3.4 The audience-rate honesty note

The presence contract's watched pacing (fishing every 1.5–4 min)
is **theatre, not ethology**: the real bird, watched, strikes
*less* willingly, not more. Keep the watched rates if Jimmy likes
them — a device is allowed its contract with its audience — but
log the decision as a deliberate departure from the animal (§1.2:
real ≈ 1 strike per 10–20 min of hunting, ~56% success), so a
future "make it real" pass knows exactly which knobs are the fake
ones: watched strike rate and watched success rate. Unwatched
rates should sit at the animal's values; the house's empty rooms
deserve the true bird.

### 3.5 Alive vs animatronic — the design discipline, distilled

From the ethogram tradition and from behavioral animation
(Tu & Terzopoulos's *Artificial Fishes*, SIGGRAPH '94, remains the
cleanest statement: model the animal as an autonomous agent with
perception, internal state, and a behavior repertoire — believable
motion *emerges* from the repertoire being driven by state, not
from scripting sequences):

1. **Every action has a visible cause, or is a maintenance act.**
   Strikes happen because a fish appeared (in the fishing third);
   alerts because something arrived; the shake because feathers
   need resettling after flight/immersion/bouts. Uncaused signature
   behaviors on a timer are the animatronic tell.
2. **Internal state, not a playlist.** Hunger (time since catch),
   satiation, disturbance level, and bout membership should gate
   what can happen next. The scheduler samples from what the
   *state* allows, never from the whole roster at once.
3. **Bouts and sequences are real.** Maintenance runs stretch →
   shake → preen; hunting runs arrive → stand → (steps) → strike →
   handle → relocate. Within a bout, order is authored; between
   bouts, timing is probabilistic. This two-level structure is the
   single biggest structural difference between an ethogram and a
   shuffle.
4. **Stillness is content.** The held fraction (§3.1) is the
   product. Any feature that spends stillness to buy "liveliness"
   is trading the wrong direction for this species.
5. **Consequences persist.** A catch changes the next hour
   (relocate, settle, drink, lower rate). A flush changes the
   return (land in a different third, longer freeze). State that
   survives the event is what separates a creature from a clip
   player.
6. **Asymmetry across days.** A daily seed (already the house
   pattern from the Kindle almanac work) so Tuesday's bird is not
   Monday's bird replayed — same canon, different day.
7. **Rarity is protected by caps, not probabilities alone** (§3.2).
8. **The gaze works even when nothing else does.** Inside every
   hold, the head's saccade-and-fixate script (already charted) is
   the cheapest aliveness there is: a statue whose *attention*
   visibly moves reads as a mind at rest, not a machine at idle.

---

## 4. What this changes — work items for the build

1. ◆ Author `relocate` (brisk post-strike walk, 3–6 s) and wire it
   after every strike resolution. *(from §1.2)*
2. ◆ Author `body_shake` (120–240 f) and a maintenance-bout wrapper
   that runs stretch → shake → preen with early stop. *(§1.5)*
3. ◆ Author `gular_flutter` held posture (summer) — needs a throat
   treatment in the rig; `beak_open` held ~0.4. *(§1.6)*
4. ◆ Author `freeze_check` (alert ladder step 1) and re-grade the
   existing `alert` as step 2; flight becomes step 3. *(§1.7)*
5. Promote `drink` to a named beat after big catches / hot days.
6. Scheduler: add tide + season as first-class probability inputs;
   implement bout structure, heavy-tailed gaps, refractory/satiation
   rules, and per-day caps on the rarest items. *(§3)*
7. Correct the success model to ~56% with `strike_miss` as a common
   outcome; log watched-mode rate/success boosts as deliberate
   theatre knobs. *(§1.2, §3.4)*
8. Bank the Upright Spread-Wing display as the heron↔heron seed;
   do not schedule solo. *(§1.7)*
9. Art note only: breeding-plumage plume growth Feb–Apr. *(§1.8)*
10. Still wanted from the real world (unchanged from the study):
    Jimmy's slow-motion footage of a strike and a full catch→swallow
    would retire the last [Uncertain] numbers in the canon.

---

## 5. Sources

**Scientific / reference**

1. Hodgens, Blumenshine & Bednarz (2004), "Great Blue Heron
   Predation on Stocked Rainbow Trout in an Arkansas Tailwater
   Fishery," *North American Journal of Fisheries Management*
   24:63–75 — 828 strikes / 202 h, 56.4% success, 87% of prey
   ≤14 cm, 86.9% of captures ≤20 cm depth, standing + walking
   slowly used almost exclusively.
   https://www.academia.edu/27275991/Great_Blue_Heron_Predation_on_Stocked_Rainbow_Trout_in_an_Arkansas_Tailwater_Fishery
2. UW undergraduate studies, False Bay / Griffin Bay, San Juan
   Island — focal sampling: standing + walking slowly dominate;
   strike rate and success vary with site, tide height and phase.
   https://digital.lib.washington.edu/researchworks/items/83dc7787-cb71-4117-b2ad-0bf793d5e58d/full
   https://digital.lib.washington.edu/researchworks/items/3dac4b95-8237-4bd3-9b15-287e6ea882e7
3. Warrick (1992), *Prey flight behaviors… of Great Blue Herons*,
   M.S. thesis, University of Oregon — post-strike relocation
   (>2–3 m, brisk walk) before resuming stealth; stand-and-wait /
   slow walk as the core tactics (after Hancock & Kushlan 1984).
   https://www.academia.edu/100510072/Prey_flight_behaviors_in_response_to_wading_bird_disturbances_and_their_influence_on_foraging_strategy_of_Great_Blue_Herons_Ardea_herodias_
4. Godin (1977), *Canadian Field-Naturalist* 91(1) — deep-water
   feeding; Krebs (1974) ~41% capture success for solitary adults;
   one bird 28/31.
   http://zenodo.org/records/15894514/files/bhlpart345340.pdf?download=1
5. Quinney & Smith (1980), *Canadian Journal of Zoology* 58 —
   adult vs juvenile foraging efficiency; juveniles slower to
   handle medium prey.
   https://explore.openaire.eu/search/result?id=doi_dedup___::1ba17084f212a5656b0f7c69b40b7108
6. Maxwell & Putnam (1968), "The Maintenance Behavior of the
   Black-crowned Night Heron," *Wilson Bulletin* 80(4):467–478 —
   the ardeid maintenance ethogram: shaking 5–10 s with wings
   rapidly in/out; stretch form and its bout context; yawning;
   throat pulsation.
   http://zenodo.org/records/16708703/files/bhlpart242068.pdf?download=1
7. RSPN, *White-bellied Heron* monograph — activity budgets:
   White-bellied 72.5% foraging / 23.1% roosting / 1.5% preening;
   mean 4.03 steps/min hunting; **Brandman (1976): GBH 30–50% of
   time hunting**; Mock & Mock (1980): Goliath Heron 58%.
   https://archive.org/stream/RSPNWhiteBelliedHeron/RSPN%20-%20White-bellied%20Heron_djvu.txt
8. Kent, estuarine heron assembly study (Tampa Bay) — Great Egret
   foraging speed 0.04 m/s; GBH among the stand-and-wait /
   walk-slowly species.
   http://www.researchgate.net/publication/232693307_Food_Exploitation_Patterns_in_an_Assembly_of_Estuarine_Herons
9. Meyerriecks (1966), "Additional Observations on 'Foot-Stirring'
   Feeding Behavior in Herons," *The Auk* 83(3):471–472 — family-
   level documentation of foot-stirring.
   (cited via https://www.dejavu.org/cgi-bin/get.cgi?ver=95&url=http://web.archive.org%2Fweb%2F20211219040656%2Fhttps%3A%2F%2Fen.wikipedia.org%2Fwiki%2FHeron)
10. "The Peculiar Necks of Herons and Anhingas," *Integrative
    Organismal Biology* (2026) — mid-neck specialization for rapid
    neck straightening (already in the movement study; re-confirmed).
    https://pmc.ncbi.nlm.nih.gov/articles/PMC13014071/
11. USA National Phenology Network, GBH species account —
    breeding timing across the range; post-breeding dispersal from
    late August; migration from late September.
    https://mynpn.usanpn.org/npnapps/species/Ardea/herodias

**Field / naturalist (graded as field accounts)**

12. Hancock & Kushlan, Upright and Spread Wing display description,
    quoted with a documented GBH encounter — Feathered Photography.
    https://featheredphotography.com/blog/2019/09/26/aggressive-great-blue-herons-upright-and-spread-wing-display/
13. Chesapeake phenology: Inside Annapolis, "Great Blue Heron:
    Symbol of the Chesapeake" (pairs form Mar–Apr; >half the
    Atlantic breeding population nests in the Bay region; year-round
    residents unless ice); Chesapeake Bay Foundation, "The
    Stalkers"; Virginia parks GBH page (nesting Feb–Apr; eggs
    ~28 d; young leave ~60 d).
    http://www.insideannapolis.com/archive/2003/issue6/GreatBlueHeron.html
    https://www.cbf.org/resources/june-the-stalkers-great-blue-herons-and-their-kin/
    https://www.smithfieldparksva.com/254/Great-Blue-Herons
14. Colony displays (Stretch Display, Landing Call, Greeting
    Ceremony, stick transfer): Birds Outside My Window (after
    Chuck Tague's rookery documentation); Wild Birds Unlimited.
    https://www.birdsoutsidemywindow.org/2010/03/24/heron-sunrise/comment-page-1/
    https://southseattle.wbu.com/botm-great-blue-heron
15. Gular flutter / delta-wing sunning: Seagrove Walks (photographed
    GBH, wings bowled, bill open, throat fluttering); Volusia
    Naturalist (delta-wing posture, sun-facing, with flutter).
    https://seagroveswalks.org/2023/08/15/two-herons/
    https://volusianaturalist.com/hot-birds/
16. Body shake / feather resettling in GBH: Henson Photography
    (stretch → shake → preen sequence, photographed); A-Z Animals
    (whole-body shake, wing flicks, after immersion).
    https://toddhensonphotography.com/blog/tag/shaking
    https://a-z-animals.com/articles/how-great-blue-herons-dry-off/
17. Vocal repertoire and escalation (Vennesland 2000): call ladder
    under increasing disturbance; Awk scream mean 2.3 s, mostly
    colonial — summarized in the species accounts.
    https://www.reptileknowledge.com/reptile-pedia/how-do-herons-eat-prey
18. Cornell Lab, *All About Birds* GBH accounts — crepuscular
    emphasis, night hunting with rod-dense retinas, territorial
    upright toward intruders incl. people (via Oneida Lake / Life
    on CSG Pond species pages quoting Cornell).
    https://www.lifeoncsgpond.com/great-blue-heron

**Design literature**

19. Tu & Terzopoulos (1994), "Artificial Fishes: Physics,
    Locomotion, Perception, Behavior," SIGGRAPH '94 — the animal
    as autonomous agent: perception + internal intention generator
    driving a behavior repertoire; believability from state-driven
    selection, not scripting.
    https://www.cs.ucla.edu/~dt/papers/siggraph94/siggraph94.pdf
20. Rain World (Videocult) creature ecosystem — independent,
    need-driven creature AI widely cited in design writing for
    reading as *alive rather than scripted*; creatures act on their
    own drives regardless of the observer. (Design case; secondary
    coverage.)
    https://source4game.com/rain-world-free-download/

**Video sources** *(consulted via Cornell/Macaulay catalog pages and
captions in this pass — not frame-stepped; frame-stepping the strike
and swallow entries remains an open item, as in the movement study §12)*

21. 🎬 Macaulay Library / Cornell — GBH stalking and striking prey
    in shallow water (Eric Liner, New York, 2006).
    https://blog.allaboutbirds.org/guide/Great_Blue_Heron/photo-gallery/435241
22. 🎬 Macaulay Library / Cornell — GBH heavy flight, slow beats,
    neck tucked (Eric Liner, Florida, 2009).
    https://www.allaboutbirds.org/guide/Great_Blue_Heron/photo-gallery/464905
23. 🎬 Macaulay Library / Cornell — GBH territorial display in a
    colony: breeding plumes ruffled, head and bill pointed skyward
    (Tom Johnson, Florida, 2014).
    https://blog.allaboutbirds.org/guide/Great_Blue_Heron/photo-gallery/475672
24. 🎬 Cornell Lab, "Species Spotlight: Great Blue Heron" — 2-minute
    species overview video (identification, feeding, nesting).
    https://www.allaboutbirds.org/guide/Great_Blue_Heron/photo-gallery/
25. 🎬 Deb Sandidge's GBH feather-shake footage (via Instagram),
    discussed at A-Z Animals [16] — the whole-body shake after
    immersion.

*Primary footage remains Jimmy's nine measured clips of the local
bird (`~/workspace/heron/reference/`) — the literature above is the
frame they hang in, not a replacement for them.*
