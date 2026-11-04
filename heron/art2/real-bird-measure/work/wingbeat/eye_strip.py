#!/usr/bin/env python3
"""Dense every-frame strip of tracked-bird crops for the eye route."""
import subprocess, sys, json
import numpy as np
from PIL import Image

cfg = json.loads(sys.argv[1])
path, t0, fps, width = cfg["path"], cfg["t0"], cfg["fps"], cfg["width"]
tr = np.load(cfg["npz"])
f0, f1 = cfg["f0"], cfg["f1"]
n = f1 - f0
dur = n / fps
seek = t0 + f0/fps
cmd = ["ffmpeg","-v","error","-ss",str(seek),"-i",path,"-t",str(dur+0.2),
       "-vf",f"fps={fps},scale={width}:-1,format=gray","-f","rawvideo","-"]
raw = subprocess.run(cmd, capture_output=True, check=True).stdout
one = subprocess.run(["ffmpeg","-v","error","-ss",str(t0),"-i",path,"-frames:v","1",
                      "-vf",f"scale={width}:-1,format=gray","-f","rawvideo","-"],
                     capture_output=True, check=True).stdout
H = len(one)//width
frames = np.frombuffer(raw[: (len(raw)//(width*H)) *width*H], dtype=np.uint8).reshape(-1,H,width)
crop = cfg.get("crop", 110); half = crop//2; tile = cfg.get("tile", 76)
cols = cfg.get("cols", 15)
rows = (n + cols - 1)//cols
sheet = np.full((rows*tile, cols*tile), 30, dtype=np.uint8)
for k in range(n):
    i = f0 + k
    cx, cy = tr["cx"][i], tr["cy"][i]
    if np.isnan(cx): cx, cy = width/2, H/2
    cx, cy = int(cx) + cfg.get("dx",0), int(cy) + cfg.get("dy",0)
    x0, y0 = max(0, cx-half), max(0, cy-half)
    patch = frames[k][y0:y0+crop, x0:x0+crop]
    if patch.shape != (crop, crop):
        tmp = np.zeros((crop,crop), dtype=np.uint8); tmp[:patch.shape[0],:patch.shape[1]] = patch; patch = tmp
    small = np.asarray(Image.fromarray(patch).resize((tile,tile), Image.BILINEAR))
    r, c = divmod(k, cols)
    sheet[r*tile:(r+1)*tile, c*tile:(c+1)*tile] = small
Image.fromarray(sheet).save(cfg["out"])
print("saved", cfg["out"], "frames", n, "abs window", t0+f0/fps, "to", t0+f1/fps)
