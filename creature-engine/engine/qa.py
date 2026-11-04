"""QA harness — pluggable validators.

Style packs SELECT checks by id and set thresholds; the engine owns the
measuring code (the cartoon-craft skill's 'Measure the craft' section,
operationalized). A check that lacks its input data reports 'not_evaluable'
rather than passing silently.
"""
import numpy as np


def _band(g, row, half):
    return g[max(0, row - half):row + half + 1, :]


def palette_exactness(grids, palette_size, **kw):
    vals = sorted(np.unique(grids).tolist())
    return dict(passed=all(0 <= v < palette_size for v in vals),
                measured=dict(grid_values=vals, palette_size=palette_size))


def join_smoothness(grids, segments, **kw):
    if len(grids) < 2:
        return dict(passed=False, measured={}, note='too few frames')
    changes = np.array([int((grids[i] != grids[i - 1]).sum()) for i in range(1, len(grids))])
    joins = [s['start'] for s in segments[1:] if s['start'] > 0]
    max_join = int(max((changes[j - 1] for j in joins), default=0))
    med = float(np.median(changes))
    limit = kw.get('max_join_over_median', 8.0)
    return dict(passed=bool(max_join <= limit * max(med, 1.0)),
                measured=dict(median_frame_change=med, max_join_change=max_join,
                              limit_ratio=limit))


def ink_at_rest(grids, segments, ink_index, surface_row, quiet_presence=None, **kw):
    """Ink discipline: during trailing seconds of quiet segments, effect-band
    ink must be (near) zero — stillness is the default."""
    half = kw.get('band_half', 6)
    tail = kw.get('tail_frames', 24)
    filt = kw.get('segment_filter', [])
    worst = 0
    checked = []
    for s in segments:
        if filt and not any(s['clip'].startswith(n) for n in filt):
            continue
        end = s['start'] + s['count']
        lo = max(s['start'], end - tail)
        if end - lo < 6:
            continue
        m = max(int((_band(grids[i], surface_row, half) == ink_index).sum())
                for i in range(lo, end))
        worst = max(worst, m)
        checked.append(s['clip'])
    return dict(passed=bool(worst <= kw.get('max_ink_cells', 0)),
                measured=dict(worst_ink_cells=worst, segments_checked=checked))


def event_causality(grids, events, effect_map, ink_index, surface_row, **kw):
    """Every event type the environment maps to an effect must actually
    produce marks near its frame (the v1 '12/12 step events inked' check)."""
    half = kw.get('band_half', 6)
    window = kw.get('window_frames', 5)
    mapped = [e for e in events if e.get('type') in effect_map]
    hits = 0
    for e in mapped:
        f = e['f']
        # marks live near the EVENT: at its own y when it carries one (a tongue
        # snap happens in the air), else at the surface band (v1's assumption)
        row = int(e['y']) if e.get('y') is not None else surface_row
        ok = any(int((_band(grids[j], row, half) == ink_index).sum()) > 0
                 for j in range(f, min(len(grids), f + window)))
        hits += int(ok)
    return dict(passed=bool(mapped and hits == len(mapped)),
                measured=dict(mapped_events=len(mapped), events_with_marks=hits))


def held_fraction(grids, segments, **kw):
    """Fraction of frames in the named segments whose subject (non-bg cells)
    barely changes — the cartoon skill's held-pose audit (>=60% in idles)."""
    thresh = kw.get('cell_change_threshold', 8)
    names = kw.get('segment_filter', [])
    sel = [s for s in segments if not names or s['clip'] in names
           or any(s['clip'].startswith(n) for n in names)]
    held = tot = 0
    for s in sel:
        for i in range(s['start'] + 1, s['start'] + s['count']):
            if i >= len(grids):
                break
            tot += 1
            held += int(int((grids[i] != grids[i - 1]).sum()) <= thresh)
    frac = held / max(tot, 1)
    return dict(passed=bool(frac >= kw.get('min_fraction', 0.6)),
                measured=dict(held_fraction=round(frac, 3), frames=tot))


def flicker_metric(grids, segments, **kw):
    """A-B-A single-frame color flips per 1000 cell-frames in held segments —
    decode flicker, the defect the skill separates from authored boil."""
    names = kw.get('segment_filter', [])
    sel = [s for s in segments if not names or s['clip'] in names
           or any(s['clip'].startswith(n) for n in names)]
    flips = cells = 0
    for s in sel:
        a, b = s['start'], min(len(grids), s['start'] + s['count'])
        for i in range(a + 1, b - 1):
            flips += int(((grids[i - 1] == grids[i + 1]) & (grids[i] != grids[i - 1])).sum())
            cells += grids[i].size
    per1000 = 1000.0 * flips / max(cells, 1)
    return dict(passed=bool(per1000 <= kw.get('max_per_1000', 40.0)),
                measured=dict(aba_flips_per_1000_cell_frames=round(per1000, 2),
                              total_flips=flips))


VALIDATORS = {
    'palette_exactness': palette_exactness,
    'join_smoothness': join_smoothness,
    'ink_at_rest': ink_at_rest,
    'event_causality': event_causality,
    'held_fraction': held_fraction,
    'flicker_metric': flicker_metric,
}


def run_checks(check_defs, **data):
    results = []
    for chk in check_defs:
        fn = VALIDATORS.get(chk['id'])
        if fn is None:
            results.append(dict(id=chk['id'], status='not_implemented',
                                note='validator not registered in this engine build'))
            continue
        try:
            r = fn(**data, **chk.get('params', {}))
            results.append(dict(id=chk['id'],
                                status='pass' if r['passed'] else 'fail',
                                severity=chk.get('severity', 'gate'), **r))
        except TypeError as e:
            results.append(dict(id=chk['id'], status='not_evaluable', note=str(e)))
    return results
