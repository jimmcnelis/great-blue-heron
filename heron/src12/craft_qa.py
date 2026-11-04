"""Heron v1.2 craft QA — the cartoon skill's measurable audits, run on the
canon clips and the assembled episode. Every gate from movement-charts.yaml
that can be measured is measured; results land in qa_results_12.json and a
contact sheet (turn sequence + eating sequence + stops + episode keys).

Run AFTER corpus_build.py (uses anchors12.json) — but degrades gracefully
to computing anchors itself.
"""
import json
import numpy as np
from PIL import Image
import rig
import clips
import sim as simmod

R = {}

def bird_cells(g):
    return int((g != rig.WHITE).sum())

def render(f):
    g, info = rig.render(clips.unflatten(f))
    return g, info

def pose_track(frames, key):
    return np.array([f[key] for f in frames], dtype=float)

# ---------------------------------------------------------------- canon
def audit_canon():
    C = clips.all_clips()
    # ---- yaw stops: silhouette area within +-5% of profile (chart gate)
    base = clips.base_flat()
    areas = {}
    for yaw in (0.0, 45.0, 90.0, 135.0, 180.0):
        f = dict(base); f['yaw'] = yaw
        g, _ = render(f)
        areas[yaw] = bird_cells(g)
    dev = {y: (a - areas[0.0]) / areas[0.0] for y, a in areas.items()}
    R['yaw_stops_area_dev'] = {str(k): round(v, 4) for k, v in dev.items()}
    R['yaw_stops_pass'] = bool(max(abs(v) for v in dev.values()) <= 0.05)

    # ---- strike: spacing audit + anticipation + smear count
    st = C['strike']
    tips = []
    for f in st:
        _g, info = render(f)
        tips.append(info['beak_tip'])
    tips = np.array(tips)
    rel = 24  # release starts after deepen 12 + hold 12; contact at rel+2
    d = [float(np.hypot(*(tips[i + 1] - tips[i]))) for i in range(rel - 2, rel + 3)]
    R['strike_spacing'] = {'travel_first2': round(d[0] + d[1], 1),
                           'travel_final2': round(d[2] + d[3], 1),
                           'pass': bool(d[2] + d[3] >= d[0] + d[1])}
    coil = pose_track(st, 'neck_coil')
    R['strike_anticipation'] = {
        'coil_at_release': float(coil[rel - 1]), 'coil_max': float(coil.max()),
        'pass': bool(coil[rel - 1] >= coil.max() - 1e-9)}
    hold_path = float(sum(np.hypot(*(tips[i + 1] - tips[i]))
                          for i in range(12, 23)))
    R['strike_loaded_hold_beak_path_cells'] = round(hold_path, 2)
    R['strike_smear_frames'] = int((pose_track(st, 'smear') > 0).sum())
    R['strike_beak_open_at_contact'] = float(st[rel + 3]['beak_open'])

    # ---- idle: held fraction + flicker (rendered)
    idle = C['idle_hunt_a']
    grids = [render(f)[0] for f in idle]
    changed = []
    flips = 0
    tot = 0
    for i in range(1, len(grids)):
        diff = grids[i] != grids[i - 1]
        changed.append(int(diff.sum()))
        if 2 <= i <= 70:  # inside the opening hold: any A-B-A is shimmer
            aba = (grids[i] == grids[i - 2]) & diff
            flips += int(aba.sum())
            tot += grids[i].size
    changed = np.array(changed)
    R['idle_held_fraction'] = float((changed <= 2).mean())
    R['idle_flicker_per_1000'] = round(1000.0 * flips / max(tot, 1), 3)

    # ---- turn: area on EVERY frame within +-5%; head world-yaw error
    turn = C['turn']
    base_area = bird_cells(render(clips.base_flat())[0])
    devs = []
    werr = []
    for f in turn:
        g, _ = render(f)
        devs.append((bird_cells(g) - base_area) / base_area)
        werr.append(abs((f['yaw'] + f['head_yaw']) - 150.0))
    R['turn_area_max_dev'] = round(float(max(abs(np.array(devs)))), 4)
    R['turn_area_pass'] = bool(max(abs(np.array(devs))) <= 0.05)
    R['turn_head_world_err_max_pivots'] = round(float(max(werr[4:60])), 2)

    # ---- flight: tip lag + downstroke share + loop wrap smoothness
    fc = C['flight_cycle']
    flap = pose_track(fc, 'flap'); tip = pose_track(fc, 'flap_tip')
    def rescale(v):
        return v * (38.0 / 52.0) if v < 0 else v * (30.0 / 34.0)
    best = None
    for lag in range(0, 5):
        errs = [abs(tip[i] - rescale(flap[(i - lag) % 12])) for i in range(12)]
        if best is None or float(np.mean(errs)) < best[1]:
            best = (lag, float(np.mean(errs)))
    R['flight_tip_lag_frames'] = int(best[0])
    # downstroke share = frames on the descending limb (incl. bottom frame)
    desc = sum(1 for i in range(12) if flap[i] < flap[(i - 1) % 12])
    R['flight_downstroke_share'] = round(desc / 12.0, 3)
    R['flight_loop_wrap_delta'] = round(float(abs(flap[0] - flap[-1])), 1)

    # ---- swallow gates (pose tracks)
    sw = C['swallow']
    amp = pose_track(sw, 'neck_bulge_amp'); pos = pose_track(sw, 'neck_bulge_pos')
    run = cur = 0
    for v in amp:
        cur = cur + 1 if v > 0.2 else 0
        run = max(run, cur)
    R['swallow_bulge_run_frames'] = int(run)
    travel = pos[66:88]
    R['swallow_bulge_monotonic'] = bool(np.all(np.diff(travel) >= -1e-9))
    R['swallow_fish_orient_at_head_back'] = float(sw[60]['fish_orient'])
    R['swallow_fish_none_from'] = next(i for i, f in enumerate(sw)
                                       if f['fish'] == 'none' and i > 40)
    # head-first freeze check: rendered frame at head_back — fish eye cell
    # should sit closer to the gape than to the beak tip
    g, info = render(sw[62])
    ys, xs = np.nonzero(g == rig.INK)
    fish_mask = np.isin(g, [rig.FISH, rig.FISH2])
    fys, fxs = np.nonzero(fish_mask)
    R['swallow_fish_visible_at_head_back'] = bool(len(fxs) > 0)

    # ---- walk gates: lift apex + head lock through passes
    wk = C['walk']
    fy = np.minimum(pose_track(wk, 'leg_near.fy'), pose_track(wk, 'leg_far.fy'))
    R['walk_foot_lift_apex_units'] = round(float(86.0 - fy.min()), 1)
    heads = []
    for f in wk:
        _g, info = render(f)
        heads.append(info['head'][0])
    heads = np.array(heads)
    # pass windows: steps 2 and 3 commit+lift = frames 30-39 and 60-69
    devs = []
    for a, b in ((30, 40), (60, 70)):
        devs.append(float(heads[a:b].max() - heads[a:b].min()))
    R['walk_head_world_x_range_in_pass_cells'] = [round(d, 1) for d in devs]

    # ---- step cycle gates: loop + lift
    sc = C['step_cycle']
    R['step_lift_apex_units'] = round(float(86.0 - pose_track(sc, 'leg_near.fy').min()), 1)

    # ---- one-leg anti-vanish: leg-color cells, tucked vs standing
    g0, _ = render(clips.base_flat())
    g1, _ = render(C['oneleg_enter'][-1])
    legcols = [rig.RUSTY, rig.LEGC]
    c0 = int(np.isin(g0, legcols).sum()); c1 = int(np.isin(g1, legcols).sum())
    R['oneleg_leg_cells_ratio'] = round(c1 / c0, 3)

    # ---- scratch: foot-to-head anchor distance at the beats (design units)
    sk = C['scratch']
    g, info = render(sk[26])
    foot = ((sk[26]['root_x'] + sk[26]['leg_near.fx'] - 60.0) * rig.S + rig.W / 2,
            sk[26]['leg_near.fy'] * rig.S)
    head = info['head']
    R['scratch_foot_head_dist_units'] = round(
        float(np.hypot(foot[0] - head[0], foot[1] - head[1]) / rig.S), 1)

    # ---- doze silhouette differs from idle
    gz, _ = render(C['doze'][-1])
    gi, _ = render(clips.base_flat())
    R['doze_vs_idle_symdiff_frac'] = round(
        float((gz != gi).sum() / max(bird_cells(gi), 1)), 3)

    # ---- landing / takeoff gates (pose tracks)
    ld = C['landing']
    touch = next(i for i, f in enumerate(ld) if f['flying'] < 0.5)
    R['landing_touch_frame'] = int(touch)
    R['landing_flare_ok'] = bool(max(pose_track(ld, 'flap')[touch - 10:touch]) >= 40)
    R['landing_feet_forward_pre_touch'] = bool(
        max(pose_track(ld, 'leg_near.fx')[touch - 12:touch]) > -5)
    fold_done = next(i for i, f in enumerate(ld) if i > touch and f['wing_amt'] < 0.05)
    R['landing_fold_after_touch_frames'] = int(fold_done - touch)
    tk = C['takeoff']
    flap_t = pose_track(tk, 'flap')
    first_down = next(i for i in range(12, 96) if flap_t[i] < -20)
    feet_off = next(i for i, f in enumerate(tk)
                    if f['leg_near.fy'] < 85.0 and i > 12)
    R['takeoff_downstroke_before_feet'] = bool(first_down < feet_off)
    dangle = sum(1 for f in tk if f['flying'] > 0.5 and f['leg_near.toe'] <= -60)
    R['takeoff_dangle_frames'] = int(dangle)
    ext_max = float(pose_track(tk, 'neck_extend').max())
    R['takeoff_neck_stretch_max'] = ext_max

# ---------------------------------------------------------------- episode
def audit_episode():
    ep, events, spans = simmod.build_episode()
    ink = simmod.InkSim()
    zone_ok, ink_rest_max = {}, 0
    turn_frames, eat_frames = [], []
    span_of = {}
    for s in spans:
        for i in range(s['start'], s['start'] + s['n']):
            span_of[i] = s['clip']
    mid_frames = {}
    for i, flat in enumerate(ep):
        if flat is None:
            grid = np.full((rig.H, rig.W), rig.WHITE, dtype=np.uint8)
        else:
            pose = clips.unflatten(flat)
            grid, info = rig.render(pose)
            ink.observe(i, pose, info)
        grid = ink.draw(np.array(grid), i)
        name = span_of[i]
        if name.startswith('idle') and getattr(ink, 'last_alive', 0) == 0:
            below = int((grid[simmod.SURF:] == rig.INK).sum())
            ink_rest_max = max(ink_rest_max, below)
        if name == 'turn@R' and (i - spans[[s['clip'] for s in spans].index('turn@R')]['start']) % 9 == 0:
            turn_frames.append(grid)
        mid_frames.setdefault(name, grid)
    R['ink_below_surface_at_rest_max'] = int(ink_rest_max)
    R['ink_event_kinds'] = {k: sum(1 for e in ink.events if e[1] == k)
                            for k in ('ripple', 'splash', 'ring', 'drip', 'churn')}
    R['episode_frames'] = len(ep)
    R['episode_spans'] = [s['clip'] for s in spans]
    # zone check: bird centroid of each span's middle frame
    zones = {}
    for s in spans:
        mid = s['start'] + s['n'] // 2
        flat = ep[mid]
        if flat is None:
            continue
        g, _ = render(flat)
        ys, xs = np.nonzero(g != rig.WHITE)
        zones[s['clip']] = round(float(xs.mean()) / rig.W, 2) if len(xs) else None
    R['span_centroid_x_frac'] = zones
    return turn_frames, mid_frames

def contact_sheet(turn_frames, mid_frames):
    C = clips.all_clips()
    def row(grids):
        return np.concatenate([rig.PALETTE[g] for g in grids], axis=1)
    stops = []
    base = clips.base_flat()
    for yaw in (0.0, 45.0, 90.0, 135.0, 180.0):
        f = dict(base); f['yaw'] = yaw
        stops.append(render(f)[0])
    eat = []
    st = clips.strike_big(); sw = clips.swallow()
    for src, idxs in ((st, (34, 37)), (sw, (10, 36, 52, 62, 74, 100))):
        for i in idxs:
            eat.append(render(src[i])[0])
    rows = [row(stops), row(eat[:4]), row(eat[4:])]
    if turn_frames:
        rows.append(row(turn_frames[:5]))
    wmax = max(r.shape[1] for r in rows)
    rows = [np.concatenate([r, np.full((r.shape[0], wmax - r.shape[1], 3), 255,
                                       dtype=np.uint8)], axis=1)
            if r.shape[1] < wmax else r for r in rows]
    img = np.concatenate(rows, axis=0)
    Image.fromarray(img).save('qa_contact_sheet_12.jpg', quality=88)
    print("contact sheet:", img.shape)

if __name__ == '__main__':
    audit_canon()
    tf, mf = audit_episode()
    with open('qa_results_12.json', 'w') as fh:
        json.dump(R, fh, indent=1)
    contact_sheet(tf, mf)
    print(json.dumps(R, indent=1))
