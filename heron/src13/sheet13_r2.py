"""Model sheet v1.3 r2 — the five phase-1.1 repairs, both style packs.
Flight + front in both styles; rest/coil/swallow panels as changed.
Silhouette strip along the bottom. Same layout conventions as sheet13.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig13 as R
import cycles13 as C

OUT = os.path.expanduser('~/workspace/heron/model_sheet_v1_3_r2.png')
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def pose(**kw):
    p = R.default_pose(); p['root_x'] = 58.0
    for k, v in kw.items():
        if k in ('leg_near', 'leg_far'):
            p[k].update(v)
        else:
            p[k] = v
    return p

COIL = dict(body_tilt=24, coil=1.0, hx=25, hy=-15, head_pitch=16, root_y=1.5)
FLIGHT = dict(wing_mode='flight', body_tilt=2, coil=0.9, hx=24, hy=-14,
              head_pitch=-2, flap=-42, flap_tip=10,
              leg_near=dict(fx=-37, fy=53, toe=-55), leg_far=dict(fx=-34, fy=50, toe=-55))
FRONT = dict(yaw=90, hx=-2, hy=-27, body_tilt=4, coil=0.3)

_frames, _ink = C.build_episode()
SWAL = _frames[412]

PANELS = [
    ('NATURALIST — flight (r2)', pose(**FLIGHT), 'naturalist'),
    ('STORYBOOK — flight (r2)', pose(**FLIGHT), 'storybook'),
    ('NATURALIST — yaw 90 front (r2)', pose(**FRONT), 'naturalist'),
    ('STORYBOOK — yaw 90 front (r2)', pose(**FRONT), 'storybook'),
    ('NATURALIST — profile rest', pose(), 'naturalist'),
    ('STORYBOOK — profile rest (beard r2)', pose(), 'storybook'),
    ('NATURALIST — hunting coil (patch r2)', pose(**COIL), 'naturalist'),
    ('STORYBOOK — hunting coil (patch r2)', pose(**COIL), 'storybook'),
    ('NATURALIST — swallow f412 (bulge r2)', SWAL, 'naturalist'),
    ('STORYBOOK — swallow f412 (bulge r2)', SWAL, 'storybook'),
]
SILS = [('silhouette — rest', pose()), ('silhouette — front', pose(**FRONT)),
        ('silhouette — flight', pose(**FLIGHT))]

def main():
    PW, PH, LAB = 676, 396, 34
    W = PW * 3 + 24
    H = (PH + LAB) * 4 + 250
    sheet = Image.new('RGB', (W, H), 'white')
    dr = ImageDraw.Draw(sheet)
    try:
        fl = ImageFont.truetype(FB, 25)
        fs = ImageFont.truetype(FONT, 21)
    except Exception:
        fl = fs = ImageFont.load_default()
    for i, (label, p, style) in enumerate(PANELS):
        g = R.render(p, style)
        im = Image.fromarray(R.to_rgb(g)).resize((PW, PH))
        x, y = (i % 3) * (PW + 8) + 4, (i // 3) * (PH + LAB)
        sheet.paste(im, (x, y + LAB))
        dr.text((x + 6, y + 5), label, fill=(20, 30, 45), font=fl)
    y0 = 4 * (PH + LAB) + 8
    dr.text((10, y0), 'SILHOUETTE TEST — name the pose from the shape alone', fill=(20, 30, 45), font=fl)
    for i, (label, p) in enumerate(SILS):
        g = R.render(p, 'silhouette')
        im = Image.fromarray(R.to_rgb(g)).resize((PW // 2, PH // 2))
        x = 10 + i * (PW // 2 + 30)
        sheet.paste(im, (x, y0 + 36))
        dr.text((x + 4, y0 + 40 + PH // 2), label, fill=(20, 30, 45), font=fs)
    sheet.save(OUT)
    print('sheet', OUT, sheet.size)

if __name__ == '__main__':
    main()
