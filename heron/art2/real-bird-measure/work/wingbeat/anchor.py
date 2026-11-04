#!/usr/bin/env python3
"""Anchor-interpolated crop extraction: signals + dense eye strips.
cfg: path,t0,t1,fps,width, anchors=[[t,nx,ny],...] (normalized), crop (px),
     out prefix, tile, cols"""
import subprocess, sys, json
import numpy as np
from scipy import signal
from PIL import Image

cfg = json.loads(sys.argv[1])
path, t0, t1, fps, width = cfg["path"], cfg["t0"], cfg["t1"], cfg["fps"], cfg["width"]
raw = subprocess.run(["ffmpeg","-v","error","-ss",str(t0),"-i",path,"-t",str(t1-t0),
                      "-vf",f"fps={fps},scale={width}:-1,format=gray","-f","rawvideo","-"],
                     capture_output=True, check=True).stdout
one = subprocess.run(["ffmpeg","-v","error","-ss",str(t0),"-i",path,"-frames:v","1",
                      "-vf",f"scale={width}:-1,format=gray","-f","rawvideo","-"],
                     capture_output=True, check=True).stdout
H = len(one)//width; W = width
n = len(raw)//(W*H)
frames = np.frombuffer(raw[:n*W*H], dtype=np.uint8).reshape(n,H,W).astype(np.float32)
times = t0 + np.arange(n)/fps
anch = np.array(cfg["anchors"])
ax = np.interp(times, anch[:,0], anch[:,1]*W)
ay = np.interp(times, anch[:,0], anch[:,2]*H)
crop = cfg["crop"]; half = crop//2
dark = np.zeros(n); bh = np.zeros(n); bw = np.zeros(n); area = np.zeros(n)
crops = []
for i in range(n):
    cx = int(min(max(ax[i], half), W-half)); cy = int(min(max(ay[i], half), H-half))
    c = frames[i][cy-half:cy+half, cx-half:cx+half]
    crops.append(c.astype(np.uint8))
    thr = c.min() + 0.45*(np.percentile(c,90)-c.min())
    m = c < thr
    area[i] = m.sum(); dark[i] = m.mean()
    ys, xs = np.nonzero(m)
    if len(ys) > 5:
        # keep only the largest cluster near crop centre: use pixels within 0.75*crop of centre
        d2 = (ys-half)**2 + (xs-half)**2
        keep = d2 < (0.75*half)**2
        if keep.sum() > 5:
            ys, xs = ys[keep], xs[keep]
        bh[i] = ys.max()-ys.min(); bw[i] = xs.max()-xs.min()
    else:
        bh[i] = np.nan; bw[i] = np.nan

def estimate(s, band=(1.2,4.0)):
    s = s.copy(); ok = ~np.isnan(s)
    if ok.sum() < 20: return None
    s[~ok] = np.interp(np.nonzero(~ok)[0], np.nonzero(ok)[0], s[ok])
    k = int(fps*0.9)//2*2+1
    s = s - signal.medfilt(s, kernel_size=k); s = s - s.mean()
    win = np.hanning(len(s))
    F = np.abs(np.fft.rfft(s*win)); fr = np.fft.rfftfreq(len(s), 1/fps)
    sel = (fr>=band[0])&(fr<=band[1])
    f_fft = float(fr[sel][np.argmax(F[sel])])
    ac = np.correlate(s, s, "full")[len(s)-1:]; ac = ac/ac[0] if ac[0] else ac
    lo, hi = int(fps/band[1]), int(fps/band[0])
    lag = lo + int(np.argmax(ac[lo:hi]))
    return dict(fft_hz=round(f_fft,3), ac_hz=round(float(fps/lag),3), ac_peak=round(float(ac[lag]),3))

res = {"clip": cfg["name"], "window": [t0, t1], "frames": n}
for nm, s in (("dark_frac",dark),("bh",bh),("bw",bw),("area",area)):
    res[nm] = estimate(s)
np.savez(cfg["out"]+"_sig.npz", dark=dark, bh=bh, bw=bw, area=area, ax=ax, ay=ay)
# dense strip
tile = cfg.get("tile", 90); cols = cfg.get("cols", 15)
f0, f1 = cfg.get("f0",0), cfg.get("f1",n)
sel = crops[f0:f1]
rows = (len(sel)+cols-1)//cols
sheet = np.full((rows*tile, cols*tile), 30, dtype=np.uint8)
for k, c in enumerate(sel):
    small = np.asarray(Image.fromarray(c).resize((tile,tile), Image.BILINEAR))
    r, cc = divmod(k, cols)
    sheet[r*tile:(r+1)*tile, cc*tile:(cc+1)*tile] = small
Image.fromarray(sheet).save(cfg["out"]+"_strip.jpg")
print(json.dumps(res, indent=1))
