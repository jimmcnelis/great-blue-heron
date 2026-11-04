"""Overlay a labeled coordinate grid on an image so keypoints can be read
off visually. Usage: make_grid.py IN OUT [STEP]  (grid every STEP px,
labels = source pixel coords)."""
import sys
from PIL import Image, ImageDraw, ImageFont

src, dst = sys.argv[1], sys.argv[2]
step = int(sys.argv[3]) if len(sys.argv) > 3 else 80
im = Image.open(src).convert('RGB')
d = ImageDraw.Draw(im)
try:
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
except Exception:
    f = ImageFont.load_default()
W, H = im.size
for x in range(0, W, step):
    d.line([(x, 0), (x, H)], fill=(255, 60, 60), width=1)
    d.text((x + 2, 2), str(x), fill=(255, 60, 60), font=f)
for y in range(0, H, step):
    d.line([(0, y), (W, y)], fill=(60, 60, 255), width=1)
    d.text((2, y + 2), str(y), fill=(60, 60, 255), font=f)
im.save(dst)
print('grid ->', dst, im.size)
