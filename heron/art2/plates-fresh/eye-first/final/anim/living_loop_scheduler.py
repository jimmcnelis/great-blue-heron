#!/usr/bin/env python3
"""
Living Loop Scheduler — great blue heron ambient loop.

Director's rules (Jimmy, 2026-11-04):
  * The loop is RANDOM, not a fixed sequence.
  * Non-repeating tasks: non-idle behaviors are drawn WITHOUT REPLACEMENT
    from a weighted shuffle-bag. Bag composition (copies = weights):
        preen x3, stride x3, strike x2, stretch x2, miss x2,
        flight x1, courtship x1, nightstalk x1                 (15 tickets)
    A behavior cannot play again until the bag empties and is reshuffled,
    and the first draw after a reshuffle may not be the behavior that
    just played.
  * Idle / stillness sits between every behavior draw, for a randomized
    hold of ~20-90 s, built from the two accepted idle cycles.
  * Accepted cycles ONLY (all start and end on the shared alert stance,
    so joins are plain cuts at a matched pose):
        idle_attempt1  -> attempt1.mp4          (10 s, generated idle)
        idle_attempt2  -> attempt2.mp4          (1 s procedural loop, tileable)
        preen          -> preen_attempt1.mp4
        stride         -> stride_attempt2.mp4
        strike         -> strike_attemptA.mp4
        stretch        -> stretch_attempt1.mp4
        flight         -> flight_attempt1.mp4   (contains its own
                                                 empty-paper beat)
        miss           -> miss_attempt1.mp4     (second fishing outcome,
                                                 added 2026-11-04 18:21)
        courtship      -> courtship_attempt1.mp4 (display, rare; added
                                                 2026-11-04 18:21)
        nightstalk     -> nightstalk_attempt1.mp4 (added 2026-11-04 18:21)
    nightstalk is NIGHT-GATED: on the device it draws only when the
    ambient light sensor says dark. In offline playlist renders it is an
    ordinary ticket and may appear; the sequence map marks every
    nightstalk draw as the night piece.
    No catch (closed by Jimmy 2026-11-04; ships without it).

Usage:
    python3 living_loop_scheduler.py                 # playlist + map only
    python3 living_loop_scheduler.py --render        # also render the mp4
    python3 living_loop_scheduler.py --seed 42 --render --target 420
    python3 living_loop_scheduler.py --render --out my_loop.mp4

Without --seed the run is random and the seed it used is recorded in the
sequence map, so any render can be reproduced exactly with that seed.
Output video: 1024x600, 24 fps, silent. Cycles' internals are never
altered — assembly only.
"""

import argparse
import os
import random
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

CLIPS = {
    "idle1":      "attempt1.mp4",
    "idle2":      "attempt2.mp4",
    "preen":      "preen_attempt1.mp4",
    "stride":     "stride_attempt2.mp4",
    "strike":     "strike_attemptA.mp4",
    "stretch":    "stretch_attempt1.mp4",
    "flight":     "flight_attempt1.mp4",
    "miss":       "miss_attempt1.mp4",
    "courtship":  "courtship_attempt1.mp4",
    "nightstalk": "nightstalk_attempt1.mp4",
}
BEHAVIOR_SECONDS = 10.0          # every behavior cycle is a 10 s clip
IDLE1_SECONDS = 10.0

BAG_RECIPE = {"preen": 3, "stride": 3, "strike": 2, "stretch": 2, "miss": 2,
              "flight": 1, "courtship": 1, "nightstalk": 1}

# Night-gated behaviors: on the device these draw only when the ambient
# light sensor says dark. In playlist renders they are ordinary tickets;
# the sequence map flags each of their draws as the night piece.
NIGHT_GATED = {"nightstalk"}

IDLE_MIN, IDLE_MAX = 20, 90      # randomized stillness hold, seconds


def fresh_bag(rng, last_played):
    """A shuffled bag of behavior tickets; first ticket != last_played."""
    bag = [b for b, n in BAG_RECIPE.items() for _ in range(n)]
    while True:
        rng.shuffle(bag)
        if last_played is None or bag[0] != last_played:
            return bag


def idle_hold_units(rng, seconds):
    """Split an idle hold into units of the two idle cycles.
    Returns a list of (clip_key, seconds) summing exactly to `seconds`:
    10 s blocks of idle1, one tileable idle2 block for the remainder,
    shuffled so the mix varies."""
    blocks = []
    remaining = seconds
    while remaining >= 30:                    # sprinkle idle1 blocks in long holds
        if rng.random() < 0.5:
            blocks.append(("idle1", IDLE1_SECONDS))
            remaining -= IDLE1_SECONDS
        else:
            break
    if remaining > 0:
        blocks.append(("idle2", float(remaining)))
    rng.shuffle(blocks)
    return blocks


def build_schedule(rng, target):
    """Returns (units, events): units = [(clip, seconds)...] for rendering;
    events = human-readable sequence map rows."""
    units, events = [], []
    elapsed = 0.0
    bag = fresh_bag(rng, None)
    last = None
    draw_no = 0

    def add_idle():
        nonlocal elapsed
        hold = rng.randint(IDLE_MIN, IDLE_MAX)
        for key, secs in idle_hold_units(rng, hold):
            units.append((key, secs))
        events.append(("idle", hold, f"stillness hold ({hold} s)"))
        elapsed += hold

    add_idle()                                # opens on stillness
    while elapsed < target:
        if not bag:
            bag = fresh_bag(rng, last)
            events.append(("reshuffle", 0, "bag emptied -> reshuffled "
                           f"(first draw cannot be '{last}')"))
        behavior = bag.pop(0)
        draw_no += 1
        units.append((behavior, BEHAVIOR_SECONDS))
        note = f"bag draw #{draw_no}, {len(bag)} ticket(s) left in bag"
        if behavior in NIGHT_GATED:
            note += (" — NIGHT PIECE (night-gated on device: plays only "
                     "when the ambient sensor says dark)")
        events.append((behavior, BEHAVIOR_SECONDS, note))
        elapsed += BEHAVIOR_SECONDS
        last = behavior
        add_idle()                            # stillness between every draw
    return units, events


def ffprobe_dur(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(out.stdout.strip())


def render(units, out_path):
    """Normalize each unit to an identical-parameter segment, then concat.
    Cycles are never altered internally — trimming is to whole frames at
    the clip edges only."""
    tmp = tempfile.mkdtemp(prefix="livingloop_")
    seg_paths = []
    for i, (key, secs) in enumerate(units):
        src = os.path.join(HERE, CLIPS[key])
        seg = os.path.join(tmp, f"seg_{i:03d}.mp4")
        frames = int(round(secs * 24))
        cmd = ["ffmpeg", "-y", "-v", "error"]
        if key == "idle2":
            cmd += ["-stream_loop", "-1"]    # tile the 1 s procedural loop
        cmd += ["-i", src, "-vf",
                "scale=1024:600:force_original_aspect_ratio=disable,"
                "fps=24,setsar=1,format=yuv420p",
                "-frames:v", str(frames), "-an",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                "-video_track_timescale", "24000", seg]
        subprocess.run(cmd, check=True)
        seg_paths.append(seg)
    listfile = os.path.join(tmp, "concat.txt")
    with open(listfile, "w") as f:
        for p in seg_paths:
            f.write(f"file '{p}'\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", listfile, "-c", "copy", out_path], check=True)
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Heron living-loop scheduler")
    ap.add_argument("--seed", type=int, default=None,
                    help="seed for a reproducible schedule (default: random)")
    ap.add_argument("--target", type=float, default=420,
                    help="target total seconds (default 420 = 7 min); the "
                         "render ends after the idle hold that crosses it")
    ap.add_argument("--render", action="store_true", help="render the mp4")
    ap.add_argument("--out", default=os.path.join(HERE, "living_loop_demo.mp4"))
    ap.add_argument("--playlist", default=os.path.join(HERE, "living_loop_playlist.txt"))
    ap.add_argument("--map", default=None,
                    help="sequence map path (default: <out>.sequence.md when "
                         "rendering, else living_loop_sequence.md)")
    args = ap.parse_args()

    seed = args.seed if args.seed is not None else random.SystemRandom().randrange(2**31)
    rng = random.Random(seed)

    units, events = build_schedule(rng, args.target)
    total = sum(s for _, s in units)

    # concat playlist (source clips, for inspection / external renderers)
    with open(args.playlist, "w") as f:
        for key, secs in units:
            f.write(f"# {key} x {secs:.0f}s\nfile '{CLIPS[key]}'\n")

    map_path = args.map or (os.path.splitext(args.out)[0] + ".sequence.md"
                            if args.render else
                            os.path.join(HERE, "living_loop_sequence.md"))
    with open(map_path, "w") as f:
        f.write("# Living loop — drawn sequence\n\n")
        f.write(f"- seed: {seed}  (reproduce: `--seed {seed}`)\n")
        f.write(f"- target: {args.target:.0f} s; drawn total: {total:.0f} s "
                f"({total/60:.1f} min)\n")
        f.write(f"- bag recipe: " +
                ", ".join(f"{k} x{v}" for k, v in BAG_RECIPE.items()) +
                " — drawn without replacement; reshuffle's first draw "
                "cannot repeat the last behavior played\n")
        if NIGHT_GATED:
            f.write("- night-gated (device: ambient sensor dark only; "
                    "flagged in the map below): " +
                    ", ".join(sorted(NIGHT_GATED)) + "\n")
        f.write("\n")
        f.write("| # | start | event | duration |\n|---|-------|-------|----------|\n")
        t = 0.0
        for i, (kind, secs, note) in enumerate(events, 1):
            if kind == "reshuffle":
                f.write(f"| {i} | {t:.0f} s | *reshuffle* | — |\n")
                continue
            f.write(f"| {i} | {t:.0f} s | {kind} — {note} | {secs:.0f} s |\n")
            t += secs
        f.write(f"\nTotal: {t:.0f} s. Idle share: "
                f"{100*sum(s for k,s,_n in events if k=='idle')/t:.0f}% of time "
                f"is stillness.\n")

    print(f"seed {seed}: {len(units)} units, {total:.0f} s total")
    print(f"playlist -> {args.playlist}")
    print(f"sequence map -> {map_path}")
    if args.render:
        render(units, args.out)
        print(f"rendered -> {args.out} ({ffprobe_dur(args.out):.1f} s)")


if __name__ == "__main__":
    sys.exit(main())
