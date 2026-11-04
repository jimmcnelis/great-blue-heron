#!/usr/bin/env python3
"""Corpus + rig measurements: validate spike 3 on f0027, then the strike
family across extension + the idle control. Writes corpus_results.json."""
import json
import numpy as np
import measure_core as MC

OUT = {}

def drawn_for(pair_id):
    pose = MC.pose_of(pair_id)
    img = MC.load(f'{MC.FM3}/corpus/target/{pair_id}.png')
    pts_d, pts_r, names, notes = MC.DL.drawn_landmarks(img, pose, MC.EYE_UV)
    d = {n: p for n, p in zip(names, pts_d)}
    r = {n: p for n, p in zip(names, pts_r)}
    return img, pose, d, r, notes

def frame_record(pair_id):
    img, pose, d, r, notes = drawn_for(pair_id)
    rig = MC.rig_geometry(pose)
    cm = MC.S1.content_mask(img)
    drawn_run = float(np.hypot(*(d['skull'] - d['neck_s1'])))
    drawn_poly = [d['neck_s1'], d['neck_s2'], d['neck_s3'], d['skull']]
    rig_poly = rig['spine'][1:] + [rig['head_c']]
    neck_fp = rig['stack'][1] > 0
    dw, _ = MC.centerline_widths(cm, drawn_poly)
    rw, _ = MC.centerline_widths(neck_fp, rig_poly)
    # station widths (drawn stations vs rig stations)
    st_drawn, st_rig = {}, {}
    for i, nm in enumerate(('neck_s1', 'neck_s2', 'neck_s3')):
        lo = drawn_poly[max(i - 1, 0)]; hi = drawn_poly[min(i + 1, 3)]
        w, _, _ = MC.scan_width(cm, d[nm], hi - lo)
        st_drawn[nm] = w
        lo = rig_poly[max(i - 1, 0)]; hi = rig_poly[min(i + 1, 4)]
        w, _, _ = MC.scan_width(neck_fp, rig['spine'][i + 1], hi - lo)
        st_rig[nm] = w
    # uniform torso reference on the drawing AND on the rig silhouette
    tor_d, _ = MC.torso_hull_from_mask(cm, d['neck_s1'], d['skull'] - d['neck_s1'])
    sil = np.any(rig['stack'] > 0, axis=0)
    tor_sil, _ = MC.torso_hull_from_mask(sil, rig['spine'][1],
                                         rig['head_c'] - rig['spine'][1])
    return dict(
        drawn_run_straight=drawn_run,
        rig_run_straight=rig['run_straight'], rig_run_arc=rig['run_arc'],
        ratio_straight=drawn_run / rig['run_straight'],
        drawn_pts={k: [round(float(v), 1) for v in p] for k, p in d.items()},
        rig_spine=[[round(float(v), 1) for v in p] for p in rig['spine']],
        rig_head_c=[round(float(v), 1) for v in rig['head_c']],
        torso_rig_poly=rig['torso_hull'], torso_uniform_drawn=tor_d,
        torso_uniform_silhouette=tor_sil,
        drawn_run_norm=drawn_run / tor_d if tor_d else None,
        rig_run_norm=rig['run_straight'] / tor_sil if tor_sil else None,
        widths_drawn_frac={str(k): round(v[0], 1) for k, v in dw.items()},
        widths_rig_frac={str(k): round(v[0], 1) for k, v in rw.items()},
        widths_drawn_stations={k: round(v, 1) for k, v in st_drawn.items()},
        widths_rig_stations={k: round(v, 1) for k, v in st_rig.items()},
        neck_w_param_units=rig['neck_w_param'], notes=notes)

# ---- rig extension curve over the whole strike chart (rig only, cheap)
curve = {}
for i in range(len(MC.TRACKS2['strike'])):
    g = MC.rig_geometry(MC.TRACKS2['strike'][i])
    curve[i] = round(g['run_straight'], 1)
peak = max(curve, key=curve.get)
print('rig strike run: peak frame', peak, curve[peak],
      '| f20/25/27/29/34:', [curve[i] for i in (20, 25, 27, 29, 34)])
OUT['rig_curve'] = {str(k): v for k, v in curve.items()}
OUT['rig_peak_frame'] = peak

for pid in ('strike_f0027', 'strike_f0025', 'strike_f0029',
            'strike_f0020', 'strike_f0034', 'idle_f0030'):
    OUT[pid] = frame_record(pid)
    r = OUT[pid]
    print(pid, 'drawn', round(r['drawn_run_straight'], 1),
          'rig', round(r['rig_run_straight'], 1),
          'ratio', round(r['ratio_straight'], 2),
          '| torso drawn/rigpoly/sil', round(r['torso_uniform_drawn'], 1),
          round(r['torso_rig_poly'], 1), round(r['torso_uniform_silhouette'], 1))

json.dump(OUT, open(f'{MC.ART2}/strike-measure/corpus_results.json', 'w'), indent=1)
print('corpus_results.json written')
