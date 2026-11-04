#!/usr/bin/env python3
"""Draw recorded landmarks on key frames -> atlas images. Coords are 0-1000."""
import json, os
from PIL import Image, ImageDraw, ImageFont

B = os.path.expanduser('~/workspace/heron/art2/real-bird-measure')
K = os.path.join(B, 'frames', 'keys')
F = os.path.join(B, 'frames')
OUT = os.path.join(B, 'atlas')
os.makedirs(OUT, exist_ok=True)

def xy(p, W, H):
    return (p[0] / 1000 * W, p[1] / 1000 * H)

def draw(img, pts, lines, label):
    W, H = img.size
    dr = ImageDraw.Draw(img)
    for a, b, color, wdt in lines:
        dr.line([xy(pts[a], W, H), xy(pts[b], W, H)], fill=color, width=wdt)
    for name, p in pts.items():
        x, y = xy(p, W, H)
        r = max(5, W // 160)
        dr.ellipse([x - r, y - r, x + r, y + r], fill=(255, 60, 60), outline=(255, 255, 255), width=2)
        dr.text((x + r + 3, y - 6), name, fill=(255, 255, 0))
    dr.rectangle([0, 0, W, 26], fill=(0, 0, 0))
    dr.text((6, 6), label, fill=(255, 255, 255))
    return img

RED = (255, 60, 60); BLU = (60, 140, 255); GRN = (60, 255, 120); WHT = (255, 255, 255)

jobs = []

# 1 standing tall (UR)
img = Image.open(os.path.join(K, 'UR_stand_tall.jpg')).convert('RGB')
pts = {'tip': (373, 80), 'billbase': (468, 48), 'eye': (498, 26), 'back': (556, 68),
       'q1': (536, 165), 'q2': (545, 270), 'q3': (553, 365), 'base': (570, 460),
       'tail': (744, 962), 'chest': (533, 538), 'backtop': (607, 437), 'belly': (614, 823)}
skull = ((498 + 556) / 2, (26 + 68) / 2)
pts['skull'] = skull
img = draw(img, pts, [('tip', 'billbase', RED, 3), ('eye', 'q1', GRN, 3), ('q1', 'q2', GRN, 3),
                      ('q2', 'q3', GRN, 3), ('q3', 'base', GRN, 3), ('tail', 'chest', BLU, 3)],
           'STANDING ALERT (neck extended up) - UR4n4gYX2T4 t=75s, GBH')
img.save(os.path.join(OUT, 'atlas_01_standing_UR.jpg'), quality=88)
jobs.append('atlas_01_standing_UR.jpg')

# 2 coil (qpYk f28)
img = Image.open(os.path.join(F, 'qpYkzsJIQ4M_0.5-7.0', 'f0028.jpg')).convert('RGB')
pts = {'head': (534, 328), 'tip': (645, 436), 'mid': (498, 386), 'base': (484, 447),
       'tail': (211, 396), 'chest': (518, 470), 'backtop': (372, 321), 'belly': (393, 549)}
img = draw(img, pts, [('head', 'mid', GRN, 3), ('mid', 'base', GRN, 3), ('head', 'base', RED, 3),
                      ('tail', 'chest', BLU, 3)],
           'RESTING COIL (pre-strike) - qpYkzsJIQ4M t=1.40s, GBH')
img.save(os.path.join(OUT, 'atlas_02_coil_qpYk.jpg'), quality=88)
jobs.append('atlas_02_coil_qpYk.jpg')

# 3 peak strike GBH (qpYk f37)
img = Image.open(os.path.join(F, 'qpYkzsJIQ4M_0.5-7.0', 'f0037.jpg')).convert('RGB')
pts = {'head': (741, 635), 'tip': (764, 725), 'base': (538, 488),
       'tail': (210, 323), 'chest': (540, 540), 'backtop': (395, 315), 'belly': (385, 560)}
img = draw(img, pts, [('head', 'base', RED, 4), ('tail', 'chest', BLU, 3)],
           'PEAK STRIKE (standing spear) - qpYkzsJIQ4M t=1.70s, GBH')
img.save(os.path.join(OUT, 'atlas_03_strike_peak_qpYk.jpg'), quality=88)
jobs.append('atlas_03_strike_peak_qpYk.jpg')

# 4 lunge strike (6bc f266)
img = Image.open(os.path.join(F, '6bcHcoarCU4_55.0-65.0', 'f0266.jpg')).convert('RGB')
pts = {'head': (155, 585), 'tip': (45, 655), 'base': (415, 545)}
img = draw(img, pts, [('head', 'base', RED, 4)],
           'PEAK LUNGE STRIKE - 6bcHcoarCU4 t=59.42s, GBH (body pitches in)')
img.save(os.path.join(OUT, 'atlas_04_lunge_6bc.jpg'), quality=88)
jobs.append('atlas_04_lunge_6bc.jpg')

# 5 peak strike grey (GY f88)
img = Image.open(os.path.join(F, 'P7Yb_koYsoA_110.0-124.0', 'f0088.jpg')).convert('RGB')
pts = {'head': (440, 788), 'tip': (423, 850), 'base': (680, 548),
       'tail': (996, 385), 'chest': (712, 622), 'backtop': (845, 368), 'belly': (775, 668)}
img = draw(img, pts, [('head', 'base', RED, 4), ('tail', 'chest', BLU, 3)],
           'PEAK STRIKE - P7Yb_koYsoA t=113.48s, GREY HERON (cousin, separate)')
img.save(os.path.join(OUT, 'atlas_05_strike_peak_grey.jpg'), quality=88)
jobs.append('atlas_05_strike_peak_grey.jpg')

# 6 withdrawal grey (GY f100)
img = Image.open(os.path.join(F, 'P7Yb_koYsoA_110.0-124.0', 'f0100.jpg')).convert('RGB')
pts = {'head': (483, 635), 'tip': (440, 852), 'base': (678, 555)}
img = draw(img, pts, [('head', 'base', RED, 4)],
           'WITHDRAWAL (re-coiling, +0.48s after peak) - P7Yb_koYsoA t=113.96s, GREY')
img.save(os.path.join(OUT, 'atlas_06_withdrawal_grey.jpg'), quality=88)
jobs.append('atlas_06_withdrawal_grey.jpg')

# 7 stalk step (6bc f241)
img = Image.open(os.path.join(F, '6bcHcoarCU4_55.0-65.0', 'f0241.jpg')).convert('RGB')
pts = {'head': (465, 275), 'tip': (352, 322), 'base': (540, 515)}
img = draw(img, pts, [('head', 'base', RED, 3)],
           'STALK STEP (mid-stride, neck coiled, head steady) - 6bcHcoarCU4 t=59.00s, GBH')
img.save(os.path.join(OUT, 'atlas_07_stalk_step_6bc.jpg'), quality=88)
jobs.append('atlas_07_stalk_step_6bc.jpg')

# 8 swallow (oaBww t33) with width bars
img = Image.open(os.path.join(K, 'OA_bulge2.jpg')).convert('RGB')
W, H = img.size
dr = ImageDraw.Draw(img)
for (fx, bx, yy, lab) in [(403, 138, 575, 'upper'), (498, 238, 705, 'mid (bolus)'), (492, 168, 835, 'lower')]:
    p1, p2 = xy((fx, yy), W, H), xy((bx, yy), W, H)
    dr.line([p1, p2], fill=RED, width=4)
    for p in (p1, p2):
        dr.ellipse([p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5], fill=(255, 60, 60))
    dr.text((10, p1[1] - 16), lab, fill=(255, 255, 0))
dr.rectangle([0, 0, W, 26], fill=(0, 0, 0))
dr.text((6, 6), 'SWALLOW (fish bolus in neck) - oaBwwXsn_K0 t=33s, GBH', fill=WHT)
img.save(os.path.join(OUT, 'atlas_08_swallow_oaBww.jpg'), quality=88)
jobs.append('atlas_08_swallow_oaBww.jpg')

# 9 stalk crouch grey (GY_stalk)
img = Image.open(os.path.join(K, 'GY_stalk.jpg')).convert('RGB')
pts = {'tip': (243, 548), 'billbase': (359, 510), 'eye': (376, 492), 'back': (447, 474),
       'below': (448, 554), 'mid': (424, 612), 'above': (472, 658), 'base': (514, 693),
       'tail': (917, 689), 'chest': (395, 641), 'backtop': (613, 460), 'belly': (645, 776)}
img = draw(img, pts, [('below', 'mid', GRN, 3), ('mid', 'above', GRN, 3), ('above', 'base', GRN, 3),
                      ('tail', 'chest', BLU, 3)],
           'STALKING CROUCH (neck low, body pitched) - P7Yb_koYsoA t=234s, GREY')
img.save(os.path.join(OUT, 'atlas_09_stalk_crouch_grey.jpg'), quality=88)
jobs.append('atlas_09_stalk_crouch_grey.jpg')

# contact sheet of all
ims = [Image.open(os.path.join(OUT, j)) for j in jobs]
tw = 640
thumbs = []
for im in ims:
    r = tw / im.width
    thumbs.append(im.resize((tw, int(im.height * r))))
cols = 3
rows = (len(thumbs) + cols - 1) // cols
hh = max(t.height for t in thumbs)
sheet = Image.new('RGB', (cols * tw, rows * hh))
for i, t in enumerate(thumbs):
    sheet.paste(t, ((i % cols) * tw, (i // cols) * hh))
sheet.save(os.path.join(OUT, 'atlas_sheet.jpg'), quality=85)
print('atlas done:', jobs)
