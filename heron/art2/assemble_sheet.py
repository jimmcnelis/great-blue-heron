"""Assemble one route's model sheet (4 masters, labeled) + a 100% crops
sheet (512x340 windows centered on each pose's keypoint centroid)."""
import argparse, json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ART2 = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ART2)
import maskrender as M

FD = '/usr/share/fonts/truetype/dejavu/'
def font(name, size):
    try:
        return ImageFont.truetype(FD + name, size)
    except Exception:
        return ImageFont.load_default()

POSES = ['rest', 'front', 'swallow', 'flight']
LABELS = {'rest': 'REST — profile at the waterline',
          'front': 'FRONT',
          'swallow': 'SWALLOW — upright neck, fish bulge mid-neck',
          'flight': 'FLIGHT'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--indir', required=True)
    ap.add_argument('--title', required=True)
    ap.add_argument('--sub', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--cropsout', required=True)
    a = ap.parse_args()
    pj = json.load(open(os.path.join(ART2, 'poses_art2.json')))
    frames = {p: Image.open(os.path.join(a.indir, f'master_{p}.png')).convert('RGB')
              for p in POSES}
    FW, FH = 1024, 600
    margin, lab_h, head_h, gap = 16, 40, 128, 16
    W = margin * 2 + FW * 2 + gap
    H = head_h + 2 * (lab_h + FH) + gap + margin
    sheet = Image.new('RGB', (W, H), (24, 24, 28))
    d = ImageDraw.Draw(sheet)
    d.text((margin, 18), a.title, fill=(255, 255, 255), font=font('DejaVuSans-Bold.ttf', 40))
    d.text((margin, 74), a.sub, fill=(190, 190, 200), font=font('DejaVuSans.ttf', 23))
    for i, p in enumerate(POSES):
        cx = margin + (i % 2) * (FW + gap)
        cy = head_h + (i // 2) * (lab_h + FH + gap)
        d.text((cx + 4, cy + 6), LABELS[p], fill=(255, 210, 120),
               font=font('DejaVuSans-Bold.ttf', 26))
        sheet.paste(frames[p], (cx, cy + lab_h))
    sheet.save(a.out)
    print('sheet ->', a.out, sheet.size)
    # 100% crops
    CW, CH = 512, 340
    crops = Image.new('RGB', (CW * 2 + margin * 2 + gap, CH * 2 + head_h + gap + margin),
                      (24, 24, 28))
    dc = ImageDraw.Draw(crops)
    dc.text((margin, 18), a.title + ' — 100% CROPS', fill=(255, 255, 255),
            font=font('DejaVuSans-Bold.ttf', 34))
    dc.text((margin, 66), 'Unscaled pixel windows from the masters above (512x340 each).',
            fill=(190, 190, 200), font=font('DejaVuSans.ttf', 21))
    for i, p in enumerate(POSES):
        kp = pj['poses'][p]['keypoints_master']
        pts = np.array(M.all_points(kp), float)
        cxp, cyp = pts.mean(axis=0)
        x0 = int(min(max(cxp - CW / 2, 0), FW - CW))
        y0 = int(min(max(cyp - CH / 2, 0), FH - CH))
        crop = frames[p].crop((x0, y0, x0 + CW, y0 + CH))
        ox = margin + (i % 2) * (CW + gap)
        oy = head_h + (i // 2) * (CH + gap)
        crops.paste(crop, (ox, oy))
        dc.rectangle([ox, oy, ox + 190, oy + 32], fill=(24, 24, 28))
        dc.text((ox + 6, oy + 5), LABELS[p].split(' — ')[0], fill=(255, 210, 120),
                font=font('DejaVuSans-Bold.ttf', 22))
    crops.save(a.cropsout)
    print('crops ->', a.cropsout, crops.size)


if __name__ == '__main__':
    main()
