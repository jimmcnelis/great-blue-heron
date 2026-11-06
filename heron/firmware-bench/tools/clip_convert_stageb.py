#!/usr/bin/env python3
"""Stage B clip converter: mp4 -> normalized, PIL-encoded MJPEG @12fps.

Route (proven Stage A): PIL/libjpeg, subsampling=1 (4:2:2 as 2x1/1x1/1x1 --
the only layout the ESP32-P4 JPEG driver recognizes), optimize=True.

Background normalization: generated clips carry grain + a warm cast over
the whole frame. Estimate the clip background B from border pixels
(median over sampled frames); the paper target P is the approved plate's
border median. Near-background pixels are pulled toward P with their
deviation from B damped (grain reduction); pixels far from B (the bird)
are untouched. Weight is a smoothstep ramp on RGB distance from B.
"""
import io, os, struct, subprocess, sys, tempfile
import numpy as np
from PIL import Image

PLATE = os.path.expanduser(
    "~/workspace/heron/art2/plates-fresh/eye-first/final/alert_legfix_approved.png")
DAMP = 0.35          # background deviation damping (grain cut)
D_LO, D_HI = 12.0, 45.0   # distance ramp: full weight <= D_LO, none >= D_HI


def border_pixels(arr, t=10):
    """arr: HxWx3 float. Returns Nx3 border pixel sample."""
    top = arr[:t].reshape(-1, 3); bot = arr[-t:].reshape(-1, 3)
    lef = arr[:, :t].reshape(-1, 3); rig = arr[:, -t:].reshape(-1, 3)
    return np.concatenate([top, bot, lef, rig])


def paper_target():
    im = np.asarray(Image.open(PLATE).convert("RGB"), dtype=np.float32)
    return np.median(border_pixels(im), axis=0)


def smoothstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def normalize(frame, bg, paper):
    """frame: HxWx3 float32. Pull near-bg pixels toward paper."""
    d = np.sqrt(((frame - bg) ** 2).sum(axis=2))
    w = 1.0 - smoothstep((d - D_LO) / (D_HI - D_LO))
    target = paper + (frame - bg) * DAMP
    out = frame + w[..., None] * (target - frame)
    return np.clip(out, 0, 255)


def bg_stats(frames_dir, files):
    """Border mean/std over the given frame files (float arrays)."""
    vals = []
    for f in files:
        arr = np.asarray(Image.open(os.path.join(frames_dir, f)).convert("RGB"),
                         dtype=np.float32)
        vals.append(border_pixels(arr))
    allb = np.concatenate(vals)
    return allb.mean(axis=0), allb.std(axis=0)


def convert(mp4, out_path, quality, frames_out_dir=None):
    tmp = tempfile.mkdtemp(prefix="stageb_frames_")
    subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf",
                    "select='not(mod(n,2))'", "-vsync", "0",
                    os.path.join(tmp, "f%04d.png")], check=True)
    files = sorted(os.listdir(tmp))
    assert len(files) == 120, f"{mp4}: expected 120 frames, got {len(files)}"

    paper = paper_target()
    # clip background estimate: border medians of every 10th frame
    meds = []
    for f in files[::10]:
        arr = np.asarray(Image.open(os.path.join(tmp, f)).convert("RGB"),
                         dtype=np.float32)
        meds.append(np.median(border_pixels(arr), axis=0))
    bg = np.median(np.stack(meds), axis=0)

    before_mean, before_std = bg_stats(tmp, files[::10])

    sizes = []
    with open(out_path, "wb") as out:
        for i, f in enumerate(files):
            arr = np.asarray(Image.open(os.path.join(tmp, f)).convert("RGB"),
                             dtype=np.float32)
            norm = normalize(arr, bg, paper).astype(np.uint8)
            if frames_out_dir and i in (0, 60, 119):
                Image.fromarray(norm).save(
                    os.path.join(frames_out_dir, f"norm_{i:04d}.png"))
                Image.fromarray(arr.astype(np.uint8)).save(
                    os.path.join(frames_out_dir, f"raw_{i:04d}.png"))
            buf = io.BytesIO()
            Image.fromarray(norm).save(buf, "JPEG", quality=quality,
                                       subsampling=1, optimize=True)
            data = buf.getvalue()
            sizes.append(len(data))
            out.write(data)

    after_mean, after_std = None, None
    # after-stats: decode the mjpeg frames back and measure borders
    data = open(out_path, "rb").read()
    frames, i = [], 0
    while True:
        s = data.find(b"\xff\xd8", i)
        if s < 0:
            break
        e = data.find(b"\xff\xd9", s)
        frames.append(data[s:e + 2])
        i = e + 2
    samples = []
    for fr in frames[::10]:
        arr = np.asarray(Image.open(io.BytesIO(fr)).convert("RGB"),
                         dtype=np.float32)
        samples.append(border_pixels(arr))
    allb = np.concatenate(samples)
    after_mean, after_std = allb.mean(axis=0), allb.std(axis=0)

    return dict(frames=len(sizes), total=sum(sizes), max_frame=max(sizes),
                avg=sum(sizes) / len(sizes), bg=bg.tolist(),
                paper=paper.tolist(),
                before_mean=before_mean.tolist(),
                before_std=before_std.tolist(),
                after_mean=after_mean.tolist(),
                after_std=after_std.tolist())


if __name__ == "__main__":
    mp4, out, q = sys.argv[1], sys.argv[2], int(sys.argv[3])
    fout = sys.argv[4] if len(sys.argv) > 4 else None
    if fout:
        os.makedirs(fout, exist_ok=True)
    import json
    print(json.dumps(convert(mp4, out, q, fout), indent=1))
