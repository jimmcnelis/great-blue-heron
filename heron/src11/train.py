"""Train the v1.1 palette autoencoder (bigger, latent 128) on the corpus;
fit latent dynamics (PCA + AR(2) noise). Writes a model config sidecar so the
sim builds the identical architecture, and reports validation accuracy under
BOTH decode snaps (categorical argmax and RGB nearest-palette snap)."""
import json, os, sys, time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as Fn

DEV = 'cuda'
NPAL = 12

class AE(nn.Module):
    """Parametric conv autoencoder. n_down stride-2 stages; chans per stage.
    Bottleneck spatial = (H >> n_down, W >> n_down)."""
    def __init__(self, H, W, latent=128, chans=(48, 96, 160, 224)):
        super().__init__()
        self.H, self.W, self.latent = H, W, latent
        self.chans = list(chans)
        self.n_down = len(chans)
        self.bh, self.bw = H >> self.n_down, W >> self.n_down
        assert H == self.bh << self.n_down and W == self.bw << self.n_down
        layers, cin = [], NPAL
        for c in chans:
            layers += [nn.Conv2d(cin, c, 3, 2, 1), nn.GELU()]
            cin = c
        self.enc = nn.Sequential(*layers)
        self.to_lat = nn.Linear(chans[-1] * self.bh * self.bw, latent)
        self.from_lat = nn.Linear(latent, chans[-1] * self.bh * self.bw)
        self.dec0 = nn.Sequential(nn.Conv2d(chans[-1], chans[-1], 3, 1, 1), nn.GELU())
        blocks = []
        for i in range(self.n_down - 1, -1, -1):
            cout = chans[i - 1] if i > 0 else chans[0]
            blocks.append(nn.Conv2d(chans[i], cout, 3, 1, 1))
        self.dec_blocks = nn.ModuleList(blocks)
        self.dec_act = nn.GELU()
        self.head = nn.Conv2d(chans[0], NPAL, 1)
    def encode(self, x):
        return self.to_lat(self.enc(x).flatten(1))
    def decode(self, z):
        h = self.from_lat(z).view(-1, self.chans[-1], self.bh, self.bw)
        h = self.dec0(h)
        for blk in self.dec_blocks:
            h = Fn.interpolate(h, scale_factor=2, mode='nearest')
            h = self.dec_act(blk(h))
        return self.head(h)
    def forward(self, x):
        return self.decode(self.encode(x))

def count_params(m):
    return sum(p.numel() for p in m.parameters())

def snap_rgb(logits, palette):
    """Palette-snap in RGB space: softmax -> expected RGB -> nearest palette entry."""
    p = torch.softmax(logits, dim=1)                       # (B,NPAL,H,W)
    rgb = torch.einsum('bkhw,kc->bhwc', p, palette)        # (B,H,W,3)
    d = ((rgb[:, :, :, None, :] - palette[None, None, None, :, :]) ** 2).sum(-1)
    return d.argmin(-1)

def main(prefix='/home/jim/heron/corpus11', out='/home/jim/heron/model11',
         epochs=55, latent=128, chans=(48, 96, 160, 224), batch=96):
    torch.set_float32_matmul_precision('high')
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.benchmark = True
    frames = np.load(prefix + '_frames.npy')
    N, H, W = frames.shape
    with open(prefix + '_clips.json') as f:
        clips_meta = json.load(f)
    rng = np.random.default_rng(0)
    val_names = {c['name'] for c in clips_meta if c['name'].endswith('_9') or c['name'].endswith('_9_m')
                 or c['name'] in ('strike_big_3', 'strike_big_3_m', 'flyin_R_1', 'flyin_R_1_m')}
    val_idx, tr_idx = [], []
    for c in clips_meta:
        (val_idx if c['name'] in val_names else tr_idx).extend(range(c['start'], c['start'] + c['count']))
    val_idx = np.array(val_idx); tr_idx = np.array(tr_idx)
    print(f'grid {H}x{W}  train frames {len(tr_idx)}  val frames {len(val_idx)}', flush=True)
    hist = np.bincount(frames.ravel(), minlength=NPAL).astype(np.float64)
    wts = np.clip(hist.sum() / (NPAL * np.maximum(hist, 1)), 0.12, 8.0)
    wts[0] = 0.10
    print('class weights:', np.round(wts, 2), flush=True)
    model = AE(H, W, latent=latent, chans=chans).to(DEV).to(memory_format=torch.channels_last)
    if os.environ.get('HERON_INIT'):
        model.load_state_dict(torch.load(os.environ['HERON_INIT']))
        print('init from', os.environ['HERON_INIT'], flush=True)
    print('params:', count_params(model), flush=True)
    palette = torch.tensor(
        [[255, 255, 255], [0, 0, 0], [30, 48, 74], [105, 130, 155], [66, 93, 122],
         [176, 203, 224], [240, 133, 36], [154, 82, 60], [74, 48, 36], [150, 163, 105],
         [94, 110, 66], [216, 222, 182]], dtype=torch.float32, device=DEV)
    peak_lr = float(os.environ.get('HERON_LR', 2e-3))
    clip_val = float(os.environ.get('HERON_CLIP', 5.0))
    opt = torch.optim.AdamW(model.parameters(), lr=peak_lr, weight_decay=1e-4)
    steps_per_ep = int(np.ceil(len(tr_idx) / batch))
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, peak_lr, total_steps=steps_per_ep * epochs)
    lossf = nn.CrossEntropyLoss(weight=torch.tensor(wts, dtype=torch.float32, device=DEV))
    X = torch.from_numpy(frames)
    def batch_tensors(idx):
        x = X[idx].to(DEV)
        oh = Fn.one_hot(x.long(), NPAL).permute(0, 3, 1, 2).float()
        return oh.to(memory_format=torch.channels_last), x
    def evaluate(idx, max_n=6000):
        idx = idx[:max_n]
        model.eval()
        res = {}
        for mode in ('argmax', 'rgb'):
            tot = bird_tot = fish_tot = 0
            cor = bird_cor = fish_cor = 0
            with torch.no_grad():
                for i in range(0, len(idx), 128):
                    oh, x = batch_tensors(idx[i:i + 128])
                    logits = model(oh)
                    pred = logits.argmax(1) if mode == 'argmax' else snap_rgb(logits, palette)
                    eq = (pred == x)
                    tot += x.numel(); cor += int(eq.sum())
                    bm = x != 0
                    bird_tot += int(bm.sum()); bird_cor += int(eq[bm].sum())
                    fm = x >= 9
                    fish_tot += int(fm.sum()); fish_cor += int(eq[fm].sum())
            res[mode] = dict(cell_acc=cor / tot, bird_acc=bird_cor / max(bird_tot, 1),
                             fish_acc=fish_cor / max(fish_tot, 1))
        model.train()
        return res
    t0 = time.time()
    for ep in range(epochs):
        model.train()
        perm = rng.permutation(tr_idx)
        tot = 0.0
        for i in range(0, len(perm), batch):
            oh, x = batch_tensors(perm[i:i + batch])
            with torch.autocast('cuda', dtype=torch.bfloat16):
                loss = lossf(model(oh), x.long())
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), clip_val)
            opt.step(); sched.step()
            tot += loss.item()
        if ep % 5 == 4 or ep == epochs - 1:
            msg = f'ep {ep + 1} loss {tot / steps_per_ep:.4f}  {time.time() - t0:.0f}s'
            if ep % 10 == 9 or ep == epochs - 1:
                ev = evaluate(val_idx)
                msg += (f"  val bird argmax {ev['argmax']['bird_acc']:.4f}"
                        f" rgb {ev['rgb']['bird_acc']:.4f}  fish {ev['argmax']['fish_acc']:.4f}")
            print(msg, flush=True)
    ev_tr = evaluate(tr_idx)
    ev_val = evaluate(val_idx)
    snap_mode = 'argmax' if ev_val['argmax']['bird_acc'] >= ev_val['rgb']['bird_acc'] else 'rgb'
    stats = dict(params=count_params(model), latent=latent, chans=list(chans),
                 grid=[H, W], snap_mode=snap_mode,
                 train_argmax=ev_tr['argmax'], val_argmax=ev_val['argmax'],
                 train_rgb=ev_tr['rgb'], val_rgb=ev_val['rgb'])
    print(stats, flush=True)
    # ---- encode all frames
    lat = np.empty((N, latent), dtype=np.float32)
    model.eval()
    with torch.no_grad():
        for i in range(0, N, 512):
            oh, _x = batch_tensors(np.arange(i, min(i + 512, N)))
            lat[i:i + 512] = model.encode(oh).cpu().numpy()
    np.save(out + '_latents.npy', lat)
    torch.save(model.state_dict(), out + '.pt')
    cfg = dict(H=H, W=W, latent=latent, chans=list(chans), snap_mode=snap_mode)
    with open(out + '_config.json', 'w') as f:
        json.dump(cfg, f, indent=1)
    # ---- dynamics: PCA + AR(2) on idle residuals
    mean = lat.mean(0)
    U, S, Vt = np.linalg.svd(lat - mean, full_matrices=False)
    NPC = 48
    comps = Vt[:NPC]
    var_exp = float((S[:NPC] ** 2).sum() / (S ** 2).sum())
    pc = (lat - mean) @ comps.T
    res = []
    for c in clips_meta:
        if c['kind'] != 'idle':
            continue
        seg = pc[c['start']:c['start'] + c['count']]
        k = 25  # ~1 s smoothing at 24 fps
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
    stats['pca_var_exp'] = var_exp
    with open(out + '_stats.json', 'w') as f:
        json.dump(stats, f, indent=1)
    print('saved model + latents + dynamics; snap_mode =', snap_mode, flush=True)

if __name__ == '__main__':
    import ast
    args = sys.argv[1:]
    kw = {}
    if len(args) > 0: kw['prefix'] = args[0]
    if len(args) > 1: kw['out'] = args[1]
    if len(args) > 2: kw['epochs'] = int(args[2])
    if len(args) > 3: kw['chans'] = tuple(ast.literal_eval(args[3]))
    main(**kw)
