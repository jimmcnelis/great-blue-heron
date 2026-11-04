"""Segment the heron in each selected frame with rembg isnet-general-use
on a crop around the bird; keep the largest connected component; paste
alpha back to full-frame size. Prints bbox/area per frame for yield log."""
import os, sys
import numpy as np
from PIL import Image
import cv2
from rembg import remove, new_session

ART2 = os.path.expanduser('~/workspace/heron/art2')
R1 = os.path.join(ART2, 'route1')
os.makedirs(os.path.join(R1, 'alpha'), exist_ok=True)

FRAMES = {  # name -> (image path, crop box x0,y0,x1,y1)
 'day_2':  ('frames/day_2.jpg',  (620, 270, 900, 530)),
 'day_5':  ('frames/day_5.jpg',  (540, 270, 820, 530)),
 'day_8':  ('frames/day_8.jpg',  (470, 260, 790, 530)),
 'day_11': ('frames/day_11.jpg', (420, 280, 700, 530)),
 'day_14': ('frames/day_14.jpg', (290, 270, 650, 530)),
 'day_17': ('frames/day_17.jpg', (270, 300, 540, 540)),
 'day_20': ('frames/day_20.jpg', (210, 290, 470, 540)),
 'day_23': ('frames/day_23.jpg', (230, 300, 480, 540)),
 'day_27': ('frames/day_27.jpg', (170, 190, 490, 510)),
 'day_31': ('frames/day_31.jpg', (200, 200, 490, 510)),
 'day_34': ('frames/day_34.jpg', (210, 250, 460, 510)),
 'day_36': ('frames/day_36.jpg', (110, 250, 460, 510)),
 'day_38': ('frames/day_38.jpg', (150, 280, 450, 510)),
 'day_40': ('frames/day_40.jpg', (110, 260, 460, 510)),
 'sun_2':   ('frames/sun_2.jpg',   (1100, 0, 1280, 120)),
 'sun_4.4': ('frames/sun_4.4.jpg', (170, 370, 430, 550)),
 'sun_5':   ('frames/sun_5.jpg',   (390, 390, 570, 570)),
 'sun_6':   ('frames/sun_6.jpg',   (470, 450, 630, 630)),
 'sun_8':   ('frames/sun_8.jpg',   (510, 460, 670, 610)),
 'sun_10':  ('frames/sun_10.jpg',  (530, 460, 680, 600)),
 'still_a': ('../reference/real-heron-a.jpg', None),
 'still_b': ('../reference/real-heron-b.jpg', None),
}

session = new_session('isnet-general-use')
only = sys.argv[1:] or list(FRAMES)
for name in only:
    rel, box = FRAMES[name]
    img = Image.open(os.path.join(ART2, rel)).convert('RGB')
    W, H = img.size
    if box is None:
        box = (0, 0, W, H)
    crop = img.crop(box)
    out = remove(crop, session=session)
    a = np.asarray(out.split()[3])
    raw = np.zeros((H, W), np.uint8); raw[box[1]:box[3], box[0]:box[2]] = a; os.makedirs(os.path.join(R1, "alpha_raw"), exist_ok=True); Image.fromarray(raw).save(os.path.join(R1, "alpha_raw", name + ".png"))
    # largest connected component of alpha>40
    m = (a > 40).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
    if n > 1:
        big = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        a = np.where(lab == big, a, 0).astype(np.uint8)
    full = np.zeros((H, W), np.uint8)
    full[box[1]:box[3], box[0]:box[2]] = a
    Image.fromarray(full).save(os.path.join(R1, 'alpha', name + '.png'))
    ys, xs = np.where(full > 100)
    if len(xs):
        print(f'{name}: bbox x {xs.min()}-{xs.max()} y {ys.min()}-{ys.max()} '
              f'area {int((full>40).sum())} comps {n-1}')
    else:
        print(f'{name}: EMPTY')
print('SEG DONE')
