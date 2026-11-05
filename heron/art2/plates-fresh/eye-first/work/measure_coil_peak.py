"""COIL+PEAK eye-first batch — DIAGNOSTICS ONLY (not gates, not selection).
Same protocol as measure_top3.py: grounding 0-1000 -> px on 1024x600;
T_p = max pairwise over tail/chest/backtop/belly; skull = occiput + 0.052*T_p
along bill axis; eye anchor = skull + 0.028*T_p along + 0.014*T_p perp-up;
ink by the v3 protocol."""
import numpy as np
from PIL import Image

# tail, chest, backtop, belly, neckbase, occiput, billtip, eye,
# then coil: jointN, ringN, jointF, ringF | peak: ringBill
G = {
 'coil_c7': [(49,499),(612,554),(524,158),(415,568),(617,374),(800,314),(812,786),(838,462),(394,685),(395,896),(340,681),(328,898)],
 'coil_c2': [(53,513),(658,614),(508,192),(332,577),(645,385),(788,382),(864,756),(831,458),(393,701),(399,890),(356,681),(329,891)],
 'coil_c1': [(49,514),(671,527),(473,205),(448,563),(630,365),(800,300),(783,710),(810,438),(395,697),(400,894),(352,690),(328,894)],
 'peak_c6': [(44,416),(623,484),(547,124),(415,497),(634,388),(760,540),(866,914),(808,678),(863,911)],
 'peak_c2': [(20,327),(566,471),(475,198),(357,444),(607,374),(795,553),(895,903),(847,682),(891,907)],
 'peak_c4': [(86,423),(600,460),(512,168),(415,493),(628,371),(748,550),(868,902),(803,662),(865,914)],
}
BASE = '/home/hatch/workspace/heron/art2/plates-fresh/eye-first/%s/candidates/%s.png'

def px(p): return np.array([p[0]/1000*1024, p[1]/1000*600], float)

def ink(path):
    im = np.asarray(Image.open(path).convert('RGB')).astype(int)
    corners = np.concatenate([im[:40,:40].reshape(-1,3), im[:40,-40:].reshape(-1,3),
                              im[-40:,:40].reshape(-1,3), im[-40:,-40:].reshape(-1,3)])
    paper = np.median(corners, axis=0)
    diff = np.abs(im - paper).sum(axis=2)
    content = diff > 55
    black = content & (im.mean(axis=2) < 70)
    return black.mean(), black.sum()/max(content.sum(),1)

for k, g in G.items():
    pose = k.split('_')[0]
    tail, chest, back, belly, nb, occ, tip, eye = [px(p) for p in g[:8]]
    lm = [tail, chest, back, belly]
    T = max(np.hypot(*(a-b)) for i,a in enumerate(lm) for b in lm[i+1:])
    dvec = (tip-occ)/np.hypot(*(tip-occ)); perp = np.array([dvec[1], -dvec[0]])
    skull = occ + 0.052*T*dvec
    anchor = skull + 0.028*T*dvec + 0.014*T*perp
    miss = float(np.hypot(*(eye-anchor)))
    chord = float(np.hypot(*(skull-nb)))/T
    bill = float(np.hypot(*(tip-skull)))/T
    bf, bc = ink(BASE % (pose, k))
    out = (f"{k}: T={T:.1f}px chord_base={chord:.3f} eye_miss={miss:.1f}px bill={bill:.3f} "
           f"ink_frame={bf:.4f} ink_content_black={bc:.3f}")
    if pose == 'coil':
        jN, rN, jF, rF = [px(p) for p in g[8:12]]
        out += (f" ripple_seat near={abs(rN[1]-jN[1]):.0f}px({abs(rN[1]-jN[1])/T:.3f}T)"
                f" far={abs(rF[1]-jF[1]):.0f}px({abs(rF[1]-jF[1])/T:.3f}T)")
    else:
        rb = px(g[8])
        d = float(np.hypot(*(rb-tip)))
        out += (f" bill_ring_offset={d:.0f}px({d/T:.3f}T) chord76_est={0.78*chord:.3f}")
    print(out)
