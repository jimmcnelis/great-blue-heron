"""Guardrailed fine-tune of a trained heron AE: oversample the thin-structure
clips (flight legs, strike plume) that the base model smears into blobs, bump
the ink/leg class weights, train briefly at low LR from the trained weights.
Saves to a NEW prefix; the base model is never overwritten. Val accuracy is
measured before and after so the caller can keep whichever model wins."""
import json, sys, time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as Fn
from train import AE, snap_rgb

DEV = 'cuda'
NPAL = 12
PALETTE = [[255, 255, 255], [0, 0, 0], [30, 48, 74], [105, 130, 155], [66, 93, 122],
           [176, 203, 224], [240, 133, 36], [154, 82, 60], [74, 48, 36],
           [150, 163, 105], [94, 110, 66], [216, 222, 182]]
EXTRA = {'strike': 3, 'takeoff': 5, 'flyin': 5, 'turn': 2}

def main(prefix='/home/jim/heron/corpus11', init='/home/jim/heron/model11',
         out='/home/jim/heron/model11f', epochs=6, lr=6e-4, batch=96):
    torch.set_float32_matmul_precision('high')
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.benchmark = True
    frames = np.load(prefix + '_frames.npy')
    N, H, W = frames.shape
    clips_meta = json.load(open(prefix + '_clips.json'))
    cfg = json.load(open(init + '_config.json'))
    latent, chans = cfg['latent'], tuple(cfg['chans'])
    val_names = {c['name'] for c in clips_meta if c['name'].endswith('_9') or c['name'].endswith('_9_m')
                 or c['name'] in ('strike_big_3', 'strike_big_3_m', 'flyin_R_1', 'flyin_R_1_m')}
    val_idx, tr_idx, pool = [], [], []
    for c in clips_meta:
        rng_ = range(c['start'], c['start'] + c['count'])
        if c['name'] in val_names:
            val_idx.extend(rng_)
        else:
            tr_idx.extend(rng_)
            pool.extend(rng_)
            pool.extend(list(rng_) * EXTRA.get(c['kind'], 0))
    val_idx = np.array(val_idx); tr_idx = np.array(tr_idx); pool = np.array(pool)
    print(f'pool {len(pool)} (train {len(tr_idx)})  val {len(val_idx)}', flush=True)
    hist = np.bincount(frames.ravel(), minlength=NPAL).astype(np.float64)
    wts = np.clip(hist.sum() / (NPAL * np.maximum(hist, 1)), 0.12, 8.0)
    wts[0] = 0.10
    wts[1] = min(10.0, wts[1] * 1.5)   # ink: plume, brow, eye lines
    wts[8] = min(10.0, wts[8] * 1.5)   # leg brown: flight stilt lines
    print('class weights:', np.round(wts, 2), flush=True)
    model = AE(H, W, latent=latent, chans=chans).to(DEV).to(memory_format=torch.channels_last)
    model.load_state_dict(torch.load(init + '.pt'))
    palette = torch.tensor(PALETTE, dtype=torch.float32, device=DEV)
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
    before = evaluate(val_idx)
    print('BEFORE val:', json.dumps(before), flush=True)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    steps_per_ep = int(np.ceil(len(pool) / batch))
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=steps_per_ep * epochs)
    lossf = nn.CrossEntropyLoss(weight=torch.tensor(wts, dtype=torch.float32, device=DEV))
    rng = np.random.default_rng(7)
    t0 = time.time()
    for ep in range(epochs):
        model.train()
        perm = rng.permutation(pool)
        tot = 0.0
        for i in range(0, len(perm), batch):
            oh, x = batch_tensors(perm[i:i + batch])
            with torch.autocast('cuda', dtype=torch.bfloat16):
                loss = lossf(model(oh), x.long())
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            opt.step(); sched.step()
            tot += loss.item()
        print(f'ft ep {ep + 1} loss {tot / steps_per_ep:.4f}  {time.time() - t0:.0f}s', flush=True)
    after = evaluate(val_idx)
    print('AFTER val:', json.dumps(after), flush=True)
    snap_mode = 'argmax' if after['argmax']['bird_acc'] >= after['rgb']['bird_acc'] else 'rgb'
    torch.save(model.state_dict(), out + '.pt')
    with open(out + '_config.json', 'w') as f:
        json.dump(dict(H=H, W=W, latent=latent, chans=list(chans), snap_mode=snap_mode), f, indent=1)
    # ---- re-encode latents + refit dynamics (same recipe as train.py)
    lat = np.empty((N, latent), dtype=np.float32)
    model.eval()
    with torch.no_grad():
        for i in range(0, N, 512):
            oh, _x = batch_tensors(np.arange(i, min(i + 512, N)))
            lat[i:i + 512] = model.encode(oh).cpu().numpy()
    np.save(out + '_latents.npy', lat)
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
        k = 25
        ker = np.ones(k) / k
        sm = np.stack([np.convolve(seg[:, d], ker, mode='same') for d in range(NPC)], axis=1)
        res.append((seg - sm)[k:-k])
    R = np.concatenate(res)
    a1 = np.zeros(NPC); a2 = np.zeros(NPC); innov = np.zeros(NPC)
    for d in range(NPC):
        y = R[2:, d]; A = np.stack([R[1:-1, d], R[:-2, d]], axis=1)
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        a1[d], a2[d] = coef
        innov[d] = float(np.std(y - A @ coef))
    np.savez(out + '_dynamics.npz', mean=mean, comps=comps, a1=a1, a2=a2, innov=innov,
             var_exp=var_exp)
    with open(out + '_stats.json', 'w') as f:
        json.dump(dict(before=before, after=after, snap_mode=snap_mode,
                       pca_var_exp=var_exp), f, indent=1)
    print('saved fine-tuned model to', out, 'snap_mode =', snap_mode, flush=True)

if __name__ == '__main__':
    args = sys.argv[1:]
    kw = {}
    if len(args) > 0: kw['prefix'] = args[0]
    if len(args) > 1: kw['init'] = args[1]
    if len(args) > 2: kw['out'] = args[2]
    if len(args) > 3: kw['epochs'] = int(args[3])
    main(**kw)
