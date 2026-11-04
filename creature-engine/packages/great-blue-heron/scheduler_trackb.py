"""Track B scheduler — the heron as a state-driven animal, not a
playlist (deep-dive §3.5). Package code for great-blue-heron; consumes
behaviors_trackb.yaml. The engine core is not involved.

Model (all numbers live in behaviors_trackb.yaml):
  - Two-level structure: BOUTS with authored internal order, separated
    by heavy-tailed (lognormal) gaps filled with held poses.
  - Internal state gates what can happen next: hunger (time since
    catch), satiation, stand (creek/east), disturbance, refractory
    clocks, daily caps. The scheduler samples only from what the
    state allows.
  - Strikes are events inside hunt bouts: ~56% success [Documented],
    tide moves strike RATE only, never success; after a strike the
    bird relocates (~always) before stealth resumes [Documented].
  - Maintenance runs stretch -> body_shake -> preen with authored
    early stops; the alert ladder grades disturbance freeze -> alert
    -> flush.
  - Night is doze; the moon gate (brightest bucket only) is shut for
    the sim date, so there is no night hunt.

Output: a run-length TIMELINE of segments. A segment is either
  {kind: clip, clip: <name>, frames: [idx...], held: [bool...]}
or
  {kind: hold, clip: <name>, frame: <idx>, count: <frames>}
plus a parallel event log (strikes, relocations, bouts, ladder steps)
from which sim_day.py measures the day. Frames are 24 fps sim-frames;
holds are counted, not expanded.
"""
import math, os
import numpy as np
import yaml

FPS = 24.0
HERE = os.path.dirname(os.path.abspath(__file__))

# Clip table: name -> (folder, frame_count, held_ranges).
# Folders resolve in sim_day.py (roster frames vs sim assets).
# held_ranges are 0-based inclusive ranges counted as HELD (bird-region
# still) from the charts' own phase data — holds and no-channel events
# (blink has no conditioning channel in the bridge, so blink frames
# are pixel-still). Everything else counts as motion. Conservative:
# where a chart has sub-phase holds we did not enumerate, frames count
# as motion.
def _comp(n, motion_ranges):
    held, cur = [], 0
    for a, b in sorted(motion_ranges):
        if a > cur:
            held.append((cur, a - 1))
        cur = max(cur, b + 1)
    if cur < n:
        held.append((cur, n - 1))
    return held

CLIPS = {
    # idle_hunt: motion only at the two saccades and the head-roll lean
    'idle_hunt_at_stand': (480, _comp(480, [(140, 142), (236, 247),
                                            (314, 316)])),
    # doze: sink (36f) is motion; eye-close has no channel; hold still
    'doze_at_stand': (96, _comp(96, [(0, 35)])),
    'oneleg_at_stand': (36, []),
    'alert_at_stand': (61, [(7, 25), (29, 42)]),
    'stretch_at_stand': (168, [(54, 101)]),
    'preen_at_stand': (240, [(48, 63), (180, 239)]),
    'scratch_at_stand': (48, []),
    'head_saccade_at_stand': (3, []),
    'head_turn': (18, []),
    'body_shake': (152, [(140, 151)]),
    'strike': (52, []), 'swallow': (118, []), 'strike_miss': (64, []),
    'strike_at_R': (52, []), 'swallow_at_R': (118, []),
    'strike_miss_at_R': (64, []),
    'relocate': (120, []),
    'takeoff': (96, []), 'takeoff_at_R': (96, []),
    'flight_cycle': (12, []), 'glide': (24, []), 'landing': (120, []),
}
# A held statue frame at the east stand: strike_at_R's recover end
# (idle base pose at root 95) — the stealth stand between strikes.
EAST_HOLD = ('strike_at_R', 51)
CREEK_HOLD_FRAME = ('idle_hunt_at_stand', 0)


def _lognorm(rng, median, sigma, lo, hi):
    v = float(rng.lognormal(math.log(median), sigma))
    return min(max(v, lo), hi)


class World:
    def __init__(self, cfg):
        self.light = cfg['world']['light']
        self.tide_period = cfg['world']['tide']['period_h'] * 3600.0
        self.low0 = cfg['world']['tide']['low_water_h'][0] * 3600.0
        self.moon = cfg['world']['moon_bucket']

    def light_phase(self, t):
        h = t / 3600.0
        L = self.light
        if h < L['dawn']:
            return 'night'
        if h < L['day']:
            return 'dawn'
        if h < L['dusk']:
            return 'day'
        if h < L['night']:
            return 'dusk'
        return 'night'

    def tide_state(self, t):
        """(height in [-1,1], ebb_factor in [0,1]) — ebb peaks at low."""
        ph = 2 * math.pi * (t - self.low0) / self.tide_period
        height = -math.cos(ph)            # -1 at low, +1 at high
        ebb = max(0.0, math.sin(ph))      # falling toward low
        return height, ebb

    def tide_rate_mult(self, t, cfg):
        h, ebb = self.tide_state(t)
        lo_m = cfg['hunting']['tide_rate']['ebb_low_max']
        hi_m = cfg['hunting']['tide_rate']['flood_high_min']
        # ebbing + low -> lo_m ; flooding + high -> hi_m ; smooth blend
        w = 0.5 + 0.5 * ebb * (-h)        # 1 at mid-ebb-low approach
        w2 = 0.5 + 0.5 * (1 - ebb) * h    # 1 at high slack after flood
        return 1.0 + (lo_m - 1.0) * w * ebb + (hi_m - 1.0) * w2 * (1 - ebb)


class Timeline:
    def __init__(self):
        self.segments = []
        self.t = 0.0

    def clip(self, behavior, name, frames=None, label=''):
        n, held_ranges = CLIPS[name]
        idx = list(range(n)) if frames is None else list(frames)
        held = [any(a <= i <= b for a, b in held_ranges) for i in idx]
        self.segments.append(dict(kind='clip', behavior=behavior,
                                  clip=name, frames=idx, held=held,
                                  t0=self.t, label=label))
        self.t += len(idx) / FPS

    def hold(self, behavior, src, seconds, label=''):
        name, fi = src
        count = max(1, int(round(seconds * FPS)))
        self.segments.append(dict(kind='hold', behavior=behavior,
                                  clip=name, frame=fi, count=count,
                                  t0=self.t, label=label))
        self.t += count / FPS

    @property
    def total_frames(self):
        return sum(len(s['frames']) if s['kind'] == 'clip' else s['count']
                   for s in self.segments)

    @property
    def held_frames(self):
        h = 0
        for s in self.segments:
            if s['kind'] == 'clip':
                h += sum(s['held'])
            else:
                h += s['count']
        return h


class HeronDay:
    """One simulated day, 00:00-24:00, unwatched (the true bird)."""

    def __init__(self, cfg=None, seed=20261015, events=None):
        path = os.path.join(HERE, 'behaviors_trackb.yaml')
        self.cfg = cfg or yaml.safe_load(open(path))
        self.world = World(self.cfg)
        self.rng = np.random.default_rng(seed)
        self.tl = Timeline()
        self.events = []          # measured-event log for the report
        self.stand = 'creek'
        self.last_catch_t = -6 * 3600.0
        self.sat_big_until = -1.0
        self.sat_any_until = -1.0
        self.last_maint_t = -10 * 3600.0
        self.last_hunt_min = 0.0
        self.flights = 0
        self.strikes_since_relocate = 0
        # scripted disturbance inputs (the engine bus, exercised):
        # (time_s, kind) — brief / sustained / escalating
        self.script = sorted(events if events is not None else
                             [(7.08 * 3600, 'brief'),
                              (12.67 * 3600, 'sustained'),
                              (17.92 * 3600, 'escalating')])

    # ------------------------------------------------------------ util
    @property
    def t(self):
        return self.tl.t

    def log(self, kind, **kw):
        kw.update(kind=kind, t=round(self.t, 1))
        self.events.append(kw)

    def lognorm(self, spec):
        return _lognorm(self.rng, spec['median_min'] * 60,
                        spec['sigma'], spec['floor_min'] * 60,
                        spec['ceil_min'] * 60)

    def satiation_mult(self, t):
        m = 1.0
        if t < self.sat_big_until:
            m *= self.cfg['hunting']['satiation']['big_factor']
        elif t < self.sat_any_until:
            m *= self.cfg['hunting']['satiation']['any_factor']
        return m

    def stand_idle(self, behavior, seconds, label=''):
        """Held time in the current stand's own visual language."""
        if self.stand == 'creek':
            # idle_hunt cycles: play whole/partial cycles (their held
            # ranges ride along), topping up with a statue hold
            left = seconds
            while left > 0:
                cyc = CLIPS['idle_hunt_at_stand'][0] / FPS
                if left >= cyc:
                    self.tl.clip(behavior, 'idle_hunt_at_stand',
                                 label=label)
                    left -= cyc
                else:
                    self.tl.hold(behavior, CREEK_HOLD_FRAME, left,
                                 label=label)
                    left = 0
        else:
            self.tl.hold(behavior, EAST_HOLD, seconds, label=label)

    # -------------------------------------------------------- behaviors
    def strike_sequence(self):
        """One strike event inside a hunt bout, with its consequences."""
        H = self.cfg['hunting']
        atR = self.stand == 'east'
        sfx = '_at_R' if atR else ''
        hit = self.rng.random() < H['success_rate']
        big = bool(hit and self.rng.random() < H['big_share_of_hits'])
        self.tl.clip('hunt', f'strike{sfx}', label='strike')
        if hit:
            self.tl.clip('hunt', f'swallow{sfx}', label='swallow')
            if big:
                # drink beat: the swallow chart's own dip segment,
                # replayed as the post-catch drink (deep-dive §1.9)
                self.tl.clip('hunt', f'swallow{sfx}',
                             frames=list(range(12, 30)), label='drink')
                self.log('drink')
            self.last_catch_t = self.t
            now = self.t
            self.sat_big_until = now + H['satiation']['big_min'] * 60 \
                if big else self.sat_big_until
            self.sat_any_until = now + H['satiation']['any_min'] * 60
        else:
            self.tl.clip('hunt', f'strike_miss{sfx}', label='strike_miss')
        self.log('strike', hit=bool(hit), big=big, stand=self.stand)
        self.strikes_since_relocate += 1
        # relocation: ~always, mandatory after 2 without (§3.2)
        want = self.rng.random() < H['relocate_probability'] or \
            self.strikes_since_relocate >= H['relocate_mandatory_after']
        if want:
            if self.stand == 'creek':
                self.tl.clip('relocate', 'relocate', label='relocate_walk')
                self.stand = 'east'
                self.log('relocate', mode='walk', to='east')
            else:
                self.flight_move('relocate_flight')
                self.log('relocate', mode='flight', to='creek')
            self.strikes_since_relocate = 0
        else:
            self.stand_idle('hunt', float(self.rng.uniform(60, 180)),
                            label='settle')
            self.log('relocate', mode='none', to=self.stand)

    def flight_move(self, label):
        """takeoff (current stand) -> beats + glide -> landing (creek)."""
        src = 'takeoff_at_R' if self.stand == 'east' else 'takeoff'
        self.tl.clip('flight', src, label=label)
        for _ in range(int(self.rng.integers(2, 5))):
            self.tl.clip('flight', 'flight_cycle', label=label)
        self.tl.clip('flight', 'glide', label=label)
        self.tl.clip('flight', 'landing', label=label)
        self.stand = 'creek'
        self.flights += 1
        self.log('flight', label=label)
        # standalone shake after landing, Track B §1.5 probability
        p = self.cfg['maintenance']['shake_after_landing']['probability']
        if self.rng.random() < p:
            self.tl.clip('maintenance', 'body_shake',
                         label='shake_after_landing')
            self.log('shake_after_landing')

    def hunt_bout(self):
        H = self.cfg['hunting']
        dur = self.lognorm(H['bout_lognormal'])
        end = self.t + dur
        self.log('bout_start', behavior='hunt', dur_min=round(dur / 60, 1),
                 stand=self.stand)
        while self.t < end:
            if self.script and self.t >= self.script[0][0]:
                break           # a disturbance interrupts the hunt
            gap = self.lognorm(H['strike_gap_lognormal'])
            gap /= max(0.2, self.world.tide_rate_mult(self.t, self.cfg))
            gap /= max(0.2, self.satiation_mult(self.t))
            if self.t + gap >= end:
                self.stand_idle('hunt', end - self.t, label='stand')
                break
            self.stand_idle('hunt', gap, label='stand')
            if self.t >= end:
                break
            self.strike_sequence()
        self.last_hunt_min = dur / 60.0
        self.log('bout_end', behavior='hunt')

    def loaf_bout(self):
        dur = _lognorm(self.rng, 14 * 60, 0.5, 5 * 60, 40 * 60)
        end = self.t + dur
        self.log('bout_start', behavior='loaf', dur_min=round(dur / 60, 1),
                 stand=self.stand)
        L = self.cfg['loaf']
        if self.stand == 'creek' and \
                self.rng.random() < L['oneleg_probability']:
            self.tl.clip('loaf', 'oneleg_at_stand', label='oneleg_enter')
            self.tl.hold('loaf', ('oneleg_at_stand', 35),
                         max(0.0, end - self.t - 30), label='oneleg_hold')
            # exit is a hard cut in this proof (no exit chart rendered)
        if self.stand == 'creek' and self.t < end and \
                self.rng.random() < L['head_turn_probability']:
            self.tl.clip('loaf', 'head_turn', label='head_turn')
        if self.t < end:
            self.stand_idle('loaf', end - self.t, label='loaf_stand')
        self.log('bout_end', behavior='loaf')

    def maintenance_bout(self):
        M = self.cfg['maintenance']
        self.log('bout_start', behavior='maintenance', stand=self.stand)
        seq = []
        self.tl.clip('maintenance', 'stretch_at_stand', label='stretch')
        seq.append('stretch')
        if self.rng.random() >= M['early_stop']['after_stretch']:
            self.stand_idle('maintenance', float(self.rng.uniform(5, 20)))
            self.tl.clip('maintenance', 'body_shake', label='body_shake')
            seq.append('body_shake')
            if self.rng.random() >= M['early_stop']['after_shake']:
                self.stand_idle('maintenance',
                                float(self.rng.uniform(5, 20)))
                self.tl.clip('maintenance', 'preen_at_stand',
                             label='preen')
                seq.append('preen')
                if self.rng.random() < \
                        M['scratch_after_preen_probability']:
                    self.tl.clip('maintenance', 'scratch_at_stand',
                                 label='scratch')
                    seq.append('scratch')
        self.last_maint_t = self.t
        self.log('bout_end', behavior='maintenance', sequence=seq)

    def ladder(self, kind):
        """Alert ladder (deep-dive §1.7): freeze-check -> alert ->
        flush. Steps actually taken depend on the disturbance kind."""
        self.log('ladder', step='freeze_check', disturbance=kind,
                 stand=self.stand)
        if self.stand == 'creek':
            # freeze-check assembled from the alert chart's own snap:
            # check+snap (f0-7), a held accent (1-3 s), the settle
            hold_s = float(self.rng.uniform(
                *self.cfg['alert_ladder']['freeze_check_hold_s']))
            self.tl.clip('alert', 'alert_at_stand',
                         frames=list(range(0, 8)), label='freeze_check')
            self.tl.hold('alert', ('alert_at_stand', 7), hold_s,
                         label='freeze_check_hold')
            self.tl.clip('alert', 'alert_at_stand',
                         frames=list(range(43, 61)), label='freeze_settle')
            if kind in ('sustained', 'escalating'):
                self.log('ladder', step='alert', disturbance=kind)
                self.tl.clip('alert', 'alert_at_stand', label='alert')
            if kind == 'escalating':
                self.log('ladder', step='flush', disturbance=kind)
                self.flight_move('flush')
        else:
            # east stand: freeze = the loaded stand itself, held;
            # escalation caps at a long freeze + flush (no alert
            # chart is rendered for the east stand — disclosed).
            self.tl.hold('alert', EAST_HOLD,
                         float(self.rng.uniform(2, 4)), label='freeze_check')
            if kind == 'escalating':
                self.log('ladder', step='flush', disturbance=kind)
                self.flight_move('flush')

    # ------------------------------------------------------------- day
    def run(self):
        H = self.cfg['hunting']
        while self.t < 24 * 3600:
            phase = self.world.light_phase(self.t)
            # scripted disturbance takes precedence at its time
            if self.script and self.t >= self.script[0][0]:
                _, kind = self.script.pop(0)
                self.ladder(kind)
                continue
            if phase == 'night':
                if self.world.moon != 'm3':
                    if self.stand == 'east':
                        # herons fly to roost: a bird caught east at
                        # nightfall returns by air before dozing
                        self.flight_move('dusk_return')
                    # doze the night away; the doze chart once per
                    # block, then its held final pose; occasional
                    # eye-open check (head_saccade) inside long dozes
                    self.tl.clip('doze', 'doze_at_stand', label='doze')
                    nxt = min(24 * 3600.0,
                              self.t + _lognorm(self.rng, 38 * 60, 0.4,
                                                12 * 60, 70 * 60))
                    dawn = self.cfg['world']['light']['dawn'] * 3600 \
                        if self.t < 12 * 3600 else 24 * 3600.0
                    nxt = min(nxt, dawn if self.t < dawn else 24 * 3600.0)
                    while self.t < nxt:
                        step = min(nxt - self.t,
                                   _lognorm(self.rng, 16 * 60, 0.4,
                                            6 * 60, 30 * 60))
                        if self.script:
                            step = min(step, max(
                                0.0, self.script[0][0] - self.t))
                        if step <= 0:
                            break
                        self.tl.hold('doze', ('doze_at_stand', 95), step,
                                     label='doze_hold')
                        if self.t < nxt and self.stand == 'creek':
                            self.tl.clip('doze', 'head_saccade_at_stand',
                                         label='eye_open_check')
                    continue
            # waking decision point: sample from what state allows
            hours_since_catch = (self.t - self.last_catch_t) / 3600.0
            hunger = 0.7 + 0.6 * min(1.0, hours_since_catch / 6.0)
            _, ebb = self.world.tide_state(self.t)
            w = {}
            w['hunt'] = H['light_weight'][phase] * hunger * \
                (0.85 + 0.3 * ebb)
            if self.satiation_mult(self.t) < 1.0:
                w['hunt'] *= 0.7
            w['loaf'] = 0.5
            mw = self.cfg['maintenance']['base_weight']
            hh = self.t / 3600.0
            lo, hi = self.cfg['maintenance']['midday_window_h']
            if lo <= hh <= hi:
                mw *= self.cfg['maintenance']['midday_weight']
            if self.last_hunt_min > 40:
                mw *= self.cfg['maintenance']['after_long_hunt_boost']
            if self.t - self.last_maint_t < \
                    self.cfg['maintenance']['refractory_min'] * 60:
                mw = 0.0
            if self.stand != 'creek':
                mw = 0.0        # maintenance happens at the home stand
            w['maintenance'] = mw
            wf = 0.0
            if self.flights < self.cfg['flight']['max_per_day'] and \
                    phase in ('day', 'dusk'):
                wf = 0.06 * self.cfg['flight']['autumn_factor']
                if self.stand == 'east' and hh > 16.0:
                    wf = 0.5    # dusk return pressure
            w['flight'] = wf
            tot = sum(w.values())
            r = self.rng.random() * tot
            pick = None
            for k, v in w.items():
                r -= v
                if r <= 0:
                    pick = k
                    break
            pick = pick or 'loaf'
            if pick == 'hunt':
                self.hunt_bout()
            elif pick == 'maintenance':
                self.maintenance_bout()
            elif pick == 'flight':
                self.flight_move('reposition')
            else:
                self.loaf_bout()
            # inter-bout gap: heavy-tailed, held (deep-dive §3.2);
            # a scripted disturbance cuts the gap short at its time
            if self.world.light_phase(self.t) != 'night':
                gap = self.lognorm(self.cfg['scheduler']
                                   ['gap_lognormal'])
                if self.script:
                    gap = min(gap, max(0.0, self.script[0][0] - self.t))
                if gap > 0:
                    self.stand_idle('gap', gap, label='inter_bout_gap')
        return self.tl


def run_day(seed=20261015, events=None):
    day = HeronDay(seed=seed, events=events)
    tl = day.run()
    return day, tl


if __name__ == '__main__':
    day, tl = run_day()
    print(f'timeline: {len(tl.segments)} segments, '
          f'{tl.total_frames} frames, held {tl.held_frames} '
          f'({tl.held_frames / tl.total_frames:.3f})')
    for e in day.events:
        print(e)
