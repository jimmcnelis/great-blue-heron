# FLIGHT — design notes
- Jimmy's bar (2026-11-05): flight is the SIGNATURE MOVE — presentation and
  flourish on par with or better than strike/idle/stretch/preen.
- Spec: ../choreography/flight.md — 168 ticks / 14.0 s @ 12 fps, home->home.
- Production: Mordecai draws every frame directly; keys gated first
  (style proof = airborne downstroke extreme); batches of 5 approved by
  Jimmy before the next, as with the strike.
- Flourish beats that must land: wings-raised extreme before liftoff;
  deep-amplitude climb beats (envelope 1.0/1.0/0.9/0.8); the apex GLIDE
  held a full second (the poster moment); wingtip lag 1 tick on every
  beat; splash churn at liftoff and touchdown (rings + droplets at the
  feet only — paper otherwise blank but for ripple rings); momentum
  steps plant exactly ON the home marks; fold completes >=5 ticks after
  touchdown; final resolve = exact home frame.
- Canon: wingbeat pairs (down5/up7 over 12 ticks, 2.0 Hz at 12 fps
  scheduling per spec 1b note); takeoff neck EXTENDS straight, folds to
  flight S on the second beat; legs dangle then trail STRAIGHT beyond
  the tail (clip's bent dangle is rejected for cruise — chart wins).
- Mirroring levers stay available: frames are produced bird-layer-first;
  per-frame bbox + persistent canvas bench v4 runs on the real frames
  after drawing (stride decision rides on it).
- Attribution: flight reference library (Boga flight reels, Teague
  takeoff, Astroland winter flight, Mark Smith glide-in) — see
  ~/workspace/heron/reference-footage/INVENTORY.md.

## ENDING REDESIGN (Jimmy, 2026-11-05 ~22:52)
The return-to-home landing "dragged at the end." NEW ENDING: the heron flies OUT of frame right, loops off-screen (unseen, ~10 ticks of empty marsh), re-enters from the right flying left (bird layer MIRRORED — the flip-in-code ruling), and lands on the OPPOSITE side, settling into the mirrored home. Flight is now a side-changer like stride; the next flight returns it to the left. The long settle/gather is cut: flare -> reach -> touchdown -> one step -> fold -> mirrored home.

## TWO-SEQUENCE STRUCTURE (Jimmy, 2026-11-05 ~23:18)
Flight is really TWO sequences that always run back-to-back: FLIGHT OUT (home -> takeoff -> cross -> exit right) and FLIGHT HOME (enter from left -> descend -> land -> settle -> home), joined by a couple of seconds of background-only while the bird is off-screen looping. The gap is NOT stored as frames: the player holds the single marsh plate image for the interval (same rule as the home frame acting alone between sequences). Home holds at both ends are likewise runtime holds of the shared home frame, not baked frames. Stored frames: Out ~74 + Home ~57 = ~131 (~12.9 MB est.) vs ~15.1 MB as one baked file; each file ~6-7 MB.

## GAP RULING (Jimmy, 2026-11-05 ~23:20)
The pause between FLIGHT OUT and FLIGHT HOME is 5 SECONDS (60 ticks) of background-only — a runtime hold of the plate image, zero stored frames. Firmware pair logic: play Out -> hold plate 5000 ms -> play Home.

## GAP REVISED (Jimmy, 2026-11-05 ~23:32) — supersedes the 5 s ruling
The bird is out of frame for **30 SECONDS** between FLIGHT OUT and FLIGHT HOME.
Still a runtime hold of the one plate image (zero stored frames); firmware
constant FLIGHT_GAP_MS = 30000. Total flight behavior ≈ 37 s: ~3 s out,
30 s gone, ~4.4 s home.
