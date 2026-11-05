"""Batch 3 gate measurement — batch 1/2 protocol, off the finished PNGs.
Grounding reads are 0-1000 normalized; converted to px on the 1024x600 plate.
Torso T_p = max pairwise distance over tail/chest/backtop/belly.
Skull centre = occiput + 0.052*T_p along bill dir (occiput->billtip axis).
Eye anchor = skull centre + 0.028*T_p along-bill + 0.014*T_p perp-up.
Ripple seat = |ring centre y - joint y| (the rings ARE the waterline,
Jimmy 2026-11-04 12:37); gate: seat <= 0.01*T_p, eye <= 10 px.
Ink: v3 protocol (paper = corner median; content = summed RGB diff > 55;
black = content with mean RGB < 70).
"""
import numpy as np
from PIL import Image

G = {  # normalized grounding reads: tail, chest, backtop, belly, neckbase,
       # occiput, billtip, eye, crown, jointN, ringN, jointF, ringF, emergN, emergF
 'c1': [(101,557),(672,508),(530,150),(505,540),(608,443),(734,109),(865,98),(775,98),(765,81),(388,685),(393,691),(339,685),(346,691),(389,443),(363,443)],
 'c2': [(72,610),(698,502),(472,182),(492,608),(640,450),(715,127),(908,116),(783,121),(768,99),(391,905),(391,912),(328,905),(326,912),(387,562),(345,562)],
 'c3': [(52,638),(650,445),(540,189),(466,664),(598,485),(730,122),(918,112),(781,112),(789,83),(321,834),(321,843),(378,834),(386,843),(337,527),(381,525)],
 'c4': [(53,660),(690,545),(507,189),(498,665),(618,470),(735,125),(912,143),(783,133),(792,108),(385,832),(378,837),(330,838),(320,845),(374,559),(338,556)],
 'c5': [(46,638),(735,555),(545,165),(460,657),(675,495),(749,108),(940,116),(785,113),(802,86),(383,875),(380,890),(314,875),(312,888),(380,520),(343,522)],
 'c6': [(47,642),(761,509),(492,172),(476,633),(735,536),(782,97),(939,95),(819,101),(832,67),(384,821),(387,827),(326,821),(324,827),(385,559),(341,555)],
}
BASE = '/home/hatch/workspace/heron/art2/plates-fresh/batch3/candidates/alert_%s.png'

def px(p): return np.array([p[0] / 1000 * 1024, p[1] / 1000 * 600], float)

def ink(path):
    im = np.asarray(Image.open(path).convert('RGB')).astype(int)
    h, w, _ = im.shape
    corners = np.concatenate([im[:40, :40].reshape(-1, 3), im[:40, -40:].reshape(-1, 3),
                              im[-40:, :40].reshape(-1, 3), im[-40:, -40:].reshape(-1, 3)])
    paper = np.median(corners, axis=0)
    diff = np.abs(im - paper).sum(axis=2)
    content = diff > 55
    black = content & (im.mean(axis=2) < 70)
    return black.mean(), black.sum() / max(content.sum(), 1)

for k, g in G.items():
    tail, chest, back, belly, nb, occ, tip, eye, crown, jN, rN, jF, rF, eN, eF = [px(p) for p in g]
    lm = [tail, chest, back, belly]
    T = max(np.hypot(*(a - b)) for i, a in enumerate(lm) for b in lm[i + 1:])
    dvec = (tip - occ) / np.hypot(*(tip - occ))
    perp = np.array([dvec[1], -dvec[0]])
    skull = occ + 0.052 * T * dvec
    anchor = skull + 0.028 * T * dvec + 0.014 * T * perp
    miss = float(np.hypot(*(eye - anchor)))
    chord = float(np.hypot(*(skull - nb))) / T
    along = float((eye - occ) @ dvec) / T          # drawn occiput->eye along-bill (spec 0.080)
    bill = float(np.hypot(*(tip - skull))) / T
    seatN = abs(rN[1] - jN[1]); seatF = abs(rF[1] - jF[1])
    x0, x1 = tail[0], chest[0]
    emN_x = (eN[0] - x0) / (x1 - x0); emF_x = (eF[0] - x0) / (x1 - x0)
    axis = chest - tail; L2 = axis @ axis
    emN_p = ((eN - tail) @ axis) / L2; emF_p = ((eF - tail) @ axis) / L2
    upN = float(np.hypot(*(eN - jN))) / T; upF = float(np.hypot(*(eF - jF))) / T
    jc_x = ((jN[0] + jF[0]) / 2 - x0) / (x1 - x0)
    bf, bc = ink(BASE % k)
    print(f"{k}: T={T:.1f} chord={chord:.3f} eye_miss={miss:.1f}px along={along:.3f} bill={bill:.3f} "
          f"seatN={seatN:.1f}px({seatN / T:.3f}) seatF={seatF:.1f}px({seatF / T:.3f}) "
          f"emerg_x={emN_x:.3f}/{emF_x:.3f} emerg_p={emN_p:.3f}/{emF_p:.3f} "
          f"upper={upN:.3f}/{upF:.3f} jointc_x={jc_x:.3f} "
          f"frame: crown={crown[1]:.0f} right={1024 - tip[0]:.0f} left={tail[0]:.0f} "
          f"ink f={bf:.4f} c={bc:.3f}")
