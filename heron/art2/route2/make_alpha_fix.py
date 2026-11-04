"""Fix-build variant of make_alpha.py: plates_fix/ -> alpha_fix/.
Same derivation: bird = darker and/or more saturated than near-white paper;
largest connected component + near neighbours >1% of its area."""
import os, glob
import numpy as np, cv2
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(HERE, 'alpha_fix'), exist_ok=True)
for f in sorted(glob.glob(os.path.join(HERE, 'plates_fix', 'plate_*.png'))):
    name = os.path.basename(f)[:-4]
    im = cv2.imread(f)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(np.float32)
    lum = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    sat = hsv[:,:,1]
    score = np.maximum(242.0-lum, (sat-18)*1.1)
    alpha_soft = np.clip(score*2.6, 0, 255)
    bw = (alpha_soft > 110).astype(np.uint8)
    bw = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, np.ones((7,7),np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(bw, 8)
    areas = stats[1:, cv2.CC_STAT_AREA]
    big = 1+int(np.argmax(areas))
    keep = np.zeros(n, bool); keep[big] = True
    bx,by,bw_,bh = stats[big,0],stats[big,1],stats[big,2],stats[big,3]
    for i in range(1,n):
        if areas[i-1] > 0.01*areas.max():
            x,y,w,h = stats[i,0],stats[i,1],stats[i,2],stats[i,3]
            if x < bx+bw_*1.15 and x+w > bx*0.85 and y < by+bh and y+h > by:
                keep[i] = True
    mask = keep[lab]
    a = np.where(mask, alpha_soft, 0).astype(np.uint8)
    a = cv2.GaussianBlur(a, (3,3), 0)
    Image.fromarray(a).save(os.path.join(HERE, 'alpha_fix', name + '.png'))
    print(name, 'bird px %.1f%%' % (100*mask.mean()))
