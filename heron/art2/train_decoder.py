"""Shared pose-conditioned decoder for art2 routes 1 & 2 (identical
architecture/training for both; only the dataset differs).

Sample format (dataset dir of .npz):
  mask (7,512,512) uint8, rgb (512,512,3) uint8 bird-on-white,
  alpha (512,512) uint8, pose (12,) float32 (ordering per prep_poses.py).

Train:  python3 train_decoder.py train --data DIR --out DIR --steps 4000
Infer:  python3 train_decoder.py infer --ckpt CKPT --art2 ~/workspace/heron/art2
        --outdir DIR   (renders the 4 target poses at master 1024x600)
"""
import argparse, json, math, os, sys
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

DEV = ('cuda' if torch.cuda.is_available() else
       'mps' if torch.backends.mps.is_available() else 'cpu')
AMP = (DEV == 'cuda')


class Block(nn.Module):
    def __init__(self, cin, cout):
        super().__init__()
        self.c1 = nn.Conv2d(cin, cout, 3, padding=1)
        self.c2 = nn.Conv2d(cout, cout, 3, padding=1)
        self.n1 = nn.GroupNorm(8, cout)
        self.n2 = nn.GroupNorm(8, cout)
        self.skip = nn.Conv2d(cin, cout, 1) if cin != cout else nn.Identity()

    def forward(self, x):
        h = F.silu(self.n1(self.c1(x)))
        h = F.silu(self.n2(self.c2(h)))
        return h + self.skip(x)


class UNet(nn.Module):
    def __init__(self, in_ch=19, out_ch=4, widths=(48, 96, 192, 384, 384)):
        super().__init__()
        self.downs = nn.ModuleList()
        ch = in_ch
        for w in widths:
            self.downs.append(Block(ch, w))
            ch = w
        self.pools = nn.ModuleList([nn.Conv2d(w, w, 3, stride=2, padding=1)
                                    for w in widths[:-1]])
        self.ups = nn.ModuleList()
        self.upconvs = nn.ModuleList()
        rev = list(reversed(widths))
        for i in range(len(widths) - 1):
            self.upconvs.append(nn.ConvTranspose2d(rev[i], rev[i], 2, stride=2))
            self.ups.append(Block(rev[i] * 2, rev[i + 1]))
        self.head = nn.Conv2d(widths[0], out_ch, 3, padding=1)

    def forward(self, x):
        skips = []
        h = x
        for i, blk in enumerate(self.downs):
            h = blk(h)
            skips.append(h)
            if i < len(self.pools):
                h = self.pools[i](h)
        for i, (up, blk) in enumerate(zip(self.upconvs, self.ups)):
            h = up(h)
            s = skips[-(i + 2)]
            if h.shape[-2:] != s.shape[-2:]:
                h = F.interpolate(h, size=s.shape[-2:], mode='bilinear',
                                  align_corners=False)
            h = blk(torch.cat([h, s], dim=1))
        return self.head(h)


class DS(torch.utils.data.Dataset):
    def __init__(self, d):
        self.files = sorted(f for f in os.listdir(d) if f.endswith('.npz'))
        self.d = d

    def __len__(self):
        return len(self.files)

    def __getitem__(self, i):
        z = np.load(os.path.join(self.d, self.files[i]))
        mask = torch.from_numpy(z['mask'].astype(np.float32) / 255.0)
        rgb = torch.from_numpy(z['rgb'].astype(np.float32) / 255.0).permute(2, 0, 1)
        alpha = torch.from_numpy(z['alpha'].astype(np.float32) / 255.0)[None]
        pose = torch.from_numpy(z['pose'].astype(np.float32))
        x = torch.cat([mask, pose[:, None, None].expand(12, 512, 512)], 0)
        y = torch.cat([rgb, alpha], 0)
        return x, y


def sobel(x):
    kx = torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
                      dtype=x.dtype, device=x.device).view(1, 1, 3, 3)
    ky = kx.transpose(2, 3)
    gx = F.conv2d(x.reshape(-1, 1, *x.shape[-2:]), kx, padding=1)
    gy = F.conv2d(x.reshape(-1, 1, *x.shape[-2:]), ky, padding=1)
    return (gx.abs() + gy.abs()).view(*x.shape)


def loss_fn(pred, y):
    rgb_p, a_p = pred[:, :3], torch.sigmoid(pred[:, 3:4])
    rgb_y, a_y = y[:, :3], y[:, 3:4]
    w = a_y * 0.9 + 0.1
    l_rgb = (w * (rgb_p - rgb_y).abs()).mean()
    l_a = (a_p - a_y).abs().mean()
    l_g = (w * (sobel(rgb_p) - sobel(rgb_y)).abs()).mean()
    return l_rgb + l_a + 0.3 * l_g, (l_rgb.item(), l_a.item())


def train(args):
    ds = DS(args.data)
    z0 = np.load(os.path.join(args.data, ds.files[0]))
    in_ch = z0['mask'].shape[0] + 12
    print('input channels', in_ch, 'samples', len(ds))
    n = len(ds)
    rng = np.random.RandomState(args.seed)
    idx = rng.permutation(n)
    nval = max(1, int(n * 0.12))
    val_set = torch.utils.data.Subset(ds, idx[:nval])
    tr_set = torch.utils.data.Subset(ds, idx[nval:])
    tr = torch.utils.data.DataLoader(tr_set, batch_size=args.bs, shuffle=True,
                                     num_workers=2, drop_last=True)
    va = torch.utils.data.DataLoader(val_set, batch_size=args.bs)
    model = UNet(in_ch=in_ch).to(DEV)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.OneCycleLR(
        opt, args.lr, total_steps=args.steps, pct_start=0.08)
    os.makedirs(args.out, exist_ok=True)
    step, best = 0, 1e9
    done = False
    while not done:
        for x, y in tr:
            x, y = x.to(DEV), y.to(DEV)
            with torch.autocast('cuda', dtype=torch.bfloat16, enabled=AMP):
                pred = model(x)
                loss, _ = loss_fn(pred.float(), y)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step(); sched.step()
            step += 1
            if step % 200 == 0:
                model.eval()
                with torch.no_grad():
                    vl = np.mean([loss_fn(model(xx.to(DEV)).float(),
                                          yy.to(DEV))[0].item()
                                  for xx, yy in va])
                print(f'step {step} train {loss.item():.4f} val {vl:.4f}',
                      flush=True)
                if vl < best:
                    best = vl
                    torch.save(model.state_dict(),
                               os.path.join(args.out, 'best.pt'))
                model.train()
            if step >= args.steps:
                done = True
                break
    torch.save(model.state_dict(), os.path.join(args.out, 'last.pt'))
    print('DONE best val', best)


@torch.no_grad()
def infer(args):
    from PIL import Image
    sys.path.insert(0, args.art2)
    import maskrender as M
    pj = json.load(open(os.path.join(args.art2, 'poses_art2.json')))
    zpre = np.load(os.path.join(args.art2, 'targets', 'mask_rest.npz'))
    model = UNet(in_ch=zpre['mask'].shape[0] + 12).to(DEV)
    model.load_state_dict(torch.load(args.ckpt, map_location=DEV))
    model.eval()
    pj = json.load(open(os.path.join(args.art2, 'poses_art2.json')))
    os.makedirs(args.outdir, exist_ok=True)
    for name, pd in pj['poses'].items():
        z = np.load(os.path.join(args.art2, 'targets', f'mask_{name}.npz'))
        full = z['mask'].astype(np.float32) / 255.0
        pose = z['pose']
        x0, y0, side = pd['crop_master']
        S = 512
        # crop the full-frame mask stack (pad outside with 0)
        nch = full.shape[0]
        crop = np.zeros((nch, S, S), np.float32)
        fx0, fy0 = int(round(x0)), int(round(y0))
        fs = int(round(side))
        sx0, sy0 = max(0, fx0), max(0, fy0)
        sx1, sy1 = min(1024, fx0 + fs), min(600, fy0 + fs)
        if sx1 > sx0 and sy1 > sy0:
            sub = full[:, sy0:sy1, sx0:sx1]
            sub_t = torch.from_numpy(sub)[None].to(DEV)
            sub_r = F.interpolate(sub_t, size=(S, S), mode='bilinear',
                                  align_corners=False)[0].cpu().numpy()
            dx = int(round((sx0 - fx0) / fs * S)); dy = int(round((sy0 - fy0) / fs * S))
            cw = int(round((sx1 - sx0) / fs * S)); ch = int(round((sy1 - sy0) / fs * S))
            crop[:, dy:dy + ch, dx:dx + cw] = sub_r[:, :ch, :cw]
        x = torch.from_numpy(crop)[None]
        pv = torch.from_numpy(pose)[None, :, None, None].expand(1, 12, S, S)
        x = torch.cat([x, pv], 1).to(DEV)
        with torch.autocast('cuda', dtype=torch.bfloat16, enabled=AMP):
            out = model(x).float()[0]
        rgb = out[:3].clamp(0, 1).cpu().numpy().transpose(1, 2, 0)
        alpha = torch.sigmoid(out[3]).cpu().numpy()
        crop_img = Image.fromarray((rgb * 255).astype(np.uint8))
        crop_img.save(os.path.join(args.outdir, f'raw_{name}.png'))
        # composite onto white master
        big = crop_img.resize((fs, fs), Image.LANCZOS)
        biga = Image.fromarray((alpha * 255).astype(np.uint8)).resize((fs, fs),
                                                                      Image.LANCZOS)
        master = Image.new('RGB', (1024, 600), 'white')
        amaster = Image.new('L', (1024, 600), 0)
        master.paste(big, (fx0, fy0))
        amaster.paste(biga, (fx0, fy0))
        white = Image.new('RGB', (1024, 600), 'white')
        final = Image.composite(master, white, amaster)
        final.save(os.path.join(args.outdir, f'master_{name}.png'))
        print('rendered', name)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    t = sub.add_parser('train')
    t.add_argument('--data', required=True); t.add_argument('--out', required=True)
    t.add_argument('--steps', type=int, default=4000)
    t.add_argument('--bs', type=int, default=6)
    t.add_argument('--lr', type=float, default=2e-4)
    t.add_argument('--seed', type=int, default=7)
    i = sub.add_parser('infer')
    i.add_argument('--ckpt', required=True); i.add_argument('--art2', required=True)
    i.add_argument('--outdir', required=True)
    a = ap.parse_args()
    train(a) if a.cmd == 'train' else infer(a)
