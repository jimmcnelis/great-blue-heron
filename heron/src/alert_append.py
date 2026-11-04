"""Append alert (presence-response) clips to an existing corpus + encode their latents."""
import json
import numpy as np
import torch
import torch.nn.functional as Fn
import rig, clips
from train import AE

def main(corpus='/home/jim/heron/corpus', model_pfx='/home/jim/heron/model'):
    frames = np.load(corpus + '_frames.npy')
    beaks = np.load(corpus + '_beaks.npy')
    metas = json.load(open(corpus + '_clips.json'))
    lat = np.load(model_pfx + '_latents.npy')
    model = AE().cuda()
    model.load_state_dict(torch.load(model_pfx + '.pt'))
    model.eval()

    new_frames, new_beaks, new_metas = [], [], []
    start = len(frames)
    for name, zone, seed, mirror in [('alert_L_0', 'L', 2000, False), ('alert_L_1', 'L', 2001, False),
                                     ('alert_L_0', 'L', 2000, True), ('alert_L_1', 'L', 2001, True)]:
        poses, events = clips.alert_clip(zone=zone, seed=seed)
        F = np.empty((len(poses), rig.H, rig.W), dtype=np.uint8)
        B = np.zeros((len(poses), 2), dtype=np.float32)
        for i, p in enumerate(poses):
            g, info = rig.render(p)
            F[i] = g; B[i] = info['beak_tip']
        zf = zone
        nm = name
        if mirror:
            F = np.ascontiguousarray(F[:, :, ::-1])
            B = B.copy(); B[:, 0] = (rig.W - 1) - B[:, 0]
            zf = {'L': 'R', 'R': 'L'}[zone]
            nm = name + '_m'
        new_metas.append(dict(name=nm, kind='alert', facing=-1 if mirror else 1,
                              zone_from=zf, zone_to=zf, count=len(F), events=[], start=start))
        start += len(F)
        new_frames.append(F); new_beaks.append(B)
        print('alert clip', nm, len(F), 'zone', zf)
    NF = np.concatenate(new_frames); NB = np.concatenate(new_beaks)
    with torch.no_grad():
        oh = Fn.one_hot(torch.from_numpy(NF).cuda().long(), 12).permute(0, 3, 1, 2).float()
        NL = model.encode(oh).cpu().numpy()
    np.save(corpus + '_frames.npy', np.concatenate([frames, NF]))
    np.save(corpus + '_beaks.npy', np.concatenate([beaks, NB]))
    np.save(model_pfx + '_latents.npy', np.concatenate([lat, NL]))
    json.dump(metas + new_metas, open(corpus + '_clips.json', 'w'))
    print('corpus now', start, 'frames')

if __name__ == '__main__':
    import sys
    main(*sys.argv[1:])
