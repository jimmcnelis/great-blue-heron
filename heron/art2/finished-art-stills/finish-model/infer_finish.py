#!/usr/bin/env python3
"""Deterministic inference for the finish model + motion-test-v2 render.

- Determinism proof: the hold canvas is run 8 times; every output is
  hashed and pairwise-compared. The architecture has no sampling, so
  the outputs must agree to the pixel (report any deviation honestly).
- Renders: the approved-rest-pose hold (1 output, tiled x48 in the
  sequence by design - a hold IS one frame) and all 52 strike canvases.
- Both weight sets (raw + EMA) are rendered for the strike cycle so
  checkpoint selection can be measured on the probe frames, not assumed.
"""
import hashlib, json, os, sys
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from train_finish import UNet, W, H, HP

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, 'corpus')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'render_v2')
CKPT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'train_outB', 'ckpt_final.pt')
os.makedirs(os.path.join(OUT, 'hold'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'strike_ema'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'strike_model'), exist_ok=True)

torch.backends.cudnn.benchmark = False
torch.backends.cudnn.deterministic = True
DEV = 'cuda'

def load_canvas(rel):
    a = np.asarray(Image.open(os.path.join(CORPUS, rel)).convert('RGB'), dtype=np.float32) / 127.5 - 1.0
    t = torch.from_numpy(a).permute(2, 0, 1).unsqueeze(0).to(DEV)
    return F.pad(t, (0, 0, 0, HP - H), mode='reflect')

def to_png(t):
    a = (t[0, :, :H].permute(1, 2, 0).clamp(-1, 1) * 127.5 + 127.5).round().to(torch.uint8).cpu().numpy()
    return Image.fromarray(a), a

ck = torch.load(CKPT, map_location=DEV)
nets = {}
for name in ('ema', 'model'):
    net = UNet().to(DEV); net.load_state_dict(ck[name]); net.eval(); nets[name] = net

def run(net, x):
    with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
        return net(x).float()

# ---- determinism proof on the hold canvas (EMA net) ----
hold_x = load_canvas('canvas/idle_hold.png')
outs = []
for i in range(8):
    im, arr = to_png(run(nets['ema'], hold_x))
    outs.append(arr)
    if i == 0: im.save(os.path.join(OUT, 'hold', 'hold_frame.png'))
hashes = [hashlib.md5(a.tobytes()).hexdigest() for a in outs]
maxdiff = 0.0
for i in range(len(outs)):
    for j in range(i + 1, len(outs)):
        d = float(np.abs(outs[i].astype(np.float32) - outs[j].astype(np.float32)).max())
        maxdiff = max(maxdiff, d)
det = dict(runs=8, unique_hashes=len(set(hashes)), max_pairwise_pixel_diff=maxdiff, hashes=hashes)
print('determinism:', det, flush=True)

# ---- strike cycle, both weight sets ----
for name, sub in (('ema', 'strike_ema'), ('model', 'strike_model')):
    for i in range(52):
        im, _ = to_png(run(nets[name], load_canvas(f'canvas/strike_f{i:04d}.png')))
        im.save(os.path.join(OUT, sub, f'f{i:04d}.png'))
    print('rendered', sub, flush=True)

json.dump(det, open(os.path.join(OUT, 'determinism.json'), 'w'), indent=1)
print('DONE')
