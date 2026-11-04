"""Behavior policy — the v1 report's prose pacing table, as executable data.

Each behavior carries a mean interval PER EXTERNAL MODE (pacing). The policy
is a set of competing Poisson processes: rate_i = weight_i / pacing_i(mode).
Sampling a schedule shows what a mode actually does to a creature's day —
this is how the heron's 'unwatched vs watched' columns stop being prose.

Reactions (bus events -> interrupt + play + boosts) are looked up separately;
the firmware/simulator runtime consults them before the policy.
"""
import numpy as np


class Policy:
    def __init__(self, behaviors_doc):
        self.doc = behaviors_doc
        self.behaviors = behaviors_doc.get('behaviors', [])
        self.reactions = {r['trigger']: r for r in behaviors_doc.get('reactions', [])}

    def _rate(self, b, mode):
        pacing = b.get('pacing', {})
        secs = pacing.get(mode, pacing.get('default'))
        if not secs:
            return 0.0      # no pacing in this mode = filler/baseline behavior
        return b.get('weight', 1.0) / secs

    def schedule(self, duration_s, mode, rng=None, start_at=0.0):
        """Sample [(t, behavior_id), ...] of triggered (non-baseline) behaviors."""
        rng = rng or np.random.default_rng(0)
        out = []
        clocks = {}
        for b in self.behaviors:
            r = self._rate(b, mode)
            if r > 0:
                clocks[b['id']] = start_at + rng.exponential(1.0 / r)
        cooldown_until = {}
        while clocks:
            bid = min(clocks, key=clocks.get)
            t = clocks[bid]
            if t > duration_s:
                break
            out.append((round(t, 1), bid))
            b = next(x for x in self.behaviors if x['id'] == bid)
            r = self._rate(b, mode)
            clocks[bid] = t + rng.exponential(1.0 / r)
            cd = b.get('cooldown_s', 0)
            if cd:
                clocks[bid] = max(clocks[bid], t + cd)
        return sorted(out)

    def react(self, event_name):
        return self.reactions.get(event_name)
