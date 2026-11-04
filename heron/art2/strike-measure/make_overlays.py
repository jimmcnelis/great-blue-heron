#!/usr/bin/env python3
"""Annotated landmark overlays for corpus golds (drawn=green, rig=yellow,
width ticks=cyan) — the eye-validation step spike 3 used."""
import numpy as np
from PIL import Image, ImageDraw
import measure_core as MC

def overlay(pair_id):
    pose = MC.pose_of(pair_id)
    img = MC.load(f'{MC.FM3}/corpus/target/{pair_id}.png')
    pts_d, pts_r, names, notes = MC.DL.drawn_landmarks(img, pose, MC.EYE_UV)
    rig = MC.rig_geometry(pose)
    cm = MC.S1.content_mask(img)
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGB')
    dr = ImageDraw.Draw(out)
    d = {n: p for n, p in zip(names, pts_d)}
    poly = [d['neck_s1'], d['neck_s2'], d['neck_s3'], d['skull']]
    dr.line([tuple(p) for p in poly], fill=(0, 200, 0), width=3)
    rpoly = rig['spine'][1:] + [rig['head_c']]
    dr.line([tuple(p) for p in rpoly], fill=(255, 200, 0), width=2)
    widths, _ = MC.centerline_widths(cm, poly)
    for f, (w, p, pa, pb) in widths.items():
        dr.line([tuple(pa), tuple(pb)], fill=(0, 200, 255), width=2)
    for n, p in zip(names, pts_d):
        dr.ellipse([p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5], fill=(0, 255, 0))
        dr.text((p[0] + 7, p[1] - 6), n, fill=(0, 160, 0))
    for p in rig['spine']:
        dr.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], outline=(255, 200, 0), width=2)
    dr.ellipse([rig['head_c'][0] - 5, rig['head_c'][1] - 5,
                rig['head_c'][0] + 5, rig['head_c'][1] + 5], outline=(255, 200, 0), width=2)
    path = f'{MC.ART2}/strike-measure/overlay_{pair_id}.png'
    out.save(path)
    print('saved', path, 'notes:', notes)

for pid in ('strike_f0025', 'strike_f0029'):
    overlay(pid)
