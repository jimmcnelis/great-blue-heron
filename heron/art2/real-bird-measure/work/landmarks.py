#!/usr/bin/env python3
"""Landmark sets from visual grounding (0-1000 coords) -> normalized ratios.
Frames are 1280x720 unless noted. skull = midpoint(eye, back_of_head)."""
import json, math

def P(x, y, W=1280, H=720):
    return (x / 1000 * W, y / 1000 * H)

def d(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def polyline(pts):
    return sum(d(pts[i], pts[i + 1]) for i in range(len(pts) - 1))

def point_at_frac(pts, f):
    total = polyline(pts)
    target = f * total
    acc = 0.0
    for i in range(len(pts) - 1):
        L = d(pts[i], pts[i + 1])
        if acc + L >= target:
            t = 0.0 if L == 0 else (target - acc) / L
            return (pts[i][0] + t * (pts[i + 1][0] - pts[i][0]),
                    pts[i][1] + t * (pts[i + 1][1] - pts[i][1]))
        acc += L
    return pts[-1]

def measure(name, raw, neck_keys, W=1280, H=720):
    p = {k: P(*v, W, H) for k, v in raw.items()}
    skull = ((p['eye'][0] + p['back'][0]) / 2, (p['eye'][1] + p['back'][1]) / 2)
    chain = [skull] + [p[k] for k in neck_keys] + [p['neckbase']]
    arc = polyline(chain)
    s1 = point_at_frac(chain, 0.76)
    torso_pts = [p['tail'], p['chest'], p['backtop'], p['belly']]
    torso = max(d(a, b) for i, a in enumerate(torso_pts) for b in torso_pts[i + 1:])
    out = dict(
        bill=d(p['tip'], p['billbase']), head=d(p['tip'], p['back']),
        neck_arc=arc, chord76=d(skull, s1), chord_base=d(skull, p['neckbase']),
        torso=torso, depth=d(p['backtop'], p['belly']),
        bill_over_torso=d(p['tip'], p['billbase']) / torso,
        head_over_torso=d(p['tip'], p['back']) / torso,
        chord76_over_torso=d(skull, s1) / torso,
        arc_over_torso=arc / torso,
        chordbase_over_torso=d(skull, p['neckbase']) / torso,
        depth_over_torso=d(p['backtop'], p['belly']) / torso,
        bill_over_head=d(p['tip'], p['billbase']) / d(p['tip'], p['back']),
        bill_over_neckrun=d(p['tip'], p['billbase']) / d(skull, s1) if d(skull, s1) else None,
    )
    print(f'{name}: ' + ' '.join(f'{k}={v:.3f}' if isinstance(v, float) and v < 10
                                  else f'{k}={v:.1f}' for k, v in out.items()))
    return out

SETS = {
    'UR_tall': ({'tip': (373, 80), 'base': (468, 48), 'eye': (498, 26), 'back': (556, 68),
                 'tail': (744, 962), 'chest': (533, 538), 'backtop': (607, 437), 'belly': (614, 823)},
                ['q1', 'q2', 'q3']),
    'UR_early': ({'tip': (346, 480), 'base': (405, 310), 'eye': (413, 275), 'back': (483, 233),
                  'tail': (862, 477), 'chest': (498, 438), 'backtop': (613, 272), 'belly': (700, 515)},
                 ['mid']),
    'BC_stand': ({'tip': (611, 594), 'base': (560, 533), 'eye': (545, 498), 'back': (499, 473),
                  'tail': (205, 615), 'chest': (470, 647), 'backtop': (351, 453), 'belly': (303, 717)},
                 ['below', 'mid', 'above']),
    'MU_stand2': ({'tip': (415, 270), 'base': (452, 250), 'eye': (465, 232), 'back': (480, 225),
                   'tail': (637, 617), 'chest': (450, 550), 'backtop': (515, 428), 'belly': (545, 595)},
                  ['below', 'mid', 'above']),
    'GY_stand': ({'tip': (535, 178), 'base': (600, 172), 'eye': (622, 166), 'back': (650, 161),
                  'tail': (880, 803), 'chest': (618, 535), 'backtop': (693, 403), 'belly': (701, 668)},
                 ['below', 'mid', 'above']),
    'GY_stalk': ({'tip': (243, 548), 'base': (359, 510), 'eye': (376, 492), 'back': (447, 474),
                  'tail': (917, 689), 'chest': (395, 641), 'backtop': (613, 460), 'belly': (645, 776)},
                 ['below', 'mid', 'above']),
}
# neck point coords (0-1000) per frame
NECK = {
    'UR_tall': {'q1': (536, 165), 'q2': (545, 270), 'q3': (553, 365)},
    'UR_early': {'mid': (467, 355)},
    'BC_stand': {'below': (504, 530), 'mid': (474, 579), 'above': (456, 619)},
    'MU_stand2': {'below': (477, 300), 'mid': (462, 405), 'above': (460, 505)},
    'GY_stand': {'below': (635, 254), 'mid': (628, 368), 'above': (638, 466)},
    'GY_stalk': {'below': (448, 554), 'mid': (424, 612), 'above': (472, 658)},
}
BASE = {
    'UR_tall': (570, 460), 'UR_early': (543, 410), 'BC_stand': (442, 642),
    'MU_stand2': (475, 535), 'GY_stand': (648, 497), 'GY_stalk': (514, 693),
}
if __name__ == '__main__':
    res = {}
    for name, (raw, keys) in SETS.items():
        raw2 = dict(raw)
        raw2.update({k: NECK[name][k] for k in keys})
        raw2['billbase'] = raw2.pop('base'); raw2['neckbase'] = BASE[name]
        res[name] = measure(name, raw2, keys)
    json.dump(res, open('work/landmark_ratios.json', 'w'), indent=1)
