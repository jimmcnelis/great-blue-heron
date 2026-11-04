#!/usr/bin/env python3
"""Wingbeat tracker: follow the dark bird blob in a window, record bbox signals,
then FFT + autocorrelation period estimate in the 1.2-4.0 Hz band."""
import subprocess, sys, json
import numpy as np
from scipy import ndimage, signal

def decode(path, t0, t1, fps, width):
    cmd = ["ffmpeg","-v","error","-ss",str(t0),"-i",path,"-t",str(t1-t0),
           "-vf",f"fps={fps},scale={width}:-1,format=gray","-f","rawvideo","-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    w = width
    one = subprocess.run(["ffmpeg","-v","error","-ss",str(t0),"-i",path,"-frames:v","1",
                          "-vf",f"scale={width}:-1,format=gray","-f","rawvideo","-"],
                         capture_output=True, check=True).stdout
    h = len(one)//w
    n = len(raw)//(w*h)
    return np.frombuffer(raw[:n*w*h], dtype=np.uint8).reshape(n,h,w).astype(np.float32), n

def track(frames, init_xy, thresh, search=90, min_area=6):
    """init_xy: (x,y) normalized guess for frame 0. Returns per-frame dict arrays."""
    n,H,W = frames.shape
    cx, cy = init_xy[0]*W, init_xy[1]*H
    out = {k: np.full(n, np.nan) for k in ("cx","cy","bw","bh","area")}
    vel = np.zeros(2)
    for i in range(n):
        f = frames[i]
        x0,x1 = int(max(0,cx-search)), int(min(W,cx+search))
        y0,y1 = int(max(0,cy-search)), int(min(H,cy+search))
        roi = f[y0:y1, x0:x1]
        mask = roi < thresh
        lab, m = ndimage.label(mask)
        best = None
        if m:
            objs = ndimage.find_objects(lab)
            for j,sl in enumerate(objs):
                area = int((lab[sl]==j+1).sum())
                if area < min_area: continue
                yy,xx = np.nonzero(lab[sl]==j+1)
                ccx, ccy = x0+sl[1].start+xx.mean(), y0+sl[0].start+yy.mean()
                d = np.hypot(ccx-(cx+vel[0]), ccy-(cy+vel[1]))
                bw = sl[1].stop-sl[1].start; bh = sl[0].stop-sl[0].start
                score = d - 0.3*area
                if best is None or score < best[0]:
                    best = (score, ccx, ccy, bw, bh, area)
        if best is not None:
            _,ncx,ncy,bw,bh,area = best
            vel = 0.6*vel + 0.4*np.array([ncx-cx, ncy-cy])
            cx, cy = ncx, ncy
            out["cx"][i], out["cy"][i] = cx, cy
            out["bw"][i], out["bh"][i], out["area"][i] = bw, bh, area
        else:
            cx += vel[0]; cy += vel[1]
    return out

def estimate(sig, fps, band=(1.2,4.0)):
    s = sig.copy()
    ok = ~np.isnan(s)
    if ok.sum() < 20: return None
    s[~ok] = np.interp(np.nonzero(~ok)[0], np.nonzero(ok)[0], s[ok])
    k = int(fps*0.9)//2*2+1
    s = s - signal.medfilt(s, kernel_size=k)
    s = s - s.mean()
    # FFT
    win = np.hanning(len(s))
    F = np.abs(np.fft.rfft(s*win)); fr = np.fft.rfftfreq(len(s), 1/fps)
    sel = (fr>=band[0])&(fr<=band[1])
    f_fft = fr[sel][np.argmax(F[sel])]
    # autocorrelation
    ac = np.correlate(s, s, "full")[len(s)-1:]
    ac /= ac[0]
    lo, hi = int(fps/band[1]), int(fps/band[0])
    lag = lo + np.argmax(ac[lo:hi])
    return dict(fft_hz=float(f_fft), ac_hz=float(fps/lag), ac_peak=float(ac[lag]))

if __name__ == "__main__":
    cfg = json.loads(sys.argv[1])
    frames, n = decode(cfg["path"], cfg["t0"], cfg["t1"], cfg["fps"], cfg["width"])
    tr = track(frames, cfg["init"], cfg["thresh"])
    res = {"clip": cfg["name"], "window": [cfg["t0"], cfg["t1"]], "frames": n,
           "tracked": int((~np.isnan(tr["area"])).sum())}
    for sname in ("bw","bh","area"):
        e = estimate(tr[sname], cfg["fps"])
        res[sname] = e
    np.savez(cfg["out"]+".npz", **tr)
    with open(cfg["out"]+".csv","w") as fh:
        fh.write("frame,cx,cy,bw,bh,area\n")
        for i in range(n):
            fh.write(f"{i},{tr['cx'][i]:.1f},{tr['cy'][i]:.1f},{tr['bw'][i]:.1f},{tr['bh'][i]:.1f},{tr['area'][i]:.1f}\n")
    print(json.dumps(res, indent=1))
