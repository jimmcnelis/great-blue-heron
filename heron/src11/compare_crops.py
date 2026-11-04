"""Decode the two known problem frames (strike-peak head, flyin legs) with two
models and save side-by-side crops: rig truth | model A | model B."""
import json, sys
import numpy as np, torch
import rig
from PIL import Image
from train import AE

def load_model(pfx):
    cfg = json.load(open(pfx + '_config.json'))
    m = AE(cfg['H'], cfg['W'], latent=cfg['latent'], chans=tuple(cfg['chans']))
    m.load_state_dict(torch.load(pfx + '.pt', map_location='cpu'))
    return m.eval().cuda(), cfg

def decode(m, g):
    import torch.nn.functional as Fn
    x = torch.from_numpy(g.astype(np.int64))[None]
    oh = Fn.one_hot(x, 12).permute(0, 3, 1, 2).float().cuda()
    with torch.no_grad():
        lg = m(oh)
    return lg.argmax(1)[0].cpu().numpy().astype(np.uint8)

def crop_png(g, box, path, scale=5):
    x0, y0, x1, y1 = box
    im = Image.fromarray(rig.PALETTE[g[y0:y1, x0:x1]])
    im.resize(((x1 - x0) * scale, (y1 - y0) * scale), Image.NEAREST).save(path)

def main(pfx_a, pfx_b, corpus='/home/jim/heron/corpus11'):
    F = np.load(corpus + '_frames.npy', mmap_mode='r')
    clips = {c['name']: c for c in json.load(open(corpus + '_clips.json'))}
    ma, _ = load_model(pfx_a); mb, _ = load_model(pfx_b)
    jobs = []
    c = clips['strike_tiny_0']
    sp = next(e for e in c['events'] if e['type'] == 'splash')
    jobs.append(('strike', c['start'] + sp['f'] + 3, (200, 90, 320, 200)))
    c = clips['flyin_L_0']
    jobs.append(('flyin', c['start'] + int(c['count'] * 0.55), (0, 40, 190, 170)))
    for name, idx, box in jobs:
        g = np.asarray(F[idx])
        ga, gb = decode(ma, g), decode(mb, g)
        for tag, gg in (('truth', g), ('A', ga), ('B', gb)):
            crop_png(gg, box, f'/tmp/cmp_{name}_{tag}.png')
        print(name, 'frame', idx, 'done')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
