"""Build one art2 training sample (.npz) from an annotated frame.

Inputs: source image (frame or plate), alpha PNG (bird alpha 0..255, same
size as source), keypoints JSON (in SOURCE pixel coords, schema per
KEYPOINTS.md), pose JSON (12 floats, ordering per prep_poses.py).
The crop follows maskrender.crop_spec on the keypoints; mask stack and
keypoints are transformed into the 512x512 canonical crop; rgb is the
source bird composited on white using alpha inside the same crop.
"""
import argparse, json, sys, os
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import maskrender as M


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--image', required=True)
    ap.add_argument('--alpha', required=True)
    ap.add_argument('--kp', required=True)
    ap.add_argument('--pose', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    img = Image.open(a.image).convert('RGB')
    alpha = Image.open(a.alpha).convert('L')
    assert img.size == alpha.size, 'image/alpha size mismatch'
    kp = json.load(open(a.kp))
    pose = np.array(json.load(open(a.pose)), np.float32)
    pts = M.all_points(kp)
    x0, y0, side = M.crop_spec(pts)
    S = 512
    sc = S / side

    def tf(p):
        p = np.asarray(p, float)
        return [(p[0] - x0) * sc, (p[1] - y0) * sc]

    kp_c = M.xform_points(kp, tf)
    # px_per_unit in crop coords: source px_per_unit scaled
    src_u = kp.get('_px_per_unit', None)
    scalars = dict(neck_w=float(kp.get('_neck_w', 1.0)),
                   bulge_pos=float(kp.get('_bulge_pos', 0.0)),
                   bulge_amp=float(kp.get('_bulge_amp', 0.0)),
                   px_per_unit=(src_u * sc) if src_u else 6.6667 * sc)
    stack = M.build_mask_stack(kp_c, scalars, (S, S))
    box = (int(round(x0)), int(round(y0)), int(round(x0 + side)), int(round(y0 + side)))
    rgb_c = img.crop(box).resize((S, S), Image.LANCZOS)
    al_c = alpha.crop(box).resize((S, S), Image.LANCZOS)
    white = Image.new('RGB', (S, S), 'white')
    rgb_on_white = Image.composite(rgb_c, white, al_c)
    np.savez_compressed(a.out, mask=stack,
                        rgb=np.asarray(rgb_on_white),
                        alpha=np.asarray(al_c), pose=pose)
    print('sample ->', a.out, 'crop', box)


if __name__ == '__main__':
    main()
