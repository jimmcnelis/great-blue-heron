import os, sys, json
import numpy as np
from PIL import Image
HOME = os.path.expanduser('~')
ART2 = f'{HOME}/workspace/heron/art2'
FS = f'{ART2}/finished-art-stills'
FM3 = f'{FS}/finish-model-v3'
V3 = f'{ART2}/fill-spike-v3'
sys.path.insert(0, ART2); sys.path.insert(0, f'{HOME}/workspace/heron/src13')
sys.path.insert(0, FM3); sys.path.insert(0, f'{ART2}/fill-spike-v1')
sys.path.insert(0, V3)
import build_corpus as bc
import spike_fill as S1
import drawn_landmarks as DL

load = S1.load
tracks2 = json.load(open(f'{FS}/rig-v2/work/pose_tracks_v2.json'))
eye_uv = (54.7, 1.0)   # measured from idle_f0030 gold, pregate run 2026-11-04
pose = tracks2['strike'][27]
gold = load(f'{FM3}/corpus/target/strike_f0027.png')
gold3, info = DL.reregister_part(gold, pose, eye_uv)
Image.fromarray(np.clip(gold3,0,255).astype(np.uint8)).save(f'{V3}/work/gold_strike_f0027_rereg.png')
print('rereg gold regenerated with the final 8-landmark fit; warp', info['warp'], 'rms', info['rms'])

rec = {
  "frame": "strike_f0027", "measure": "head+neck footprint coverage |content & (ch1|ch2)| / |ch1|ch2| (spike instruments: S1.content_mask, S1.labelmap)",
  "eye_uv_from_idle_gold": [54.7, 1.0], "idle_drawn_eye_xy": [580.7, 145.2],
  "coverage_before": 0.3687, "coverage_after": 0.1600, "pregate_bar": 0.60,
  "landmarks": {
    "skull":     {"drawn": [677.2, 523.9], "rig": [598.7, 463.3], "delta_px": 99.2},
    "eye":       {"drawn": [689.4, 533.7], "rig": [626.2, 510.7], "delta_px": 67.3},
    "bill_tip":  {"drawn": [702.0, 596.0], "rig": [674.3, 588.4], "delta_px": 28.7, "note": "drawn tip frame-clipped; true tip off-frame, delta biased low"},
    "bill_base": {"drawn": [687.1, 557.0], "rig": [614.7, 487.2], "delta_px": 100.6},
    "crest_root":{"drawn": [658.0, 474.5], "rig": [589.7, 444.9], "delta_px": 74.5},
    "neck_s1":   {"drawn": [556.1, 363.8], "rig": [569.2, 357.6], "delta_px": 14.5},
    "neck_s2":   {"drawn": [574.4, 397.6], "rig": [583.7, 390.5], "delta_px": 11.7},
    "neck_s3":   {"drawn": [593.0, 426.1], "rig": [596.6, 423.9], "delta_px": 4.2}
  },
  "full_fit_8_landmarks": {"warp_s_deg_dx_dy": [0.714, -11.862, 86.942, 214.338], "rms_px": 41.76,
    "resid_px": {"skull": 42.1, "eye": 32.2, "bill_tip": 61.4, "bill_base": 37.4, "crest_root": 27.0, "neck_s1": 49.9, "neck_s2": 40.9, "neck_s3": 32.8}},
  "neck_run_lengths": {"s1_to_skull_drawn": 200.8, "s1_to_headc_rig": 109.7, "ratio": 1.83,
                       "s3_to_skull_drawn": 129.1, "s3_to_headc_rig": 39.5, "ratio_s3": 3.27},
  "diagnostic_head_only_fit": {"warp_s_deg_dx_dy": [1.211, 10.35, -76.029, -289.686], "rms_px": 32.54,
    "resid_px": {"skull": 26.1, "eye": 14.7, "bill_tip": 46.0, "bill_base": 37.1, "crest_root": 30.0},
    "note": "diagnostic only - not a registration run; even the 5 head points alone do not fit a similarity (in-frame points skull/base/crest carry 26-37px residuals)"},
  "notes": {"yellow_px": 239, "head_component_px": 4244, "eye_cluster_px": 28}
}
json.dump(rec, open(f'{V3}/work/pregate_final.json', 'w'), indent=1)
print('pregate_final.json written')
