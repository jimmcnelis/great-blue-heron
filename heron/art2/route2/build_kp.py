"""Build KEYPOINTS.md-schema kp JSONs + pose JSONs + alphas from kp_raw.json
(visual-grounding points/boxes in 0..1000 normalized coords)."""
import json, math, os
import numpy as np
from PIL import Image
from scipy.spatial import ConvexHull

HERE = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(os.path.join(HERE, 'kp_raw.json')))

POSES = {  # [coil, neck_w, pitch/60, tilt/40, yaw/180, bpos, bamp, flap/60, ftip/30, flight, gape, plume/3]
 'plate_rest_a':    [0.85,1.0,0.08,0.38,0.0,0,0,0,0,0,0,0],
 'plate_rest_b':    [0.80,1.0,0.42,0.38,0.0,0,0,0,0,0,0,0],
 'plate_rest_c':    [0.70,1.0,0.00,0.30,0.0,0,0,0,0,0,0,0],
 'plate_rest_d':    [0.75,1.0,0.17,0.38,0.10,0,0,0,0,0,0,0],
 'plate_coil_a':    [0.95,1.05,0.33,0.45,0.0,0,0,0,0,0,0,0],
 'plate_coil_b':    [1.00,1.10,0.58,0.50,0.0,0,0,0,0,0,0,0],
 'plate_strike_a':  [0.05,0.85,0.50,0.10,0.0,0,0,0,0,0,0,0],
 'plate_swallow_a': [0.02,0.95,-0.92,0.38,0.0,0.45,0.50,0,0,0,0,0],
 'plate_swallow_b': [0.02,0.95,-0.83,0.38,0.0,0.50,0.80,0,0,0,0,0],
 'plate_front_a':   [0.30,1.0,0.33,0.10,0.5,0,0,0,0,0,0,0],
 'plate_front_b':   [0.55,1.0,0.75,0.15,0.5,0,0,0,0,0,0,0],
 'plate_threeq_a':  [0.80,1.0,0.08,0.35,0.25,0,0,0,0,0,0,0],
 'plate_threeq_b':  [0.60,1.0,0.67,0.30,0.30,0,0,0,0,0,0,0],
 'plate_threeq_c':  [0.65,1.0,0.00,0.30,0.25,0,0,0,0,0,0,0],
 'plate_walk_a':    [0.70,1.0,0.00,0.35,0.0,0,0,0,0,0,0,0],
 'plate_walk_b':    [0.60,1.0,0.08,0.30,0.0,0,0,0,0,0,0,0],
 'plate_flight_up_a':   [0.90,1.0,0.0,0.05,0.0,0,0,-0.83,0.33,1,0,0],
 'plate_flight_up_b':   [0.90,1.0,0.0,0.05,0.0,0,0,-0.92,0.33,1,0,0],
 'plate_flight_down_a': [0.90,1.0,0.0,0.05,0.0,0,0,0.25,0.0,1,0,0],
 'plate_flight_down_b': [0.90,1.0,0.0,0.05,0.0,0,0,0.75,0.50,1,0,0],
}
NECK_W = {'plate_coil_b':1.1,'plate_strike_a':0.85,'plate_swallow_a':0.95,'plate_swallow_b':0.95,'plate_coil_a':1.05}
BULGE = {'plate_swallow_a':(0.45,0.50),'plate_swallow_b':(0.50,0.80)}

def ellipse(box, n=12, shrink=0.94):
    x0,y0,x1,y1 = box; cx,cy = (x0+x1)/2,(y0+y1)/2
    rx,ry = (x1-x0)/2*shrink,(y1-y0)/2*shrink
    return [[cx+rx*math.cos(2*math.pi*i/n), cy+ry*math.sin(2*math.pi*i/n)] for i in range(n)]

for name, d in raw.items():
    W,H = d['size']
    P = lambda p: [p[0]/1000*W, p[1]/1000*H]
    pts = {k: P(v) for k,v in d['pts'].items()}
    box = {k: [v[0]/1000*W, v[1]/1000*H, v[2]/1000*W, v[3]/1000*H] for k,v in d['box'].items()}
    flight = name.startswith('plate_flight')
    # spine: 5 pts breast -> head
    base, head = pts['neck_base'], pts['head_c']
    if 'neck_low' in pts:
        spine = [base, pts['neck_low'], pts['neck_mid'], pts['neck_high'], head]
    else:
        mid = pts['neck_mid']
        low = [base[i]+(mid[i]-base[i])*0.5 for i in (0,1)]
        high = [mid[i]+(head[i]-mid[i])*0.5 for i in (0,1)]
        spine = [base, low, mid, high, head]
    # legs: far leg for flight = near offset toward tail
    if 'hip_f' in pts:
        legs = {k: pts[k] for k in ('hip_n','knee_n','foot_n','hip_f','knee_f','foot_f')}
    else:
        legs = {'hip_n':pts['hip_n'],'knee_n':pts['knee_n'],'foot_n':pts['foot_n'],
                'hip_f':[pts['hip_n'][0]-0.02*W, pts['hip_n'][1]-8],
                'knee_f':[pts['knee_n'][0]-0.02*W, pts['knee_n'][1]-8],
                'foot_f':[pts['foot_n'][0]-0.02*W, pts['foot_n'][1]-8]}
    # bill_poly: convex hull of skull-box corners + bill tip
    sx0,sy0,sx1,sy1 = box['skull']
    corners = np.array([[sx0,sy0],[sx1,sy0],[sx1,sy1],[sx0,sy1], pts['bill_tip']])
    hull = ConvexHull(corners)
    bill_poly = [list(corners[i]) for i in hull.vertices]
    # tail
    if 'tail' in box:
        tx0,ty0,tx1,ty1 = box['tail']
        tail_poly = [pts['tail_tip'], [tx1, ty0+0.25*(ty1-ty0)], [tx1, ty1-0.15*(ty1-ty0)]]
    else:  # front view: token tail at torso bottom
        bx0,by0,bx1,by1 = box['torso']; cx = (bx0+bx1)/2
        tail_poly = [[cx-30, by1-50],[cx+30, by1-50],[cx, by1-5]]
        pts['tail_tip'] = [cx, by1-10]
    if flight:
        ppu = (box['torso'][2]-box['torso'][0])/37.0
    else:
        ppu = (legs['foot_n'][1]-box['skull'][1])/62.0
    # torso: TRUE anatomical body line — for standing birds the bottom of
    # the fitted ellipse is tucked up ~12% so it does not wrap the plume
    # skirt (the skirt lives only in plume_poly, channel 7).
    tbox = list(box['torso'])
    if not flight:
        tbox[3] = tbox[1] + 0.88 * (tbox[3] - tbox[1])
    pbox = [d['plume'][0]/1000*W, d['plume'][1]/1000*H,
            d['plume'][2]/1000*W, d['plume'][3]/1000*H]
    kp = {'torso_poly': ellipse(tbox), 'spine': spine,
          'plume_poly': ellipse(pbox, n=10, shrink=0.95),
          'head_c': head, 'bill_tip': pts['bill_tip'], 'bill_poly': bill_poly,
          'wing_poly': ellipse(box['wing'], n=10, shrink=0.92),
          'tail_poly': tail_poly, '_px_per_unit': float(ppu),
          '_neck_w': NECK_W.get(name, 1.0), **legs}
    bp, ba = BULGE.get(name, (0.0,0.0))
    kp['_bulge_pos'], kp['_bulge_amp'] = bp, ba
    os.makedirs(os.path.join(HERE,'kp'), exist_ok=True)
    json.dump(kp, open(os.path.join(HERE,'kp',name+'.json'),'w'))
    json.dump(POSES[name], open(os.path.join(HERE,'kp',name+'_pose.json'),'w'))
    print(name, 'ppu %.1f' % ppu)
print('kp built:', len(raw))
