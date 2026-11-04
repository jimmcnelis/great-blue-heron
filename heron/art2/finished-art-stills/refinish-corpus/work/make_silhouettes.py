import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.expanduser('~/workspace/heron/art2/finished-art-stills/refinish-corpus/work'))
from gate import rig_silhouette
OUT = os.path.expanduser('~/workspace/heron/art2/finished-art-stills/refinish-corpus/work/silhouettes')
os.makedirs(OUT, exist_ok=True)
ids = ['idle_hold'] + [f'strike_f{i:04d}' for i in range(52)]
for pid in ids:
    sil = rig_silhouette(pid)
    img = np.full((600, 1024, 3), 255, np.uint8)
    img[sil] = (0, 0, 0)
    Image.fromarray(img).save(os.path.join(OUT, pid + '.png'))
print('wrote', len(ids), 'silhouettes to', OUT)
