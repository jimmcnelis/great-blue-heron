#!/usr/bin/env python3
"""Overlay tracked centroids on sample frames to validate a track by eye."""
import subprocess, sys, json
import numpy as np
from PIL import Image, ImageDraw

cfg = json.loads(sys.argv[1])
path, t0, fps, width = cfg["path"], cfg["t0"], cfg["fps"], cfg["width"]
tr = np.load(cfg["npz"])
idxs = cfg["idxs"]
tiles = []
for i in idxs:
    t = t0 + i/fps
    raw = subprocess.run(["ffmpeg","-v","error","-ss",str(t),"-i",path,"-frames:v","1",
                          "-vf",f"scale={width}:-1,format=rgb24","-f","rawvideo","-"],
                         capture_output=True, check=True).stdout
    h = len(raw)//(width*3)
    img = Image.fromarray(np.frombuffer(raw, dtype=np.uint8).reshape(h,width,3).copy())
    d = ImageDraw.Draw(img)
    cx, cy = tr["cx"][i], tr["cy"][i]
    if not np.isnan(cx):
        bw = tr["bw"][i] if "bw" in tr else 60; bh = tr["bh"][i] if "bh" in tr else 60
        d.rectangle([cx-bw/2, cy-bh/2, cx+bw/2, cy+bh/2], outline=(255,0,0), width=3)
        d.ellipse([cx-4,cy-4,cx+4,cy+4], fill=(255,255,0))
    d.text((8,8), f"f{i} t={t:.2f}", fill=(255,0,0))
    tiles.append(img.resize((360, int(360*h/width))))
W = tiles[0].width; H = tiles[0].height
sheet = Image.new("RGB", (W*len(tiles), H), (0,0,0))
for j,im in enumerate(tiles): sheet.paste(im, (j*W, 0))
sheet.save(cfg["out"])
print("saved", cfg["out"])
