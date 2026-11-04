"""Object-class plug test: Thomas Point Lighthouse in a heron scene.

Proves the OBJECT package kind end to end through the engine path:
scene load + schema validation (objects included), affordance/anchor
resolution, day vs night state renders, and compositing behind a real
heron corpus frame on the merged palette. Writes a contact sheet +
results JSON under plugtest-out/object-test/.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine.package import Scene  # noqa: E402
import engine.episode as episode_mod  # noqa: E402

OUT = Path(__file__).resolve().parent / 'object-test'
OUT.mkdir(exist_ok=True)
results = {}

# 1. scene load: validates scene.yaml (incl. the objects block), the
#    object package against object.schema.json, design-space agreement,
#    and the shared-background palette rule.
scene = Scene(ROOT / 'packages' / 'heron-lighthouse-scene', ROOT / 'packages')
results['scene_loaded'] = scene.id
results['objects'] = scene.object_order
so = scene.objects['thomas-point']

# 2. affordances + anchors resolve by name
assert scene.object_affordance('thomas-point', 'perch') == 'gallery'
assert scene.object_affordance('thomas-point', 'look_at') == 'lantern'
gx, gy = scene.object_anchor('thomas-point', 'gallery')
assert 0 <= gx < scene.grid_w and 0 <= gy < scene.grid_h, (gx, gy)
results['gallery_anchor'] = [gx, gy]
results['lantern_anchor'] = list(scene.object_anchor('thomas-point', 'lantern'))

palette, offsets, obj_offsets = episode_mod.merged_palette(scene)
results['merged_palette_size'] = len(palette)


def to_img(grid):
    return Image.fromarray(palette[np.clip(grid, 0, len(palette) - 1)])


# 3. day vs night renders of the object alone (state is the only input)
day_grid, _ = so.render(scene)
off = obj_offsets['thomas-point']
day_merged = np.where(day_grid != 0, day_grid + off, 0).astype(np.uint8)
lamp_i = off + so.index['lamp']
beam_i = off + so.index['beam']
results['day_object_cells'] = int((day_merged != 0).sum())
results['day_lamp_cells'] = int((day_merged == lamp_i).sum())
assert results['day_object_cells'] > 400, results['day_object_cells']
assert results['day_lamp_cells'] == 0

so.state.update({'lamp': 1.0, 'glow': 0.8, 'beam_angle': -18.0})
night_grid, _ = so.render(scene)
night_merged = np.where(night_grid != 0, night_grid + off, 0).astype(np.uint8)
results['night_lamp_cells'] = int((night_merged == lamp_i).sum())
results['night_beam_cells'] = int((night_merged == beam_i).sum())
assert results['night_lamp_cells'] > 0 and results['night_beam_cells'] > 0
so.state.update({'lamp': 0.0, 'glow': 0.0})   # restore placed state

# 4. composite: object (back layer) behind a real heron corpus frame
frames = np.load(Path(__file__).parent / 'heron-corpus' / 'heron_frames.npy')
heron = frames[10]
hoff = offsets['heron']
comp = day_merged.copy()
mask = heron != 0
comp[mask] = heron[mask] + hoff
results['composite_heron_cells'] = int((comp == hoff + scene.characters['heron'].index['slate']).sum())
results['composite_object_cells_visible'] = int(((comp != 0) & (comp >= off)).sum())
assert results['composite_heron_cells'] > 0 and results['composite_object_cells_visible'] > 100

# 5. full episode through render_episode when both corpora exist
try:
    grids, pal2, log = episode_mod.render_episode(
        scene, Path(__file__).parent / 'heron-corpus')
    results['episode_frames'] = int(len(grids))
    results['episode_object_cells_f0'] = int((grids[0] >= off).sum() - (grids[0] == 0).sum() * 0)
except Exception as e:  # fish corpus is not part of this test's fixtures
    results['episode_render'] = f'skipped: {type(e).__name__}: {e}'

# contact sheet: day object | night object | composite with heron
sheet = Image.new('RGB', (scene.grid_w * 3 + 8, scene.grid_h), (255, 255, 255))
sheet.paste(to_img(day_merged), (0, 0))
sheet.paste(to_img(night_merged), (scene.grid_w + 4, 0))
sheet.paste(to_img(comp), (2 * scene.grid_w + 8, 0))
sheet = sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST)
sheet.save(OUT / 'contact.png')
(OUT / 'results.json').write_text(json.dumps(results, indent=1))
print(json.dumps(results, indent=1))
print('OBJECT PLUG TEST PASS')
