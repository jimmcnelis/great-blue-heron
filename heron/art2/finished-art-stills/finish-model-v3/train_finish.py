#!/usr/bin/env python3
"""Pose-conditioned finish model for the heron (the pivot, 2026-11-03).

Deterministic paired translator: Route-2 study canvas -> finished
Audubon frame (1024x600). No sampling anywhere: same canvas in, same
finished frame out, so holds go truly still.

Two stages (the GB10 measures ~2.0 s/step at full res, batch 4):
  A: half resolution (512x304), batch 8, 3600 steps - identity, marks,
     geometry lockstep (identical-warp augmentation) learned here.
  B: full resolution, batch 4, 900 steps from A's weights - texture.
Losses: Charbonnier + Sobel L1 (x0.5) + Laplacian HF L1 (x0.25).
Probe: strike f06/f25/f34/f45 held out, evaluated on EMA weights.
"""
import csv, json, math, os, random, sys, time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, 'corpus')
SEED = 20261103
W, H = 1024, 600
HP = 608
SCALE = 1.0  # set per-stage in main()

torch.manual_seed(SEED); random.seed(SEED); np.random.seed(SEED)
torch.backends.cudnn.benchmark = False
DEV = 'cuda'

class ResBlock(nn.Module):
    def __init__(self, cin, cout):
        super().__init__()
        self.n1 = nn.GroupNorm(8, cin); self.c1 = nn.Conv2d(cin, cout, 3, padding=1)
        self.n2 = nn.GroupNorm(8, cout); self.c2 = nn.Conv2d(cout, cout, 3, padding=1)
        self.skip = nn.Conv2d(cin, cout, 1) if cin != cout else nn.Identity()
    def forward(self, x):
        h = self.c1(F.silu(self.n1(x)))
        h = self.c2(F.silu(self.n2(h)))
        return h + self.skip(x)

class Attn(nn.Module):
    def __init__(self, c):
        super().__init__()
        self.n = nn.GroupNorm(8, c)
        self.qkv = nn.Conv2d(c, c * 3, 1); self.proj = nn.Conv2d(c, c, 1)
    def forward(self, x):
        b, c, h, w = x.shape
        q, k, v = self.qkv(self.n(x)).reshape(b, 3, c, h * w).unbind(1)
        att = torch.softmax(q.transpose(1, 2) @ k / math.sqrt(c), dim=-1)
        o = (v @ att.transpose(1, 2)).reshape(b, c, h, w)
        return x + self.proj(o)

class UNet(nn.Module):
    def __init__(self, base=64):
        super().__init__()
        chs = [base * k for k in (1, 2, 4, 8)]
        self.ins = nn.Conv2d(3, chs[0], 3, padding=1)
        self.downs = nn.ModuleList(); self.pools = nn.ModuleList()
        for i in range(3):
            self.downs.append(nn.ModuleList([ResBlock(chs[i], chs[i]), ResBlock(chs[i], chs[i])]))
            self.pools.append(nn.Conv2d(chs[i], chs[i + 1], 3, stride=2, padding=1))
        self.mid = nn.ModuleList([ResBlock(chs[3], chs[3]), Attn(chs[3]), ResBlock(chs[3], chs[3])])
        self.ups = nn.ModuleList(); self.upconvs = nn.ModuleList()
        for i in reversed(range(3)):
            self.upconvs.append(nn.ConvTranspose2d(chs[i + 1], chs[i], 2, stride=2))
            self.ups.append(nn.ModuleList([ResBlock(chs[i] * 2, chs[i]), ResBlock(chs[i], chs[i])]))
        self.outn = nn.GroupNorm(8, chs[0]); self.out = nn.Conv2d(chs[0], 3, 3, padding=1)
    def forward(self, x):
        skips = []
        h = self.ins(x)
        for i in range(3):
            for b in self.downs[i]: h = b(h)
            skips.append(h); h = self.pools[i](h)
        for b in self.mid: h = b(h)
        for i, j in enumerate(reversed(range(3))):
            h = self.upconvs[i](h)
            h = torch.cat([h, skips[j]], dim=1)
            for b in self.ups[i]: h = b(h)
        return torch.tanh(self.out(F.silu(self.outn(h))))

def load_pairs():
    rows = list(csv.DictReader(open(os.path.join(HERE, 'corpus_manifest.csv'))))
    def rd(rel):
        a = np.asarray(Image.open(os.path.join(CORPUS, rel)).convert('RGB'), dtype=np.float32) / 127.5 - 1.0
        return torch.from_numpy(a).permute(2, 0, 1)
    train, probe = [], []
    for r in rows:
        pair = (rd(r['canvas']), rd(r['target']), r['pair_id'])
        (probe if r['role'] == 'probe' else train).append(pair)
    return train, probe

def warp_pair(x, y, gen):
    b = x.shape[0]
    hh, ww = x.shape[2], x.shape[3]
    ang = (torch.rand(b, generator=gen) - 0.5) * 2 * 0.01
    scl = 1.0 + (torch.rand(b, generator=gen) - 0.5) * 0.04
    tx = (torch.rand(b, generator=gen) - 0.5) * 2 * 10 / W * 2
    ty = (torch.rand(b, generator=gen) - 0.5) * 2 * 8 / HP * 2
    theta = torch.zeros(b, 2, 3)
    theta[:, 0, 0] = torch.cos(ang) / scl; theta[:, 0, 1] = -torch.sin(ang) / scl; theta[:, 0, 2] = tx
    theta[:, 1, 0] = torch.sin(ang) / scl; theta[:, 1, 1] = torch.cos(ang) / scl; theta[:, 1, 2] = ty
    grid = F.affine_grid(theta, x.shape, align_corners=False)
    fld = torch.rand(b, 2, 8, 5, generator=gen) * 2 - 1
    fld = F.interpolate(fld, size=(hh, ww), mode='bilinear', align_corners=False)
    fld = fld.permute(0, 2, 3, 1) * (6.0 / W * 2)
    grid = (grid + fld).clamp(-1.2, 1.2).to(x.device)
    return (F.grid_sample(x, grid, align_corners=False, padding_mode='reflection'),
            F.grid_sample(y, grid, align_corners=False, padding_mode='reflection'))

def pad(t):
    return F.pad(t, (0, 0, 0, HP - H), mode='reflect')

def scale_pair(t):
    if SCALE == 1.0: return t
    return F.interpolate(t, size=(int(HP * SCALE), int(W * SCALE)), mode='bilinear', align_corners=False)

def charbonnier(a, b): return torch.sqrt((a - b) ** 2 + 1e-3).mean()
def sobel_l1(a, b):
    kx = torch.tensor([[-1., 0., 1.], [-2., 0., 2.], [-1., 0., 1.]], device=a.device).view(1, 1, 3, 3) / 8
    ky = kx.transpose(2, 3)
    def g(t):
        t = t.mean(1, keepdim=True)
        return F.conv2d(t, kx, padding=1).abs() + F.conv2d(t, ky, padding=1).abs()
    return (g(a) - g(b)).abs().mean()
def hf_l1(a, b):
    k = torch.tensor([[0., 1., 0.], [1., -4., 1.], [0., 1., 0.]], device=a.device).view(1, 1, 3, 3)
    def lap(t): return F.conv2d(t.mean(1, keepdim=True), k, padding=1)
    return (lap(a) - lap(b)).abs().mean()

def main():
    global SCALE
    STAGE = sys.argv[1] if len(sys.argv) > 1 else 'A'
    OUT = os.path.join(HERE, f'train_out{STAGE}')
    os.makedirs(OUT, exist_ok=True)
    if STAGE == 'A':
        SCALE, STEPS, BATCH, LR, EVAL_EVERY, SAVE_EVERY = 0.5, 3600, 8, 2e-4, 250, 1200
    else:
        SCALE, STEPS, BATCH, LR, EVAL_EVERY, SAVE_EVERY = 1.0, 900, 4, 8e-5, 150, 300
    train, probe = load_pairs()
    print(f'stage {STAGE} scale {SCALE} train {len(train)} probe {len(probe)}', flush=True)
    model = UNet().to(DEV)
    ema = UNet().to(DEV)
    if STAGE == 'B':
        ck = torch.load(os.path.join(HERE, 'train_outA', 'ckpt_final.pt'), map_location=DEV)
        model.load_state_dict(ck['model']); ema.load_state_dict(ck['ema'])
        print('loaded stage A weights', flush=True)
    else:
        ema.load_state_dict(model.state_dict())
    ema.eval()
    print(f'params {sum(p.numel() for p in model.parameters())/1e6:.1f}M', flush=True)
    opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, LR, total_steps=STEPS, pct_start=0.05)
    gen = torch.Generator().manual_seed(SEED)
    probe_x = scale_pair(pad(torch.stack([p[0] for p in probe]))).to(DEV)
    probe_y = scale_pair(pad(torch.stack([p[1] for p in probe]))).to(DEV)
    log = []
    t0 = time.time()
    idx = list(range(len(train)))
    for step in range(1, STEPS + 1):
        if step % len(train) == 1: random.shuffle(idx)
        batch = [train[idx[(step * BATCH + k) % len(train)]] for k in range(BATCH)]
        x = scale_pair(pad(torch.stack([b[0] for b in batch]))).to(DEV)
        y = scale_pair(pad(torch.stack([b[1] for b in batch]))).to(DEV)
        if random.random() < 0.8: x, y = warp_pair(x, y, gen)
        with torch.autocast('cuda', dtype=torch.bfloat16):
            pred = model(x)
            loss = charbonnier(pred, y) + 0.5 * sobel_l1(pred.float(), y) + 0.25 * hf_l1(pred.float(), y)
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step(); sched.step()
        with torch.no_grad():
            for pe, pm in zip(ema.parameters(), model.parameters()): pe.mul_(0.999).add_(pm, alpha=0.001)
        if step % EVAL_EVERY == 0 or step == 1:
            with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
                pl = charbonnier(ema(probe_x), probe_y).item()
            rec = dict(step=step, loss=round(loss.item(), 4), probe_charb_ema=round(pl, 4),
                       elapsed_s=round(time.time() - t0))
            log.append(rec); print(rec, flush=True)
        if step % SAVE_EVERY == 0 or step == STEPS:
            torch.save(dict(model=model.state_dict(), ema=ema.state_dict(), step=step),
                       os.path.join(OUT, f'ckpt_{step}.pt'))
    torch.save(dict(model=model.state_dict(), ema=ema.state_dict(), step=STEPS),
               os.path.join(OUT, 'ckpt_final.pt'))
    json.dump(log, open(os.path.join(OUT, 'train_log.json'), 'w'), indent=1)
    print('DONE', flush=True)

if __name__ == '__main__':
    main()
