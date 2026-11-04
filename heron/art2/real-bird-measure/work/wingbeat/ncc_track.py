#!/usr/bin/env python3
"""NCC template tracker + wingbeat signals from tracked crops.
Usage: ncc_track.py '<json cfg>'  (same cfg style as track.py, plus
"init":[nx,ny] normalized, "tpl":[w,h] template px, "search": px)"""
import subprocess, sys, json
import numpy as np
from scipy import signal

def decode(path, t0, t1, fps, width):
    cmd = ["ffmpeg","-v","error","-ss",str(t0),"-i",path,"-t",str(t1-t0),
           "-vf",f"fps={fps},scale={width}:-1,format=gray","-f","rawvideo","-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    one = subprocess.run(["ffmpeg","-v","error","-ss",str(t0),"-i",path,"-frames:v","1",
                          "-vf",f"scale={width}:-1,format=gray","-f","rawvideo","-"],
                         capture_output=True, check=True).stdout
    h = len(one)//width
    n = len(raw)//(width*h)
    return np.frombuffer(raw[:n*width*h], dtype=np.uint8).reshape(n,h,width).astype(np.float32), n

def ncc_track(frames, init_xy, tpl_wh, search=45, refresh=20):
    n,H,W = frames.shape
    tw,th = tpl_wh
    cx, cy = init_xy[0]*W, init_xy[1]*H
    def patch(f, cx, cy):
        x0 = int(round(cx-tw/2)); y0 = int(round(cy-th/2))
        x0 = min(max(x0,0), W-tw); y0 = min(max(y0,0), H-th)
        return f[y0:y0+th, x0:x0+tw], x0, y0
    tpl,_,_ = patch(frames[0], cx, cy)
    tpl0 = tpl.copy()
    vel = np.zeros(2)
    centers = np.zeros((n,2)); peaks = np.zeros(n)
    for i in range(n):
        f = frames[i]
        px, py = cx+vel[0], cy+vel[1]
        x0 = int(min(max(px-search-tw/2,0), W-tw)); x1 = int(min(max(px+search+tw/2,tw), W))
        y0 = int(min(max(py-search-th/2,0), H-th)); y1 = int(min(max(py+search+th/2,th), H))
        region = f[y0:y1, x0:x1]
        # normalized cross-correlation via fftconvolve
        t = tpl - tpl.mean()
        num = signal.fftconvolve(region, t[::-1,::-1], mode="valid")
        ii = np.cumsum(np.cumsum(region,0),1); ii = np.pad(ii,((1,0),(1,0)))
        ii2 = np.cumsum(np.cumsum(region**2,0),1); ii2 = np.pad(ii2,((1,0),(1,0)))
        rh, rw = region.shape[0]-th+1, region.shape[1]-tw+1
        s1 = ii[th:th+rh, tw:tw+rw] - ii[:rh, tw:tw+rw] - ii[th:th+rh, :rw] + ii[:rh, :rw]
        s2 = ii2[th:th+rh, tw:tw+rw] - ii2[:rh, tw:tw+rw] - ii2[th:th+rh, :rw] + ii2[:rh, :rw]
        var = np.maximum(s2 - s1**2/(th*tw), 1e-6)
        ncc = num/np.sqrt(var*(t**2).sum())
        j = np.argmax(ncc)
        by, bx = np.unravel_index(j, ncc.shape)
        ncx, ncy = x0+bx+tw/2, y0+by+th/2
        vel = 0.5*vel + 0.5*np.array([ncx-cx, ncy-cy])
        cx, cy = ncx, ncy
        centers[i] = (cx,cy); peaks[i] = ncc[by,bx]
        if refresh and i>0 and i % refresh == 0:
            p,_,_ = patch(f, cx, cy)
            tpl = 0.5*tpl + 0.5*p
    return centers, peaks, tpl0

def crop_signals(frames, centers, crop):
    n = len(frames); H,W = frames.shape[1:]
    half = crop//2
    dark_frac = np.zeros(n); vcent = np.zeros(n); bh = np.zeros(n); bw = np.zeros(n)
    for i in range(n):
        cx, cy = centers[i]
        x0 = int(min(max(cx-half,0), W-crop)); y0 = int(min(max(cy-half,0), H-crop))
        c = frames[i][y0:y0+crop, x0:x0+crop]
        thr = c.min() + 0.45*(np.percentile(c,90)-c.min())
        mask = c < thr
        dark_frac[i] = mask.mean()
        ys, xs = np.nonzero(mask)
        if len(ys) > 5:
            wts = (thr - c[mask])
            vcent[i] = np.average(ys, weights=wts)/crop
            bh[i] = ys.max()-ys.min(); bw[i] = xs.max()-xs.min()
        else:
            vcent[i] = np.nan; bh[i] = np.nan; bw[i] = np.nan
    return dict(dark_frac=dark_frac, vcent=vcent, bh=bh, bw=bw)

def estimate(sig, fps, band=(1.2,4.0)):
    s = sig.copy(); ok = ~np.isnan(s)
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
    return dict(fft_hz=f_fft, ac_hz=float(fps/lag), ac_peak=float(ac[lag]))

if __name__ == "__main__":
    cfg = json.loads(sys.argv[1])
    frames, n = decode(cfg["path"], cfg["t0"], cfg["t1"], cfg["fps"], cfg["width"])
    centers, peaks, _ = ncc_track(frames, cfg["init"], cfg["tpl"], cfg.get("search",45), cfg.get("refresh",20))
    sigs = crop_signals(frames, centers, cfg.get("crop",110))
    res = {"clip": cfg["name"], "window": [cfg["t0"], cfg["t1"]], "frames": n,
           "ncc_peak_med": float(np.median(peaks)), "ncc_peak_min": float(np.min(peaks))}
    for sname, s in sigs.items():
        res[sname] = estimate(s, cfg["fps"])
    np.savez(cfg["out"]+"_ncc.npz", cx=centers[:,0], cy=centers[:,1], peak=peaks, **sigs)
    with open(cfg["out"]+"_ncc.csv","w") as fh:
        fh.write("frame,cx,cy,ncc,dark_frac,vcent,bh,bw\n")
        for i in range(n):
            fh.write(f"{i},{centers[i,0]:.1f},{centers[i,1]:.1f},{peaks[i]:.3f},{sigs['dark_frac'][i]:.4f},{sigs['vcent'][i]:.3f},{sigs['bh'][i]:.1f},{sigs['bw'][i]:.1f}\n")
    print(json.dumps(res, indent=1))
