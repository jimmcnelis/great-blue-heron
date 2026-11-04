"""Upscaled crop with a grid labeled in SOURCE pixel coordinates.
Usage: gridcrop.py IMAGE X0 Y0 X1 Y1 SCALE OUT [STEP]"""
import sys
from PIL import Image, ImageDraw, ImageFont

src, x0, y0, x1, y1, sc, dst = sys.argv[1], *map(int, sys.argv[2:7]), sys.argv[7]
step = int(sys.argv[8]) if len(sys.argv) > 8 else 20
im = Image.open(src).convert('RGB')
crop = im.crop((x0, y0, x1, y1)).resize(((x1 - x0) * sc, (y1 - y0) * sc),
                                       Image.LANCZOS)
d = ImageDraw.Draw(crop)
try:
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
except Exception:
    f = ImageFont.load_default()
for x in range((x0 // step) * step, x1, step):
    px = (x - x0) * sc
    d.line([(px, 0), (px, crop.height)], fill=(255, 60, 60), width=1)
    d.text((px + 2, 2), str(x), fill=(255, 60, 60), font=f)
for y in range((y0 // step) * step, y1, step):
    py = (y - y0) * sc
    d.line([(0, py), (crop.width, py)], fill=(60, 120, 255), width=1)
    d.text((2, py + 2), str(y), fill=(60, 120, 255), font=f)
crop.save(dst)
print('gridcrop ->', dst, crop.size)
