#!/usr/bin/env python3
"""Band pass, phase 2: exchange-rate probes from the v2.3 base.

One evaluation per (knob, direction) from the baked v2.3 state,
logging all three surfaces. This measures what each lever charges
in IoU for what it pays in band error -- the trade curve's raw
material, and the evidence for whether a cheaper path than the
main descent's keel-first route exists.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import band_core as B

LOGF = open(f'{B.OUT}/probe_log_v24.jsonl', 'a')
base = dict(B.INIT_STATE)
_, _, bm, _, _ = B.evaluate(base)
print(f"BASE raw={bm['raw']:.4f} bird={bm['bird']:.4f} band_err={bm['band_err']:.4f}", flush=True)

PROBES = ([(k, s) for k, s in (('t_keel', 1.2), ('t_bl', 1.2), ('t_crown', 1.2),
                               ('t_bk', 1.2), ('t_taildx', 1.5), ('t_brdx', 1.2),
                               ('t_taildy', 1.2), ('w_top', 1.0), ('w_bot', 1.0),
                               ('w_fwd', 1.0))]
          + [(f'tp{i}y', 0.6) for i in range(13)]
          + [(f'tp{i}x', 0.6) for i in (0, 1, 5, 6, 9, 12)]
          + [(f'wp{i}y', 0.6) for i in (5, 6, 7)])

rows = []
for key, step in PROBES:
    for sgn in (1, -1):
        st = dict(base); st[key] = base.get(key, 0.0) + sgn * step
        _, _, m, _, _ = B.evaluate(st)
        e = dict(tag=f'probe-{key}{"+" if sgn > 0 else "-"}', key=key, step=sgn * step,
                 delta=B.nonzero_state(st),
                 **{k: m[k] for k in ('raw', 'bird', 'bands', 'band_err', 'mid_err',
                                      'centroid', 'fwd_err', 'torso_w', 'len_err', 'sec_err',
                                      'ok', 'floors_ok')})
        LOGF.write(json.dumps(e) + '\n'); LOGF.flush()
        d_be = m['band_err'] - bm['band_err']
        d_raw = m['raw'] - bm['raw']; d_bird = m['bird'] - bm['bird']
        rows.append((key, sgn * step, d_be, d_raw, d_bird, m))
        print(f"probe {key:9s} {sgn*step:+.1f}  band_err={m['band_err']:.4f} (d {d_be:+.4f})  "
              f"raw={m['raw']:.4f} (d {d_raw:+.4f})  bird={m['bird']:.4f} (d {d_bird:+.4f})  "
              f"mid={m['bands']['band1']:.4f} len={m['torso_w']:.3f} ok={m['ok']}", flush=True)

print('\n-- band-improving probes, ranked by band gain per unit of IoU budget spent')
print('   (budget spent = max(-d_raw/0.0221, -d_bird/0.0256), the v2.3->floor spans)')
imp = [r for r in rows if r[2] < -0.0005 and r[5]['ok']]
for key, stp, d_be, d_raw, d_bird, m in sorted(imp, key=lambda r: r[2] / max(max(-r[3] / 0.0221, -r[4] / 0.0256), 0.02)):
    spent = max(-d_raw / 0.0221, -d_bird / 0.0256)
    print(f"  {key:9s} {stp:+.1f}  d_band={d_be:+.4f}  d_raw={d_raw:+.4f}  d_bird={d_bird:+.4f}  "
          f"budget_spent={spent:.3f}  eff={-d_be / max(spent, 0.02):.4f}")
with open(f'{B.OUT}/probe_results_v24.json', 'w') as f:
    json.dump([dict(key=r[0], step=r[1], d_band_err=r[2], d_raw=r[3], d_bird=r[4],
                    metrics={k: r[5][k] for k in ('raw', 'bird', 'bands', 'band_err', 'torso_w', 'sec_err')})
               for r in rows], f, indent=1)
print('PROBES DONE')
