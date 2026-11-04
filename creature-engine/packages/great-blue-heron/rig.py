"""Great Blue Heron rig — ADAPTER over the v1 rig (wrapping, not rewriting).

The v1 rig (~/workspace/heron/src/rig.py) is bound to its compiled-in master
grid (160x120) and its own design mapping; this adapter exposes the engine
contract render(pose, ctx) -> (grid, anchors) and asserts the scene grid
matches what the v1 rig produces. Re-expressing the heron's shapes on
engine/rigcore primitives is refactor Phase 2 (see ../../ARCHITECTURE.md).
"""
import sys

sys.path.insert(0, '/home/hatch/workspace/heron/src')
import rig as _v1  # noqa: E402


def default_pose():
    return _v1.default_pose()


def render(pose, ctx):
    assert (ctx['grid_w'], ctx['grid_h']) == (_v1.W, _v1.H), (
        f"v1 heron rig is bound to {_v1.W}x{_v1.H}; scene asks "
        f"{ctx['grid_w']}x{ctx['grid_h']} — re-render via the v1 pipeline or "
        "wait for the rigcore re-expression (refactor Phase 2).")
    grid, info = _v1.render(pose)
    return grid, info     # info already carries beak_tip + head in grid coords
