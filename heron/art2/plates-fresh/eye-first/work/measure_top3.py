"""Eye-first batch — DIAGNOSTICS ONLY (not gates, not selection).
Same protocol as batch3/work/measure.py: grounding 0-1000 -> px on 1024x600;
T_p = max pairwise over tail/chest/backtop/belly; skull centre = occiput +
0.052*T_p along bill axis; eye anchor = skull + 0.028*T_p along + 0.014*T_p
perp-up; ripple seat = |ring y - joint y|; ink v3 protocol."""
import numpy as np
from PIL import Image

G = {  # tail, chest, backtop, belly, neckbase, occiput, billtip, eye, crown,
       # jointN, ringN, jointF, ringF, emergN, emergF
 'c3': [(25,537),(637,462),(497,235),(446,578),(658,393),(728,100),(954,120),(803,114),(781,78),(394,694),(395,875),(342,680),(331,873),(384,549),(338,557)],
 'c1': [(92,537),(627,475),(476,167),(512,557),(654,392),(740,82),(896,87),(792,78),(773,55),(394,717),(395,913),(340,736),(324,915),(382,538),(342,525)],
 'c5': [(62,580),(638,472),(483,171),(453,572),(618,370),(705,128),(898,127),(763,122),(750,106),(338,607),(333,737),(386,615),(388,735),(356,518),(387,529)],
}
BASE = '/home/hatch/workspace/heron/art2/plates-fresh/eye-first/candidates/alert_%s.png'

def px(p): return np.array([p[0] / 1000 * 1024, p[1] / 1000 * 600], float)

def ink(path):
    im = np.asarray(Image.open(path).convert('RGB')).astype(int)
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
    bill = float(np.hypot(*(tip - skull))) / T
    seatN = abs(rN[1] - jN[1]); seatF = abs(rF[1] - jF[1])
    x0, x1 = tail[0], chest[0]
    emN_x = (eN[0] - x0) / (x1 - x0); emF_x = (eF[0] - x0) / (x1 - x0)
    jc_x = ((jN[0] + jF[0]) / 2 - x0) / (x1 - x0)
    bf, bc = ink(BASE % k)
    print(f"{k}: T={T:.1f}px chord_base={chord:.3f} eye_miss={miss:.1f}px bill={bill:.3f} "
          f"seatN={seatN:.0f}px({seatN / T:.3f}T) seatF={seatF:.0f}px({seatF / T:.3f}T) "
          f"emerg_x near/far={emN_x:.3f}/{emF_x:.3f} jointcentre_x={jc_x:.3f} "
          f"frame: crown_top={crown[1]:.0f}px right_margin={1024 - tip[0]:.0f}px tail_left={tail[0]:.0f}px "
          f"ring_bottom~{max(rN[1], rF[1]):.0f}px ink_frame={bf:.4f} ink_content_black={bc:.3f}")
