#!/usr/bin/env python3
"""Addendum atlas: draw recorded addendum landmarks on key frames. Coords 0-1000."""
import os
from PIL import Image, ImageDraw

B = os.path.expanduser('~/workspace/heron/art2/real-bird-measure')
F = os.path.join(B, 'frames')
OUT = os.path.join(B, 'atlas_addendum')
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
    dr.rectangle([0, 0, W, 30], fill=(0, 0, 0))
    dr.text((6, 8), label, fill=(255, 255, 255))
    return img

RED = (255, 60, 60); BLU = (60, 140, 255); GRN = (60, 255, 120); WHT = (255, 255, 255)
jobs = []

def full_pts(raw):
    pts = dict(raw)
    pts['skull'] = ((raw['eye'][0] + raw['back'][0]) / 2, (raw['eye'][1] + raw['back'][1]) / 2)
    return pts

FULL_LINES = [('tip', 'billbase', RED, 3), ('skull', 'mid', GRN, 3), ('mid', 'neckbase', GRN, 3),
              ('skull', 'neckbase', RED, 3), ('tail', 'chest', BLU, 3)]

# A1 DS2 peak (slow glean-spear), davesmith 61-68 window f88, t=63.90
img = Image.open(os.path.join(F, 'fb-davesmith-strike_61.0-68.0', 'f0088.jpg')).convert('RGB')
pts = full_pts({'tip': (820, 945), 'billbase': (812, 903), 'eye': (811, 879), 'back': (785, 850),
                'mid': (675, 850), 'neckbase': (563, 778), 'tail': (110, 819), 'chest': (528, 796),
                'backtop': (471, 698), 'belly': (369, 824)})
img = draw(img, pts, FULL_LINES, 'A1 DS2 PEAK slow glean-spear - fb-davesmith-strike t=63.90s GBH - chord76 0.508, chord_base 0.668')
img.save(os.path.join(OUT, 'atlasA_01_DS2_peak.jpg'), quality=88); jobs.append('atlasA_01_DS2_peak.jpg')

# A2 DS2 alert/coil f10, t=61.30
img = Image.open(os.path.join(F, 'fb-davesmith-strike_61.0-68.0', 'f0010.jpg')).convert('RGB')
pts = full_pts({'tip': (864, 748), 'billbase': (771, 695), 'eye': (729, 677), 'back': (628, 663),
                'mid': (709, 737), 'neckbase': (608, 782), 'tail': (183, 892), 'chest': (642, 803),
                'backtop': (498, 715), 'belly': (369, 861)})
img = draw(img, pts, FULL_LINES, 'A2 DS2 ALERT (pre-stab) - fb-davesmith-strike t=61.30s GBH - chord_base 0.435')
img.save(os.path.join(OUT, 'atlasA_02_DS2_alert.jpg'), quality=88); jobs.append('atlasA_02_DS2_alert.jpg')

# A3 DS1 peak f21 (head-centre method), 7-14 window, t=7.667
img = Image.open(os.path.join(F, 'fb-davesmith-strike_7.0-14.0', 'f0021.jpg')).convert('RGB')
pts = {'head': (555, 868), 'tip': (615, 880), 'base': (185, 830)}
img = draw(img, pts, [('head', 'base', RED, 4), ('head', 'tip', RED, 3)],
           'A3 DS1 PEAK spear (torso out of frame; timing/profile only) - fb-davesmith-strike t=7.667s - chord 424px peak')
img.save(os.path.join(OUT, 'atlasA_03_DS1_peak.jpg'), quality=88); jobs.append('atlasA_03_DS1_peak.jpg')

# A4 57Y plunge peak f90, t=136.97
img = Image.open(os.path.join(F, '57YcyG5VrYI_134.0-150.0', 'f0090.jpg')).convert('RGB')
pts = full_pts({'tip': (795, 755), 'billbase': (740, 740), 'eye': (710, 730), 'back': (685, 715),
                'mid': (595, 700), 'neckbase': (505, 650), 'tail': (278, 530), 'chest': (490, 670),
                'backtop': (382, 466), 'belly': (438, 708)})
img = draw(img, pts, FULL_LINES, 'A4 57Y PEAK lunge-plunge - 57YcyG5VrYI t=136.97s GBH - chord76 0.662, chord_base 0.870')
img.save(os.path.join(OUT, 'atlasA_04_57Y_peak.jpg'), quality=88); jobs.append('atlasA_04_57Y_peak.jpg')

# A5 57Y crouch-coil f75, t=136.47
img = Image.open(os.path.join(F, '57YcyG5VrYI_134.0-150.0', 'f0075.jpg')).convert('RGB')
pts = full_pts({'tip': (666, 696), 'billbase': (592, 622), 'eye': (573, 602), 'back': (522, 583),
                'mid': (533, 660), 'neckbase': (465, 663), 'tail': (249, 376), 'chest': (436, 677),
                'backtop': (341, 437), 'belly': (386, 709)})
img = draw(img, pts, FULL_Lines if False else FULL_LINES, 'A5 57Y CROUCH (walking coil, pre-lunge) - 57YcyG5VrYI t=136.47s GBH - chord_base 0.363')
img.save(os.path.join(OUT, 'atlasA_05_57Y_crouch.jpg'), quality=88); jobs.append('atlasA_05_57Y_crouch.jpg')

# A6 57Y deep coil portrait f91 (124-132 window), t=127.0 - no torso (tail cropped); arc:chord only
img = Image.open(os.path.join(F, '57YcyG5VrYI_124.0-132.0', 'f0091.jpg')).convert('RGB')
pts = {'eye': (575, 320), 'back': (405, 330), 'tip': (826, 387), 'billbase': (627, 334),
       'slow': (559, 648), 'neckbase': (428, 610)}
pts['skull'] = ((575 + 405) / 2, (320 + 330) / 2)
img = draw(img, pts, [('tip', 'billbase', RED, 3), ('skull', 'slow', GRN, 4), ('slow', 'neckbase', GRN, 4),
                      ('skull', 'neckbase', RED, 3)],
           'A6 57Y DEEP COIL portrait (torso cropped; arc:chord = 1.90 floor) - 57YcyG5VrYI t=127.0s GBH')
img.save(os.path.join(OUT, 'atlasA_06_57Y_deepcoil.jpg'), quality=88); jobs.append('atlasA_06_57Y_deepcoil.jpg')

# A7 SF peak f57 (OBLIQUE - floor only)
img = Image.open(os.path.join(F, 'fb-samrino-120p-fishing_4.0-16.0', 'f0057.jpg')).convert('RGB')
pts = full_pts({'tip': (684, 764), 'billbase': (658, 745), 'eye': (642, 732), 'back': (625, 710),
                'mid': (582, 714), 'neckbase': (505, 625), 'tail': (71, 510), 'chest': (468, 648),
                'backtop': (350, 489), 'belly': (322, 676)})
img = draw(img, pts, FULL_LINES, 'A7 SF PEAK (3/4 view - chord76 0.343 is a FLOOR, not pooled) - fb-samrino-120p-fishing t=6.33s render')
img.save(os.path.join(OUT, 'atlasA_07_SF_peak_oblique.jpg'), quality=88); jobs.append('atlasA_07_SF_peak_oblique.jpg')

# A8 swallow bulge f337 (58-82 window), t=72.0 render
img = Image.open(os.path.join(F, 'fb-samrino-swallow-throat_58.0-82.0', 'f0337.jpg')).convert('RGB')
pts = {'bulgeL': (340, 412), 'bulgeR': (450, 405), 'neckL': (279, 369), 'neckR': (415, 368),
       'tail': (3, 484), 'chest': (419, 542), 'backtop': (203, 372), 'belly': (42, 627)}
img = draw(img, pts, [('bulgeL', 'bulgeR', WHT, 4), ('neckL', 'neckR', WHT, 3), ('tail', 'chest', BLU, 3)],
           'A8 SMALL FISH MID-SWALLOW at throat entrance, gape max (white bar = fish width at throat) - fb-samrino-swallow-throat t=72.0s render, rate-flagged')
img.save(os.path.join(OUT, 'atlasA_08_swallow_bulge.jpg'), quality=88); jobs.append('atlasA_08_swallow_bulge.jpg')

# A9 Wilson gait f97 - leg spread + torso
img = Image.open(os.path.join(F, 'ig-wilson-donriver-stalk_118.0-134.0', 'f0097.jpg')).convert('RGB')
pts = {'ffoot': (585, 765), 'rfoot': (632, 745), 'tail': (918, 673), 'chest': (413, 543),
       'backtop': (534, 480), 'belly': (605, 638)}
img = draw(img, pts, [('tail', 'chest', BLU, 3), ('ffoot', 'rfoot', WHT, 3)],
           'A9 STALK mid-step (head frozen, feet close at placement) - ig-wilson t=121.2s juvenile GBH')
img.save(os.path.join(OUT, 'atlasA_09_wilson_gait.jpg'), quality=88); jobs.append('atlasA_09_wilson_gait.jpg')

# A10 tree-stretch full spread (label only), f127 of 16-25 window, t=20.2 render
img = Image.open(os.path.join(F, 'fb-boga-tree-stretch_16.0-25.0', 'f0127.jpg')).convert('RGB')
img = draw(img, {}, [], 'A10 POST-LANDING WING SPREAD, full hold - fb-boga-tree-stretch t=20.2s (Boga rate-suspect)')
img.save(os.path.join(OUT, 'atlasA_10_tree_stretch_spread.jpg'), quality=88); jobs.append('atlasA_10_tree_stretch_spread.jpg')

# A11 weber takeoff liftoff f49 (label only), t=20.60 - neck extended
img = Image.open(os.path.join(F, 'fb-weber-duty_19.0-24.0', 'f0049.jpg')).convert('RGB')
img = draw(img, {}, [], 'A11 TAKEOFF LIFTOFF - neck still EXTENDED - fb-weber-duty t=20.60s')
img.save(os.path.join(OUT, 'atlasA_11_takeoff_liftoff.jpg'), quality=88); jobs.append('atlasA_11_takeoff_liftoff.jpg')

# A12 weber fold complete f85 (label only), t=21.80 - neck folded (f61 was mid-retraction)
img = Image.open(os.path.join(F, 'fb-weber-duty_19.0-24.0', 'f0085.jpg')).convert('RGB')
img = draw(img, {}, [], 'A12 FLIGHT - neck folded into cruise S (+1.2s after liftoff; fold complete by ~+0.5s) - fb-weber-duty t=21.80s')
img.save(os.path.join(OUT, 'atlasA_12_flight_folded.jpg'), quality=88); jobs.append('atlasA_12_flight_folded.jpg')

print('\n'.join(jobs))
