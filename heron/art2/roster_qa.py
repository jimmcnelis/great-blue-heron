"""Aggregate roster QA against the Fix-1 gates. Reads qa_<chart>.json
files from the render output dir; prints a per-chart table + failed
frame lists; writes qa_summary.json."""
import json, os, sys
import numpy as np

OUT = sys.argv[1]
FLIGHTY = {'flight_cycle', 'glide', 'takeoff', 'landing'}
G = {'checker_max': 0.01, 'head_min': 0.041,
     'leg_n_max': 11.0, 'leg_f_max': 8.0, 'tex_lo': 0.025, 'tex_hi': 0.048}

summary = {}
for f in sorted(os.listdir(OUT)):
    if not (f.startswith('qa_') and f.endswith('.json')):
        continue
    if f == 'qa_summary.json':
        continue
    chart = f[3:-5]
    qa = json.load(open(os.path.join(OUT, f)))
    tags = sorted(qa.keys())
    def col(k):
        return [qa[t][k] for t in tags]
    tex, chk, head = col('texture'), col('checker'), col('head_alpha_occ')
    ln, lf = col('leg_n'), col('leg_f')
    def fails(vals, pred):
        return [int(t[1:]) for t, v in zip(tags, vals)
                if v is not None and pred(v)]
    s = {
        'frames': len(tags),
        'texture_min_med_max': [min(x for x in tex if x is not None),
                                float(np.median([x for x in tex if x is not None])),
                                max(x for x in tex if x is not None)],
        'checker_absmax': max(abs(x) for x in chk if x is not None),
        'head_occ_min': min(x for x in head if x is not None),
        'head_occ_none': sum(1 for x in head if x is None),
        'leg_n_max': max((x for x in ln if x), default=None),
        'leg_f_max': max((x for x in lf if x), default=None),
        'fail_checker': fails(chk, lambda v: abs(v) > G['checker_max']),
        'fail_head': fails(head, lambda v: v < G['head_min']),
        'fail_tex': fails(tex, lambda v: v < G['tex_lo'] or v > G['tex_hi']),
        'fail_legs': [] if chart in FLIGHTY else
            [int(t[1:]) for t, a, b in zip(tags, ln, lf)
             if (a is not None and a > G['leg_n_max'])
             or (b is not None and b > G['leg_f_max'])],
    }
    summary[chart] = s
    print(f"{chart:14s} n={s['frames']:4d} tex {s['texture_min_med_max'][0]:.4f}/"
          f"{s['texture_min_med_max'][1]:.4f}/{s['texture_min_med_max'][2]:.4f} "
          f"chk|max| {s['checker_absmax']:.4f} head_min {s['head_occ_min']:.3f} "
          f"legs {s['leg_n_max']}/{s['leg_f_max']} "
          f"FAIL chk{len(s['fail_checker'])} head{len(s['fail_head'])} "
          f"tex{len(s['fail_tex'])} legs{len(s['fail_legs'])}")
json.dump(summary, open(os.path.join(OUT, 'qa_summary.json'), 'w'), indent=1)
print('wrote qa_summary.json')
