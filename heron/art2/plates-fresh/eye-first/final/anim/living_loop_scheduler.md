# Living Loop Scheduler — spec

Jimmy's direction (2026-11-04): **the loop should be random** — no fixed
sequence. And: **non-repeating tasks** — behaviors may not repeat until
every other behavior has had its turn.

## How it works

`living_loop_scheduler.py` builds each run fresh:

1. **Shuffle-bag draws for behaviors.** The eight accepted non-idle cycles
   go into a bag as weighted tickets — **preen ×3, stride ×3, strike ×2,
   stretch ×2, miss ×2, flight ×1, courtship ×1, nightstalk ×1**
   (15 tickets; the weights are the relative frequencies — preen/stride
   commonest, flight/courtship/nightstalk rarest). Tickets are drawn
   **without replacement**: a behavior cannot play again until the bag
   empties. When the bag is reshuffled, the first draw is re-rolled
   until it differs from the behavior that just played — so a behavior
   never plays twice in a row, even across the reshuffle boundary.
   - **miss** (×2) is the second fishing outcome, sitting alongside
     strike in the bag — a strike doesn't always connect.
   - **courtship** (×1) is the display — a rare, seasonal-feeling event.
   - **nightstalk** (×1) is **NIGHT-GATED**: on the device it enters the
     bag only when the ambient light sensor says dark. In offline
     playlist renders it is an ordinary ticket and may appear; every
     nightstalk draw in the sequence map is flagged as the night piece.
2. **Stillness between every draw.** Between behaviors — and at the open
   and close — sits an idle hold of a randomized **20–90 s**, assembled
   from the two accepted idle cycles: 10 s blocks of `idle_attempt1`
   sprinkled into longer holds, `idle_attempt2` (the 1 s procedural loop,
   tiled) filling the rest. Idle takes ~60% of the *draws*, and because
   the holds run long (mean ~55 s against 10 s behaviors), stillness is
   the large majority of the *time* — 89% in the sample render.
3. **Flight** always plays its full clip, which contains its own
   empty-paper beat (bird gone, paper empty, return landing).

Resulting behavior frequencies over a full bag: preen 20%, stride 20%,
strike 13%, stretch 13%, miss 13%, flight 7%, courtship 7%, nightstalk 7%
of *behavior slots* — against idle's dominance of total runtime.

## Rules honored

- Accepted cycles only: idle ×2, preen, stride, strike A, stretch,
  flight, plus miss, courtship, and nightstalk — added to the loop at
  Jimmy's direction 2026-11-04 18:21 (nightstalk night-gated, see
  above). No catch (closed by Jimmy 2026-11-04; the portrait ships
  without it).
- Every cycle starts and ends on the shared alert stance, so joins are
  plain cuts at a matched pose — cycles' internals are never altered.
- Output: 1024×600, 24 fps, silent, no titles, no text, no drawn water.
- `--seed N` reproduces a run exactly; without it the seed is random and
  is recorded at the top of the sequence map.

## Outputs

- `living_loop_playlist.txt` — the drawn unit list (concat playlist).
- `living_loop_sequence.md` / `<render>.sequence.md` — order, start
  times, durations, bag state per draw, and the seed.
- `--render` renders the mp4 (default `living_loop_demo.mp4`,
  `--target` seconds, default 420).
