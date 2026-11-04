"""Shared helpers for the head-anchor work: thinning, centreline
Dijkstra, arc length. Imported by measure_anchor.py / solve_anchor.py
(kept separate so the measurement module is import-safe)."""
import heapq
import numpy as np


def zhang_suen(mask):
    """Binary thinning (Zhang-Suen), numpy-vectorised."""
    img = mask.astype(np.uint8)
    changed = True
    while changed:
        changed = False
        for step in (0, 1):
            P = img
            P2 = np.roll(P, 1, axis=0)
            P3 = np.roll(np.roll(P, 1, axis=0), 1, axis=1)
            P4 = np.roll(P, 1, axis=1)
            P5 = np.roll(np.roll(P, -1, axis=0), 1, axis=1)
            P6 = np.roll(P, -1, axis=0)
            P7 = np.roll(np.roll(P, -1, axis=0), -1, axis=1)
            P8 = np.roll(P, -1, axis=1)
            P9 = np.roll(np.roll(P, 1, axis=0), -1, axis=1)
            nbrs = P2 + P3 + P4 + P5 + P6 + P7 + P8 + P9
            seq = [P2, P3, P4, P5, P6, P7, P8, P9, P2]
            trans = np.zeros_like(img)
            for a_, b_ in zip(seq[:-1], seq[1:]):
                trans += ((a_ == 0) & (b_ == 1)).astype(np.uint8)
            if step == 0:
                cond = (P2 * P4 * P6 == 0) & (P4 * P6 * P8 == 0)
            else:
                cond = (P2 * P4 * P8 == 0) & (P2 * P6 * P8 == 0)
            kill = (P == 1) & (nbrs >= 2) & (nbrs <= 6) & (trans == 1) & cond
            kill[0, :] = kill[-1, :] = False
            kill[:, 0] = kill[:, -1] = False
            if kill.any():
                img[kill] = 0
                changed = True
    return img.astype(bool)


def skeleton(mask):
    try:
        from skimage.morphology import skeletonize
        return skeletonize(mask)
    except Exception:
        return zhang_suen(mask)


def centreline_path(skel, dt, start_xy, min_dt=9.0, goal_dt=40.0):
    """Dijkstra over skeleton pixels (dt >= min_dt), RESTRICTED to the
    largest connected component of that core set (fragments -- bill,
    plume clumps -- would otherwise trap the search), cost = step
    length weighted toward high-DT pixels. Returns (path from start
    to the first goal_dt pixel popped, start node) or (None, None)."""
    from scipy import ndimage
    core = skel & (dt >= min_dt)
    lab, n = ndimage.label(core, np.ones((3, 3)))
    if n == 0:
        return None, None
    sizes = ndimage.sum(core, lab, range(1, n + 1))
    core = lab == (1 + int(np.argmax(sizes)))
    ys, xs = np.nonzero(core)
    nodes = set(zip(xs.tolist(), ys.tolist()))
    sx, sy = start_xy
    start = min(nodes, key=lambda p: (p[0] - sx) ** 2 + (p[1] - sy) ** 2)
    dist = {start: 0.0}
    prev = {}
    pq = [(0.0, start)]
    goal = None
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, 1e18):
            continue
        if dt[u[1], u[0]] >= goal_dt and u != start:
            goal = u
            break
        ux, uy = u
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                v = (ux + dx, uy + dy)
                if v not in nodes:
                    continue
                step = float(np.hypot(dx, dy))
                wgt = step * (1.0 + 6.0 * max(0.0, (16.0 - dt[v[1], v[0]])) / 16.0)
                nd = d + wgt
                if nd < dist.get(v, 1e18):
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(pq, (nd, v))
    if goal is None:
        return None, None
    path = [goal]
    while path[-1] != start:
        path.append(prev[path[-1]])
    path.reverse()
    return path, start


def arc_len(path):
    p = np.asarray(path, float)
    return float(np.hypot(*np.diff(p, axis=0).T).sum()) if len(p) > 1 else 0.0
