import csv, hashlib, json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.expanduser('~/workspace/heron/art2/motion-test-v3/work'))
from measure_v3 import load, content_mask, color_fracs, iou

FM3 = os.path.expanduser('~/workspace/heron/art2/finished-art-stills/finish-model-v3')
rows = list(csv.DictReader(open(f'{FM3}/corpus_manifest.csv')))
idle = [r for r in rows if r['family'] == 'idle']
t30 = load(f'{FM3}/corpus/target/idle_f0030.png'); m30 = content_mask(t30)
print('== idle donors vs idle_f0030 (the gate target, EXCLUDED from donors) ==')
for r in idle:
    p = f"{FM3}/corpus/target/{r['pair_id']}.png"
    h = hashlib.md5(open(p,'rb').read()).hexdigest()[:8]
    a = load(p); m = content_mask(a)
    f = color_fracs(a, m)
    mad = float(np.abs(a - t30)[m | m30].mean())
    print(f"{r['pair_id']} md5={h} black={f['black']:.4f} slate={f['slate']:.4f} yellow={f['yellow']:.4f} IoU={iou(m,m30):.4f} MAD={mad:.2f}")
print('f0030 black:', color_fracs(t30, m30))
print('== strike neighbours of f27 ==')
g27 = load(f'{FM3}/corpus/target/strike_f0027.png'); gm27 = content_mask(g27)
for i in (23,24,25,26,27,28,29,30,31,34):
    a = load(f'{FM3}/corpus/target/strike_f{i:04d}.png'); m = content_mask(a)
    f = color_fracs(a, m)
    print(f"strike_f{i:04d} black={f['black']:.4f} IoU_vs_f27={iou(m,gm27):.4f} MAD_vs_f27={float(np.abs(a-g27)[m|gm27].mean()):.2f}")
