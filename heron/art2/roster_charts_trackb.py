"""Track B chart builders — movement-charts.yaml additions (2026-11-03):
relocate, body_shake, strike_miss, plus root-translated tracks the
living-bird sim needs (stand at root 40, R stand at root 95).

Same machinery and conventions as roster_charts.py (Track / statue /
anchors). Frame counts asserted against the charts' canonical_frames.

relocate gait (authored for this chart): plants spaced one stride
(11 units) apart — the statue's own stagger — so the gait chains
steadily: at every step end the stance reads lead +6 / trail -5,
exactly the statue stagger it started from. Per-step phases mirror
step_cycle (weight_commit 4 / lift_fold 6 / advance 8 / place 6) with
the pass distributed across the first 10 frames; the stepping foot
swings 2 strides of ground (22 units) while the body advances 11 —
the swing-speed asymmetry of a real walk. NO freeze between steps:
this is the repertoire's one brisk walk (Warrick 1992 via Track B).
Head: carried WITH the body (statue offset hx 19) with a small
per-step bob. An earlier draft world-locked the head as in
step_cycle — right for that chart's single +14 pass, wrong over
55 units: the neck stretched back toward the start stand (caught
on the contact strip, fixed before delivery).
"""
import copy, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import roster_charts as RC
from roster_charts import Track, statue, tilt, with_coil_anchor, EASE, BOTTOM

# ---------------------------------------------------------------- relocate
def _relocate_track(root0=40.0, steps=5, stride=11.0):
    """Brisk post-strike walk: `steps` alternating steps, root advancing
    `stride` per step, starting FROM the strike-stand statue (root0)."""
    tr = Track(statue(root0))
    head_world = root0 + 19.0
    plants = {'leg_near': root0 + 6.0, 'leg_far': root0 - 5.0}
    root = root0
    order = ['leg_far', 'leg_near', 'leg_far', 'leg_near', 'leg_far',
             'leg_near'][:steps]
    for leg in order:
        other = 'leg_near' if leg == 'leg_far' else 'leg_far'
        plant = plants[leg]
        base = copy.deepcopy(tr.state)
        new_root = root + stride
        frames = []
        # weight_commit 4f + lift_fold 6f: pass spans these 10 frames
        for i in range(10):
            u = EASE['inout']((i + 1) / 10)
            r = root + stride * u
            p = copy.deepcopy(base)
            p['root_x'] = r
            p['hx'] = head_world - r
            p[other]['fx'] = plants[other] - r
            p[leg]['fx'] = plant - r
            if i < 4:   # weight_commit: settle onto the stance leg
                p['root_y'] = 0.3 * (i + 1) / 4
                p[leg]['fy'] = BOTTOM
                p[leg]['toe'] = 0.0
            else:       # lift_fold: foot folds up, toes point down
                q = EASE['inout']((i - 3) / 6)
                p['root_y'] = 0.3
                p[leg]['fy'] = BOTTOM - 7.0 * q
                p[leg]['toe'] = -55.0 * q
            frames.append(p)
        # advance 8f: folded leg swings to its next plant (2 strides of
        # ground), root still, head still world-locked
        adv0 = frames[-1]
        new_plant = plant + 2 * stride
        for i in range(8):
            q = EASE['inout']((i + 1) / 8)
            p = copy.deepcopy(adv0)
            p[leg]['fx'] = (plant - new_root) + \
                ((new_plant - new_root) - (plant - new_root)) * q
            frames.append(p)
        # place 6f: unfold, descend toe-first, weight settles back
        pl0 = frames[-1]
        for i in range(6):
            q = EASE['inout']((i + 1) / 6)
            p = copy.deepcopy(pl0)
            p[leg]['fy'] = pl0[leg]['fy'] + (BOTTOM - pl0[leg]['fy']) * q
            p[leg]['toe'] = pl0[leg]['toe'] * (1 - q)
            p['root_y'] = 0.3 * (1 - q)
            frames.append(p)
        tr.frames.extend(frames)
        tr.state = copy.deepcopy(frames[-1])
        plants[leg] = new_plant
        root = new_root
    # end state: statue at the new stand (root0 + steps*stride)
    assert abs(tr.state['root_x'] - (root0 + steps * stride)) < 1e-9
    return tr

def ch_relocate():
    tr = _relocate_track(40.0, steps=5)
    assert len(tr.frames) == 120, len(tr.frames)
    # head-carry fix: the builder's per-frame hx was world-locked
    # (head_world - root); replace with a body-carried head — statue
    # offset plus a per-step bob (thrust-and-hold smoothed to a sine
    # at this fidelity). Legs and root are untouched.
    for i, p in enumerate(tr.frames):
        ph = 2 * math.pi * ((i % 24) / 24.0)
        p['hx'] = 19.0 + 2.2 * math.sin(ph)   # hx is root-relative
        p['hy'] = -28.0 + 0.5 * math.sin(2 * ph)
    tr.state = copy.deepcopy(tr.frames[-1])
    return tr

# ------------------------------------------------------------- body_shake
def ch_body_shake():
    """152f at the fishing stand (statue root 40). Erection ramp 24f,
    5 whole-body oscillations over 80f (16f period, root/head/plume
    channels), settle 48f with the plumage re-laying over 36f.
    The wing in-out beat of the ethogram has NO folded-mode channel
    in the shipped bridge (same class of gap as head_yaw) — the shake
    is carried by root_x / head_roll / plume_sway, documented in the
    chart entry."""
    tr = Track(statue(40.0))
    # erect 24f: plume erection envelope up, coil loosens a touch
    tr.seg(24, {'plume_sway': 1.8, 'neck_w': 1.05, 'head_pitch': 2.0,
                'root_y': -0.2}, 'inout')
    # shake 80f: 5 oscillations; envelope ramps in 12f, decays late
    def shake(p, i, n):
        f = i + 1
        env = min(1.0, f / 12.0) * (1.0 if f <= 60 else
                                    1.0 - 0.55 * (f - 60) / 20.0)
        ph = 2 * math.pi * f / 16.0
        p['root_x'] += 0.7 * math.sin(ph) * env
        p['head_roll'] = 5.0 * math.sin(ph + 0.7) * env
        p['plume_sway'] = 1.8 + 1.0 * math.sin(ph * 2 + 1.2) * env
        p['root_y'] = -0.2 + 0.22 * abs(math.sin(ph)) * env
    tr.hold(80, overlay=shake)
    # settle 48f: plumage re-lays over 36f, then a true hold
    tr.seg(36, {'plume_sway': 0.0, 'neck_w': 1.0, 'head_pitch': 4.0,
                'head_roll': 0.0, 'root_y': 0.0}, 'inout')
    tr.hold(12)
    assert len(tr.frames) == 152, len(tr.frames)
    return tr

# ------------------------------------------------------------ strike_miss
def ch_strike_miss():
    """64f. The strike chart verbatim through withdrawal (same
    builder code path as ch_strike's phases), except: grab_dwell
    closes on NOTHING (fish stays none) and recover is preceded by
    the authored head_shake (12f, hx overlay = the bridge's
    neck_sway channel, +/-1.6 decaying, 3 oscillations)."""
    tr = Track(statue(40.0))
    tr.seg(12, with_coil_anchor({'coil': 1.0, 'body_tilt': tilt(-30.0),
                                 'head_pitch': 17.0}), 'inout')
    tr.seg(12, {'coil': 1.06, 'hx': 26.5, 'hy': -13.8,
                'head_pitch': 19.0}, 'lin')
    start = copy.deepcopy(tr.state)
    cum = [0.25, 0.60, 1.0, 1.0]
    for i in range(4):
        p = copy.deepcopy(start)
        for path, v in RC._leaves({'coil': 0.15, 'hx': 30.0, 'hy': 20.0,
                                   'head_pitch': 56.0, 'neck_w': 0.62,
                                   'root_x': 43.0, 'body_tilt': tilt(-27.0),
                                   'root_y': 2.5}):
            a = RC._get(start, path)
            RC._set(p, path, a + (v - a) * cum[i])
        p['gape'] = (0.0, 0.0, 0.5, 1.0)[i]
        if i == 2:
            p['smear'] = 1.0
        tr.frames.append(p)
    tr.state = copy.deepcopy(tr.frames[-1])
    # grab_dwell 2f: bill closes on nothing — no fish keys at all
    tr.seg(2, {'gape': 0.0}, 'lin')
    # withdrawal 12f: identical keys to the catch's withdrawal
    tr.seg(12, {'coil': 0.7, 'hx': 24.0, 'hy': -6.0, 'head_pitch': 6.0,
                'neck_w': 0.9, 'root_x': 41.0, 'root_y': 1.0,
                'body_tilt': tilt(-31.0)}, 'out')
    # head_shake 12f: 3 decaying oscillations (chart: neck_sway ±1.6)
    def hshake(p, i, n):
        u = (i + 1) / n
        p['hx'] += 1.6 * math.sin(2 * math.pi * 3 * u) * (1 - u)
        p['head_roll'] = 3.0 * math.sin(2 * math.pi * 3 * u + 0.5) * (1 - u)
    tr.hold(12, overlay=hshake)
    # recover_to_coil 10f: identical to the catch's recover
    tr.seg(10, with_coil_anchor({'coil': 0.85, 'head_pitch': 0.0,
                                 'neck_w': 1.0, 'root_x': 40.0,
                                 'root_y': 0.0, 'body_tilt': tilt(-33.0)}),
           'inout')
    assert len(tr.frames) == 64, len(tr.frames)
    return tr

CHARTS_TRACKB = {'relocate': ch_relocate, 'body_shake': ch_body_shake,
                 'strike_miss': ch_strike_miss}
CANONICAL_TRACKB = {'relocate': 120, 'body_shake': 152, 'strike_miss': 64}

# ------------------------------------------------------- translated tracks
def _translated(builder, dx):
    tr = builder()
    out = []
    for p in tr.frames:
        q = copy.deepcopy(p)
        q['root_x'] = float(q['root_x']) + dx
        out.append(q)
    return out

def build_sim_assets():
    """Root-translated copies of canonical tracks for the sim's stage:
    the fishing stand is root 40 (canonical L-dwell charts sit at 26,
    +14); the R stand is root 95 (canonical strike family at 40, +55 —
    exactly where relocate delivers the bird). Same poses, same QA
    class; NOT roster charts — sim infrastructure, disclosed as such."""
    A = {}
    for name, b in (('idle_hunt', RC.ch_idle_hunt), ('doze', RC.ch_doze),
                    ('oneleg', RC.ch_oneleg), ('preen', RC.ch_preen),
                    ('stretch', RC.ch_stretch), ('scratch', RC.ch_scratch),
                    ('alert', RC.ch_alert),
                    ('head_saccade', RC.ch_head_saccade)):
        A[f'{name}_at_stand'] = _translated(b, 14.0)
    for name, b in (('strike', RC.ch_strike), ('swallow', RC.ch_swallow),
                    ('strike_miss', ch_strike_miss),
                    ('takeoff', RC.ch_takeoff)):
        A[f'{name}_at_R'] = _translated(b, 55.0)
    return A

def _safe(p):
    return {k: ({kk: float(vv) for kk, vv in v.items()}
                if isinstance(v, dict) else
                ([float(x) for x in v] if isinstance(v, tuple) else
                 (float(v) if isinstance(v, (int, float)) else v)))
            for k, v in p.items()}

if __name__ == '__main__':
    mode = sys.argv[1]
    tracks = {}
    if mode == 'charts':
        for name, fn in CHARTS_TRACKB.items():
            tr = fn()
            assert len(tr.frames) == CANONICAL_TRACKB[name], \
                (name, len(tr.frames))
            tracks[name] = tr.frames
            print(f'{name}: {len(tr.frames)} frames')
        dst = sys.argv[2]
    else:
        tracks = build_sim_assets()
        for name, fr in tracks.items():
            print(f'{name}: {len(fr)} frames, '
                  f'root {fr[0]["root_x"]:.0f} -> {fr[-1]["root_x"]:.0f}')
        dst = sys.argv[2]
    with open(dst, 'w') as f:
        json.dump({k: [_safe(p) for p in v] for k, v in tracks.items()}, f)
    print('wrote', dst)
