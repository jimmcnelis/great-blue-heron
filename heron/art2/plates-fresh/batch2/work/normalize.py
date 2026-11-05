import sys
from PIL import Image
src, dst, yfrac = sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv)>3 else 0.5
im = Image.open(src).convert('RGB')
W,H = im.size
target = 1024/600
ch = int(W/target)          # crop height for full width
if ch <= H:
    y0 = int((H-ch)*yfrac)
    im = im.crop((0,y0,W,y0+ch))
else:                        # image too tall-narrow: crop width
    cw = int(H*target); x0=(W-cw)//2
    im = im.crop((x0,0,x0+cw,H))
im = im.resize((1024,600), Image.LANCZOS)
im.save(dst)
print(dst, im.size)
