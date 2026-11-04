import os, sys
os.environ.setdefault('U2NET_HOME', os.path.expanduser('~/workspace/heron/art2/route3/work/.u2net'))
import numpy as np
from PIL import Image
from rembg import new_session, remove

W = os.path.expanduser('~/workspace/heron/art2/route3/work')
session = new_session('isnet-general-use')

jobs = [
    (os.path.expanduser('~/workspace/heron/reference/real-heron-b.jpg'), 'alpha_b.png', None),
    (os.path.expanduser('~/workspace/heron/reference/real-heron-a.jpg'), 'alpha_a.png', None),
    (f'{W}/patio_16.jpg', 'alpha_patio.png', (1000, 250, 1280, 720)),
    (f'{W}/night5_12.7.jpg', 'alpha_night5.png', (300, 0, 780, 420)),
]
for src, out, crop in jobs:
    im = Image.open(src).convert('RGB')
    if crop: im = im.crop(crop)
    im.save(f'{W}/{out.replace("alpha_","src_").replace(".png",".png")}')
    res = remove(im, session=session, only_mask=True)
    res.save(f'{W}/{out}')
    a = np.asarray(res)
    print(out, im.size, 'alpha>128 frac', round(float((a>128).mean()),4))
print('SEG_DONE')
