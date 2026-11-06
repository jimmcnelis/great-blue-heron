import sys, numpy as np
from PIL import Image

def orange_mask(im):
    a = np.asarray(im.convert('RGB')).astype(int)
    R,G,B = a[...,0], a[...,1], a[...,2]
    return (R>150)&(G>70)&(G<190)&(B<110)&((R-B)>70)

def tip_of(path):
    im = Image.open(path).convert('RGB')
    m = orange_mask(im)
    ys, xs = np.nonzero(m)
    if len(xs)==0: return None
    # bill tip: extreme in direction of bill (down-right): maximize x*0.6 + y
    score = xs*0.6 + ys
    i = np.argmax(score)
    W,H = im.size
    return (round(xs[i]/W*1000), round(ys[i]/H*1000))

def feet_of(path):
    im = Image.open(path).convert('L')
    a = np.asarray(im).astype(float)
    H,W = a.shape
    band = a[int(H*0.90):, int(W*0.10):int(W*0.32)]
    ys, xs = np.nonzero(band < 170)
    if len(xs)==0: return None
    return round((xs.mean()/band.shape[1])*220 + 100)

if __name__ == '__main__':
    for p in sys.argv[1:]:
        im = Image.open(p)
        print(p.split('/')[-1], 'tip', tip_of(p), 'feet', feet_of(p))
