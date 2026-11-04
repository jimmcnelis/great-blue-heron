"""Episode renderer + QA for v1.3 r3 (Naturalist only).
Same episode; cycles13_r3 (swallow reworked) on the leaner rig13.
Writes preview_heron_v1_3_naturalist_r4.mp4, the standard contact strip,
a dedicated swallow strip (full frames + native-res neck crops), and
qa13_r4.json (phase audits + straightness + rendered-bulge descent).
"""
import os, sys, pickle, subprocess, time, json
import numpy as np
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig13_r4 as R
import cycles13 as C2
import cycles13_r4 as C3
import cycles13_r3 as C3R
import ink13 as I

OUT = os.path.expanduser('~/workspace/heron')
TMP = '/tmp/heron13_frames_r4'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def _work(job):
    f0, f1 = job
    with open(f'{TMP}/episode.pkl', 'rb') as fh:
        frames, ink = pickle.load(fh)
    d = f'{TMP}/naturalist'
    os.makedirs(d, exist_ok=True)
    for f in range(f0, f1):
        ev = I.frame_ink(ink, f)
        g = R.render(frames[f], 'naturalist', ink_events=ev)
        Image.fromarray(R.to_rgb(g)).save(f'{d}/f{f:04d}.png')
    return (f0, f1)

def encode():
    out = f'{OUT}/preview_heron_v1_3_naturalist_r4.mp4'
    subprocess.run(['ffmpeg', '-y', '-framerate', '24', '-i',
                    f'{TMP}/naturalist/f%04d.png', '-c:v', 'libx264',
                    '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags',
                    '+faststart', out], check=True, capture_output=True)
    return out

def strip(sel, name, labels=None, tile=(512, 300), cols=4):
    tiles = []
    for f in sel:
        im = Image.open(f'{TMP}/naturalist/f{f:04d}.png').resize(tile)
        tiles.append(im)
    rows = (len(tiles) + cols - 1) // cols
    lab_h = 22 if labels else 0
    sheet = Image.new('RGB', (tile[0] * cols, (tile[1] + lab_h) * rows), 'white')
    dr = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(FONT, 17)
    except Exception:
        font = ImageFont.load_default()
    for i, im in enumerate(tiles):
        x, y = (i % cols) * tile[0], (i // cols) * (tile[1] + lab_h)
        sheet.paste(im, (x, y + lab_h))
        if labels:
            dr.text((x + 8, y + 2), labels[i], fill=(20, 30, 45), font=font)
    sheet.save(f'{OUT}/{name}')
    return f'{OUT}/{name}'

def swallow_strip(frames):
    """Full frames across the eat + native-res neck crops down the bulge."""
    full = [388, 394, 400, 406, 412, 418, 424, 430]
    strip(full, 'v1_3_swallow_strip_r4.jpg',
          labels=['f388 re-catch (head back)', 'f394 rearing up',
                  'f400 neck ~straight', 'f406 bulge high',
                  'f412 bulge mid', 'f418 bulge lower', 'f424 bulge low',
                  'f430 swallow done'],
          tile=(512, 300), cols=4)
    # neck crops at native res: box around the upright neck column
    box = (400, 80, 590, 340)
    crops = [403, 409, 415, 421, 427]
    tiles = []
    for f in crops:
        im = Image.open(f'{TMP}/naturalist/f{f:04d}.png').crop(box)
        tiles.append(im)
    tw, th = box[2] - box[0], box[3] - box[1]
    sheet = Image.new('RGB', (tw * len(tiles), th + 22), 'white')
    dr = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(FONT, 16)
    except Exception:
        font = ImageFont.load_default()
    for i, im in enumerate(tiles):
        sheet.paste(im, (i * tw, 22))
        dr.text((i * tw + 6, 2), 'f%d bulge_pos %.2f' % (crops[i], frames[crops[i]]['bulge_pos']),
                fill=(20, 30, 45), font=font)
    sheet.save(f'{OUT}/v1_3_swallow_crops_r4.jpg')
    return 'v1_3_swallow_crops_r4.jpg'

def breast_of(pose):
    xf, piv = R.body_xform(pose)
    st = R.YAW_STOPS.get(int(round(pose['yaw'])), R.YAW_STOPS[0])
    return np.array(xf((R.BREAST_LOCAL[0] + st['ndx'], R.BREAST_LOCAL[1])))

def straight(pose):
    B = breast_of(pose)
    spine, H = R.neck_spine(pose, B)
    d = H - B
    chord = float(np.hypot(*d))
    ang = float(np.degrees(np.arctan2(abs(d[0]), abs(d[1]))))
    u = d / chord
    rel = spine - B
    perp = rel - np.outer(rel @ u, u)
    return ang, float(np.hypot(perp[:, 0], perp[:, 1]).max()), chord

def audits(frames, ink):
    a = {}
    f2, _ = C2.build_episode()
    diff_out = [f for f in list(range(0, 390)) + list(range(448, C3.N))
                if f2[f] != frames[f]]
    a['pose_frames_differing_outside_swallow_window'] = diff_out
    f3, _ = C3R.build_episode()
    diff_r3 = [f for f in list(range(0, 390)) + list(range(448, C3.N))
               if f3[f] != frames[f]]
    a['pose_frames_differing_vs_r3_outside_window'] = diff_r3
    diff_r3_in = [f for f in range(390, 448) if f3[f] != frames[f]]
    a['pose_frames_differing_vs_r3_inside_window_count'] = len(diff_r3_in)
    same = sum(1 for f in range(449, C3.N) if frames[f] == frames[f - 1])
    a['closing_statue_held_fraction'] = round(same / (C3.N - 449), 3)
    same = sum(1 for f in range(1, 132) if frames[f] == frames[f - 1])
    a['opening_statue_held_fraction'] = round(same / 131, 3)
    tips = [R.bill_tip(frames[f]) for f in range(300, 332)]
    path = [float(np.hypot(*(tips[i + 1] - tips[i]))) for i in range(len(tips) - 1)]
    a['loaded_hold_tip_path_max_per_frame'] = round(max(path[6:22]), 2)
    a['release_tip_peak_speed'] = round(max(path[22:26]), 2)
    a['strike_contact_tip'] = [round(float(v), 1) for v in R.bill_tip(frames[326])]
    a['ink_events'] = len(ink)
    a['fish_airborne_frames'] = sum(1 for f in range(C3.N)
                                    if frames[f]['fish_mode'] == 'free')
    angs = [straight(frames[f])[0] for f in range(402, 432)]
    devs = [straight(frames[f])[1] for f in range(402, 432)]
    a['swallow_bulge_window_402_431'] = dict(
        chord_angle_from_vertical_max_deg=round(max(angs), 2),
        chord_angle_from_vertical_mean_deg=round(float(np.mean(angs)), 2),
        max_spine_deviation_units=round(max(devs), 2),
        max_spine_deviation_px=round(max(devs) * R.U, 1),
        r2_equivalents=dict(chord_angle_max_deg=32.67, max_spine_deviation_units=4.72))
    # BULGE SHAPE, measured identically on the r3 and r4 renders:
    # excess non-white mask vs each version's own f430 (post-swallow)
    # baseline, inside the neck box. The neck stands ~vertical there,
    # so mask width = across-neck, mask height = along-neck.
    def bulge_measure(d):
        base = np.array(Image.open(f'{d}/f0430.png').convert('L')) < 250
        box_b = base[80:340, 400:590]
        rows = {}
        for f in range(403, 432):
            g = np.array(Image.open(f'{d}/f{f:04d}.png').convert('L')) < 250
            m = (g[80:340, 400:590] != box_b)
            ys, xs = np.where(m)
            if len(ys) >= 30:
                rows[f] = dict(area=int(len(ys)),
                               across_px=int(xs.max() - xs.min() + 1),
                               along_px=int(ys.max() - ys.min() + 1),
                               centroid_row=round(float(ys.mean()) + 80, 1))
        if not rows:
            return {}
        peak = max(rows, key=lambda f: rows[f]['area'])
        fs = sorted(rows)
        return dict(peak_frame=peak, peak=rows[peak],
                    travel_px=round(rows[fs[-1]]['centroid_row']
                                    - rows[fs[0]]['centroid_row'], 1),
                    frames_seen=[fs[0], fs[-1]])
    a['bulge_shape_r4'] = bulge_measure(f'{TMP}/naturalist')
    a['bulge_shape_r3_same_method'] = bulge_measure('/tmp/heron13_frames_r3/naturalist')
    # rendered bulge descent: DARKSLATE shadow-slice centroid in the neck box
    cents = {}
    for f in range(402, 432):
        g = np.array(Image.open(f'{TMP}/naturalist/f{f:04d}.png').convert('RGB'))
        box = g[80:340, 400:590]
        m = (np.abs(box.astype(int) - np.array(R.PALETTE[R.DARKSLATE])).sum(axis=2) < 30)
        ys, xs = np.where(m)
        cents[f] = round(float(ys.mean()) + 80, 1) if len(ys) >= 8 else None
    a['bulge_shadow_centroid_rows'] = {str(k): v for k, v in cents.items()
                                       if v is not None}
    got = [(f, c) for f, c in cents.items() if c is not None]
    if got:
        a['bulge_shadow_descent_px'] = round(got[-1][1] - got[0][1], 1)
        a['bulge_shadow_frames_seen'] = [got[0][0], got[-1][0]]
    return a

def main():
    os.makedirs(TMP, exist_ok=True)
    frames, ink = C3.build_episode()
    assert all(f is not None for f in frames)
    with open(f'{TMP}/episode.pkl', 'wb') as fh:
        pickle.dump((frames, ink), fh)
    jobs = [(f0, min(f0 + 40, C3.N)) for f0 in range(0, C3.N, 40)]
    t0 = time.time()
    with Pool(4) as pool:
        for r in pool.imap_unordered(_work, jobs):
            print('done', r, flush=True)
    print('render wall', round(time.time() - t0, 1), 's')
    print('encoded', encode())
    sel = [60, 141, 160, 312, 326, 340, 352, 364, 385, 412, 440, 560]
    strip(sel, 'v1_3_strip_naturalist_r4.jpg')
    print('swallow strip:', swallow_strip(frames))
    a = audits(frames, ink)
    g = np.array(Image.open(f'{TMP}/naturalist/f0060.png'))
    ink_rgb = (g == np.array([0, 0, 0], dtype=np.uint8)).all(axis=2)
    a['ink_pixels_at_rest_f60'] = int(ink_rgb.sum())
    with open(f'{OUT}/src13/qa13_r4.json', 'w') as fh:
        json.dump(a, fh, indent=1)
    print(json.dumps(a, indent=1))

if __name__ == '__main__':
    main()
