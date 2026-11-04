"""Train the tiny palette autoencoder on the corpus; fit latent dynamics (PCA + AR(2) noise)."""
import json, sys, time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as Fn

DEV = 'cuda'
NPAL, LAT = 12, 48
H, W = 120, 160

class AE(nn.Module):
    def __init__(self):
        super().__init__()
        self.enc = nn.Sequential(
            nn.Conv2d(NPAL, 32, 3, 2, 1), nn.GELU(),          # 60x80
            nn.Conv2d(32, 48, 3, 2, 1), nn.GELU(),            # 30x40
            nn.Conv2d(48, 64, 3, 2, 1), nn.GELU(),            # 15x20
        )
        self.to_lat = nn.Linear(64 * 15 * 20, LAT)
        self.from_lat = nn.Linear(LAT, 64 * 15 * 20)
        self.dec = nn.Sequential(
            nn.Conv2d(64, 48, 3, 1, 1), nn.GELU(),
            nn.Conv2d(48, 32, 3, 1, 1), nn.GELU(),
        )
        self.head = nn.Conv2d(32, NPAL, 1)
    def encode(self, x):
        h = self.enc(x).flatten(1)
        return self.to_lat(h)
    def decode(self, z):
        h = self.from_lat(z).view(-1, 64, 15, 20)
        h = Fn.interpolate(h, size=(30, 40), mode='nearest'); h = self.dec[0](h); h = self.dec[1](h)
        h = Fn.interpolate(h, size=(60, 80), mode='nearest'); h = self.dec[2](h); h = self.dec[3](h)
        h = Fn.interpolate(h, size=(120, 160), mode='nearest')
        return self.head(h)
    def forward(self, x):
        return self.decode(self.encode(x))

def count_params(m):
    return sum(p.numel() for p in m.parameters())

def main(prefix='/home/jim/heron/corpus', out='/home/jim/heron/model', epochs=26):
    frames = np.load(prefix + '_frames.npy')
    with open(prefix + '_clips.json') as f:
        clips = json.load(f)
    N = len(frames)
    rng = np.random.default_rng(0)
    val_names = {c['name'] for c in clips if c['name'].endswith('_9') or c['name'].endswith('_9_m')
                 or c['name'] in ('strike_big_3', 'strike_big_3_m', 'flyin_R_1', 'flyin_R_1_m')}
    val_idx, tr_idx = [], []
    for c in clips:
        (val_idx if c['name'] in val_names else tr_idx).extend(range(c['start'], c['start'] + c['count']))
    val_idx = np.array(val_idx); tr_idx = np.array(tr_idx)
    print(f'train frames {len(tr_idx)}  val frames {len(val_idx)}')
    hist = np.bincount(frames.ravel(), minlength=NPAL).astype(np.float64)
    wts = np.clip(hist.sum() / (NPAL * np.maximum(hist, 1)), 0.12, 6.0)
    wts[0] = 0.15
    print('class weights:', np.round(wts, 2))
    model = AE().to(DEV)
    print('params:', count_params(model))
    opt = torch.optim.AdamW(model.parameters(), lr=2e-3, weight_decay=1e-4)
    steps_per_ep = int(np.ceil(len(tr_idx) / 128))
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, 2e-3, total_steps=steps_per_ep * epochs)
    lossf = nn.CrossEntropyLoss(weight=torch.tensor(wts, dtype=torch.float32, device=DEV))
    X = torch.from_numpy(frames)
    def batch(idx):
        x = X[idx].to(DEV)
        oh = Fn.one_hot(x.long(), NPAL).permute(0, 3, 1, 2).float()
        return oh, x
    t0 = time.time()
    for ep in range(epochs):
        model.train()
        perm = rng.permutation(tr_idx)
        tot = 0.0
        for i in range(0, len(perm), 128):
            oh, x = batch(perm[i:i + 128])
            logits = model(oh)
            loss = lossf(logits, x.long())
            opt.zero_grad(); loss.backward(); opt.step(); sched.step()
            tot += loss.item()
        if ep % 5 == 4 or ep == epochs - 1:
            print(f'ep {ep + 1} loss {tot / steps_per_ep:.4f}  {time.time() - t0:.0f}s', flush=True)
    # ---- evaluation: exact-cell accuracy
    model.eval()
    def evaluate(idx):
        tot = bird_tot = fish_tot = 0
        cor = bird_cor = fish_cor = 0
        with torch.no_grad():
            for i in range(0, len(idx), 256):
                oh, x = batch(idx[i:i + 256])
                pred = model(oh).argmax(1)
                eq = (pred == x)
                tot += x.numel(); cor += int(eq.sum())
                bm = x != 0
                bird_tot += int(bm.sum()); bird_cor += int(eq[bm].sum())
                fm = x >= 9
                fish_tot += int(fm.sum()); fish_cor += int(eq[fm].sum())
        return dict(cell_acc=cor / tot, bird_acc=bird_cor / max(bird_tot, 1),
                    fish_acc=fish_cor / max(fish_tot, 1), n=len(idx))
    stats = dict(params=count_params(model), latent=LAT,
                 train=evaluate(tr_idx[:4000]), val=evaluate(val_idx))
    print(stats)
    # ---- encode all frames
    lat = np.empty((N, LAT), dtype=np.float32)
    with torch.no_grad():
        for i in range(0, N, 512):
            x = X[i:i + 512].to(DEV)
            oh = Fn.one_hot(x.long(), NPAL).permute(0, 3, 1, 2).float()
            lat[i:i + 512] = model.encode(oh).cpu().numpy()
    np.save(out + '_latents.npy', lat)
    torch.save(model.state_dict(), out + '.pt')
    # ---- dynamics: PCA + AR(2) on idle residuals
    mean = lat.mean(0)
    U, S, Vt = np.linalg.svd(lat - mean, full_matrices=False)
    NPC = 32
    comps = Vt[:NPC]                                   # (NPC, LAT)
    var_exp = float((S[:NPC] ** 2).sum() / (S ** 2).sum())
    pc = (lat - mean) @ comps.T                        # (N, NPC)
    res = []
    for c in clips:
        if c['kind'] != 'idle':
            continue
        seg = pc[c['start']:c['start'] + c['count']]
        k = 13
        ker = np.ones(k) / k
        sm = np.stack([np.convolve(seg[:, d], ker, mode='same') for d in range(NPC)], axis=1)
        r = seg - sm
        res.append(r[k:-k])
    R = np.concatenate(res)
    a1 = np.zeros(NPC); a2 = np.zeros(NPC); innov = np.zeros(NPC)
    for d in range(NPC):
        y = R[2:, d]; A = np.stack([R[1:-1, d], R[:-2, d]], axis=1)
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        a1[d], a2[d] = coef
        innov[d] = float(np.std(y - A @ coef))
    np.savez(out + '_dynamics.npz', mean=mean, comps=comps, a1=a1, a2=a2, innov=innov,
             var_exp=var_exp)
    stats['pca_var_exp_32'] = var_exp
    with open(out + '_stats.json', 'w') as f:
        json.dump(stats, f, indent=1)
    print('saved model + latents + dynamics')

if __name__ == '__main__':
    main(*sys.argv[1:])
