"""Contact sheets for the roster build (run locally after frames land).
Per-chart strip sheets + one master sheet of signature frames."""
import json, os, sys
from PIL import Image, ImageDraw

ROSTER = sys.argv[1] if len(sys.argv) > 1 else \
    os.path.expanduser('~/workspace/heron/art2/route2/roster')
FRAMES = os.path.join(ROSTER, 'frames')

SIGNATURE = {'idle_hunt': 30, 'head_saccade': 1, 'head_turn': 10,
             'strike': 27, 'swallow': 84, 'step_cycle': 14, 'turn': 33,
             'alert': 20, 'takeoff': 30, 'flight_cycle': 5, 'glide': 6,
             'landing': 35, 'stretch': 90, 'oneleg': 35, 'doze': 70,
             'preen': 100, 'scratch': 27}
ORDER = ['idle_hunt', 'head_saccade', 'head_turn', 'alert', 'step_cycle',
         'turn', 'strike', 'swallow', 'stretch', 'oneleg', 'doze',
         'preen', 'scratch', 'takeoff', 'flight_cycle', 'glide',
         'landing']

def strip(chart, max_frames=32):
    d = os.path.join(FRAMES, chart)
    files = sorted(f for f in os.listdir(d) if f.endswith('.png'))
    n = len(files)
    if n > max_frames:
        idx = [round(i * (n - 1) / (max_frames - 1)) for i in range(max_frames)]
    else:
        idx = list(range(n))
    tw, th, lab = 256, 150, 16
    cols = 8
    rows = (len(idx) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * tw, rows * (th + lab) + lab), 'white')
    dr = ImageDraw.Draw(sheet)
    dr.text((6, 2), f'{chart} — {n} frames (strip of {len(idx)})',
            fill=(0, 0, 0))
    for j, fi in enumerate(idx):
        im = Image.open(os.path.join(d, files[fi])).resize((tw, th))
        x, y = (j % cols) * tw, lab + (j // cols) * (th + lab)
        sheet.paste(im, (x, y))
        dr.text((x + 4, y + th + 2), f'f{fi}', fill=(0, 0, 0))
    out = os.path.join(ROSTER, f'contact_{chart}.png')
    sheet.save(out)
    print('strip', chart, n, '->', out)

def master():
    tw, th, lab = 341, 200, 18
    cols = 3
    rows = (len(ORDER) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * tw, rows * (th + lab) + lab), 'white')
    dr = ImageDraw.Draw(sheet)
    dr.text((6, 2), 'ROSTER — signature frames (Route 2 Fix 1, step-6000)',
            fill=(0, 0, 0))
    for j, chart in enumerate(ORDER):
        fi = SIGNATURE[chart]
        im = Image.open(os.path.join(FRAMES, chart, f'f{fi:04d}.png'))
        im = im.resize((tw, th))
        x, y = (j % cols) * tw, lab + (j // cols) * (th + lab)
        sheet.paste(im, (x, y))
        dr.text((x + 4, y + th + 2), f'{chart} f{fi}', fill=(0, 0, 0))
    out = os.path.join(ROSTER, 'contact_master.png')
    sheet.save(out)
    print('master ->', out)

if __name__ == '__main__':
    for c in ORDER:
        strip(c)
    master()
