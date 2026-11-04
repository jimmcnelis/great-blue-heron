"""Creature Engine CLI.

  python3 -m engine.run validate   <scene_dir> [--root packages]
  python3 -m engine.run corpus     <scene_dir> --out DIR [--only kind,...]
  python3 -m engine.run episode    <scene_dir> --corpus DIR --out DIR
  python3 -m engine.run schedule   <scene_dir> --char ID --mode MODE --duration S
  python3 -m engine.run qa         <scene_dir> --episode DIR
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import corpus as corpus_mod
from engine import episode as episode_mod
from engine import qa as qa_mod
from engine.behavior import Policy
from engine.package import Scene


def cmd_validate(a):
    sc = Scene(a.scene, a.root)
    print(f"scene {sc.id}: OK — chars={sc.char_order} env={sc.environment.id} "
          f"style={sc.style.id} design={sc.design_w}x{sc.design_h} grid={sc.grid_w}x{sc.grid_h}")
    for cid in sc.char_order:
        sp = sc.characters[cid]
        print(f"  {cid}: species={sp.id} palette={len(sp.palette_names)} "
              f"roster={len(sp.roster)} behaviors={'yes' if sp.behaviors else 'no'}")
    return 0


def cmd_corpus(a):
    sc = Scene(a.scene, a.root)
    only = a.only.split(',') if a.only else None
    for cid in sc.char_order:
        print(f"[{cid}] species {sc.characters[cid].id}")
        corpus_mod.build_character(sc, cid, a.out, only=only)
    return 0


def cmd_episode(a):
    sc = Scene(a.scene, a.root)
    grids, palette, log = episode_mod.render_episode(sc, a.corpus)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    np.save(out / 'episode_grids.npy', grids)
    (out / 'episode_log.json').write_text(json.dumps(log, indent=1))
    mp4 = out / 'episode.mp4'
    scale = max(1, 320 // sc.grid_w)
    ow, oh = sc.grid_w * scale, sc.grid_h * scale
    proc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo',
                             '-pix_fmt', 'rgb24', '-s', f'{ow}x{oh}', '-r', str(int(sc.fps)),
                             '-i', '-', '-c:v', 'libx264', '-crf', '10',
                             '-pix_fmt', 'yuv420p', str(mp4)], stdin=subprocess.PIPE)
    for g in grids:
        frame = np.asarray(Image.fromarray(palette[g]).resize((ow, oh), Image.NEAREST),
                           dtype=np.uint8)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close(); proc.wait()
    # contact sheet: segment midpoints
    picks = [(s['clip'], s['start'] + s['count'] // 2) for s in log['segments']][:12]
    cols = 4
    rows = max(1, int(np.ceil(len(picks) / cols)))
    cw, chh = 240, int(240 * sc.grid_h / sc.grid_w)
    sheet = Image.new('RGB', (cw * cols, chh * rows), (255, 255, 255))
    for i, (nm, fi) in enumerate(picks):
        im = Image.fromarray(palette[grids[fi]]).resize((cw, chh), Image.NEAREST)
        sheet.paste(im, ((i % cols) * cw, (i // cols) * chh))
    sheet.save(out / 'contact_sheet.jpg', quality=88)
    print(f"episode: {log['total_frames']} frames @ {sc.fps} fps -> {mp4}")
    print(f"segments: {[s['clip'] for s in log['segments']]}")
    return 0


def cmd_schedule(a):
    sc = Scene(a.scene, a.root)
    sp = sc.characters[a.char]
    pol = Policy(sp.behaviors)
    sched = pol.schedule(a.duration, a.mode)
    from collections import Counter
    counts = Counter(b for _, b in sched)
    print(f"{a.char} mode={a.mode} duration={a.duration}s -> {len(sched)} triggered behaviors")
    for bid, n in counts.most_common():
        print(f"  {bid}: {n}")
    return 0


def cmd_qa(a):
    sc = Scene(a.scene, a.root)
    ep = Path(a.episode)
    grids = np.load(ep / 'episode_grids.npy')
    log = json.loads((ep / 'episode_log.json').read_text())
    palette, offsets, _obj_offsets = episode_mod.merged_palette(sc)
    ink_idx = episode_mod.world_ink_index(sc, offsets)
    s = sc.grid_h / sc.design_h
    er = sc.environment.data.get('effect_region')
    planes = sc.environment.canvas_law.get('clip_planes', [])
    surface_row = int(round((er['y_center'] if er else planes[0]['at']) * s)) if (er or planes) else sc.grid_h // 2
    results = qa_mod.run_checks(
        sc.style.qa_checks, grids=grids, segments=log['segments'],
        events=log['events'], effect_map=sc.environment.effect_map,
        ink_index=ink_idx, palette_size=len(palette), surface_row=surface_row)
    print(json.dumps(results, indent=1))
    (ep / 'qa_results.json').write_text(json.dumps(results, indent=1))
    return 0


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd', required=True)
    for name in ('validate', 'corpus', 'episode', 'schedule', 'qa'):
        sp = sub.add_parser(name)
        sp.add_argument('scene')
        sp.add_argument('--root', default='packages')
    sub.choices['corpus'].add_argument('--out', required=True)
    sub.choices['corpus'].add_argument('--only', default=None)
    sub.choices['episode'].add_argument('--corpus', required=True)
    sub.choices['episode'].add_argument('--out', required=True)
    sub.choices['schedule'].add_argument('--char', required=True)
    sub.choices['schedule'].add_argument('--mode', required=True)
    sub.choices['schedule'].add_argument('--duration', type=float, default=3600)
    sub.choices['qa'].add_argument('--episode', required=True)
    a = p.parse_args()
    return {'validate': cmd_validate, 'corpus': cmd_corpus, 'episode': cmd_episode,
            'schedule': cmd_schedule, 'qa': cmd_qa}[a.cmd](a)


if __name__ == '__main__':
    raise SystemExit(main())
