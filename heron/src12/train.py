"""Heron v1.2 — POSE-SPACE model. An MLP autoencoder over rig pose
parameters (the learned model lives in pose space; the rig renders).
Plus the dynamics summary: PCA over train latents and a per-dimension
AR(2) fit on the grounded behavior sequences, mirroring v1.1's stats.

Held-out clips (never trained): swallow_tiny, turn_reverse, glide,
balance_flick, idle_hunt_c. The honest generalization number is the
roundtrip: encode->decode a held-out pose, render BOTH poses through
the rig, compare grids (cell accuracy / bird-cell accuracy).
"""
import json
import numpy as np
import torch
import torch.nn as nn
import rig
import clips

torch.manual_seed(12)
DEV = 'cuda' if torch.cuda.is_available() else 'cpu'
LATENT = 24
EPOCHS = 160

def load():
    d = np.load('corpus12_poses.npz', allow_pickle=True)
    X = d['X']
    keys = list(d['keys'])
    table = [json.loads(s) for s in d['table']]
    return X, keys, table

class AE(nn.Module):
    def __init__(self, din):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(din, 160), nn.GELU(),
                                 nn.Linear(160, 80), nn.GELU(),
                                 nn.Linear(80, LATENT))
        self.dec = nn.Sequential(nn.Linear(LATENT + 2, 80), nn.GELU(),
                                 nn.Linear(80, 160), nn.GELU(),
                                 nn.Linear(160, din))
    def forward(self, x, code):
        z = self.enc(x)
        return self.dec(torch.cat([z, code], dim=1)), z

def main():
    X, keys, table = load()
    ncont = len(clips.FLAT_KEYS)
    cont = X[:, :ncont]
    code = X[:, ncont:]
    train_idx, val_idx = [], []
    clip_of = np.zeros(len(X), dtype=object)
    for t in table:
        idx = list(range(t['start'], t['start'] + t['n']))
        (val_idx if t['split'] == 'val' else train_idx).extend(idx)
        for i in idx:
            clip_of[i] = t['clip']
    train_idx, val_idx = np.array(train_idx), np.array(val_idx)
    mu, sd = cont[train_idx].mean(0), cont[train_idx].std(0) + 1e-6
    Xn = (cont - mu) / sd
    code_oh = np.zeros((len(X), 2), dtype=np.float32)
    code_oh[:, 0] = (code[:, 0] > 0)          # any fish present
    code_oh[:, 1] = code[:, 1]                # big?
    xt = torch.tensor(Xn[train_idx], device=DEV)
    ct = torch.tensor(code_oh[train_idx], device=DEV)
    xv = torch.tensor(Xn[val_idx], device=DEV)
    cv = torch.tensor(code_oh[val_idx], device=DEV)
    model = AE(ncont).to(DEV)
    nparams = sum(p.numel() for p in model.parameters())
    opt = torch.optim.AdamW(model.parameters(), lr=2e-3, weight_decay=1e-5)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, EPOCHS)
    lossf = nn.MSELoss()
    for ep in range(EPOCHS):
        model.train()
        perm = torch.randperm(len(xt), device=DEV)
        tot = 0.0
        for i in range(0, len(perm), 512):
            j = perm[i:i + 512]
            opt.zero_grad()
            out, _z = model(xt[j], ct[j])
            loss = lossf(out, xt[j])
            loss.backward()
            opt.step()
            tot += float(loss) * len(j)
        sched.step()
        if ep % 20 == 0 or ep == EPOCHS - 1:
            print(f"ep {ep}: train mse {tot / len(xt):.5f}")
    model.eval()
    with torch.no_grad():
        out_v, z_v = model(xv, cv)
        val_mse = float(lossf(out_v, xv))
        out_t, z_t = model(xt, ct)
        train_mse = float(lossf(out_t, xt))
    recon = out_v.cpu().numpy() * sd + mu
    per_param = {}
    for k_i, k in enumerate(clips.FLAT_KEYS):
        err = recon[:, k_i] - cont[val_idx][:, k_i]
        per_param[k] = float(np.sqrt((err ** 2).mean()))
    # roundtrip render check on a val sample (the pose-space analogue of
    # v1.1's pixel val): render decoded vs direct, compare grids
    rng = np.random.default_rng(0)
    sample = rng.choice(val_idx, size=min(240, len(val_idx)), replace=False)
    cell_ok, bird_ok, bird_tot = 0, 0, 0
    for i in sample:
        orig = {k: float(cont[i][j]) for j, k in enumerate(clips.FLAT_KEYS)}
        dec = {k: float(recon[list(val_idx).index(i)][j])
               for j, k in enumerate(clips.FLAT_KEYS)}
        for d in (orig, dec):
            d['fish'] = ['none', 'held', 'free'][int(code[i][0])]
            d['fish_size'] = ['tiny', 'big'][int(code[i][1])]
        g0, _ = rig.render(clips.unflatten(orig))
        g1, _ = rig.render(clips.unflatten(dec))
        cell_ok += int((g0 == g1).sum())
        bird = g0 != rig.WHITE
        bird_ok += int(((g0 == g1) & bird).sum())
        bird_tot += int(bird.sum())
    # dynamics: PCA on train latents + AR(2) residual on grounded clips
    Z = z_t.cpu().numpy()
    Zc = Z - Z.mean(0)
    _u, s_, _vt = np.linalg.svd(Zc, full_matrices=False)
    var = s_ ** 2 / max(len(Z) - 1, 1)
    pca_var = (var / var.sum()).tolist()
    stats = {'params': int(nparams), 'latent': LATENT,
             'train_mse_norm': train_mse, 'val_mse_norm': val_mse,
             'val_frames': int(len(val_idx)), 'train_frames': int(len(train_idx)),
             'per_param_rmse_val': per_param,
             'roundtrip_cell_acc': cell_ok / (len(sample) * rig.W * rig.H),
             'roundtrip_bird_acc': bird_ok / max(bird_tot, 1),
             'pca_var_frac': pca_var[:8]}
    torch.save({'state': model.state_dict(), 'mu': mu, 'sd': sd,
                'keys': clips.FLAT_KEYS, 'latent': LATENT}, 'model12.pt')
    with open('model12_stats.json', 'w') as fh:
        json.dump(stats, fh, indent=1)
    print(json.dumps({k: v for k, v in stats.items()
                      if k != 'per_param_rmse_val'}, indent=1))
    worst = sorted(per_param.items(), key=lambda kv: -kv[1])[:6]
    print("worst val params:", worst)

if __name__ == '__main__':
    main()
