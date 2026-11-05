"""Dump rig v2.5 mechanism data for the warp spike: chains, visible chains,
neckbase, skull, eye anchors, head bill directions, tube widths."""
import sys, json, math
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/heron/art2/rig-v25-gate/iter2')
import rig_v25 as R

out = {}
for pose in ('alert', 'deep_coil', 'strike_peak'):
    img, dv, eye = R.render(pose)
    pts, heads, spec = dv['pts'], dv['heads'], R.ANIMAL['poses'][pose]
    vis, neckbase = R.visible_chain(pts)
    skull = pts[-1]
    final_head = heads[-1] + spec['head_pitch_offset_deg']
    dvec = np.array([math.cos(math.radians(final_head)), math.sin(math.radians(final_head))])
    # full-chain u at each visible-chain point: locate neckbase in dense full chain
    dense_full = R.dense_chain(pts)
    s_full = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(dense_full, axis=0).T))])
    u_full = s_full / s_full[-1]
    # visible dense chain cumulative arc
    s_vis = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(vis, axis=0).T))])
    # widths along visible chain: width profile at full-chain u of nearest dense-full point
    widths = []
    for p in vis:
        d = np.hypot(dense_full[:, 0] - p[0], dense_full[:, 1] - p[1])
        j = int(np.argmin(d))
        w = float(R.width_rest(np.clip(u_full[j], 0, 1))) * R.T
        if spec.get('slimming'):
            w *= float(R.slim_mult(np.clip(u_full[j], 0, 1)))
        widths.append(w)
    out[pose] = dict(
        pts=pts.tolist(), heads=heads.tolist(),
        visible=vis.tolist(), s_vis=s_vis.tolist(), widths_vis=widths,
        neckbase=neckbase.tolist(), skull=skull.tolist(), eye=np.asarray(eye).tolist(),
        bill_dir_deg=float(final_head), dvec=dvec.tolist(),
        chord_base=dv['chord_base'], chord76=dv['chord76'], arc_vis=dv['arc_vis'],
        arc_chord=dv['arc_vis'] / dv['chord_base'])
    print(pose, 'neckbase', np.round(neckbase, 1), 'skull', np.round(skull, 1),
          'eye', np.round(eye, 1), 'bill_dir', round(final_head, 1),
          'chord_base', round(dv['chord_base'], 3), 'chord76', round(dv['chord76'], 3),
          'arc_vis', round(dv['arc_vis'], 3), 'arc:chord', round(dv['arc_vis'] / dv['chord_base'], 2),
          'vis_len_px', round(float(s_vis[-1]), 1))
out['TORSO_PX'] = R.T
out['TORSO_LOOP'] = R.TORSO_LOOP
out['LEGS'] = [[list(a), list(b), list(c)] for a, b, c in R.LEGS]
out['ROOT'] = R.ROOT.tolist()
json.dump(out, open('/home/hatch/workspace/heron/art2/warp-spike-v25/work/mech.json', 'w'), indent=1)
print('TORSO_PX (rig) =', round(R.T, 2))
