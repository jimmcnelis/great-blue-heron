# Driver: run shared build_sample.py with an in-memory patch to
# maskrender.xform_points so scalar keys (_px_per_unit etc.) pass through
# instead of crashing. Shared files on disk are NOT modified.
import sys, os
sys.path.insert(0, os.path.expanduser('~/workspace/heron/art2'))
import maskrender as M
_orig = M.xform_points
def patched(kp, fn):
    geo = {k: v for k, v in kp.items() if not k.startswith('_')}
    return _orig(geo, fn)
M.xform_points = patched
sys.argv = ['build_sample.py'] + sys.argv[1:]
import runpy
runpy.run_path(os.path.expanduser('~/workspace/heron/art2/build_sample.py'), run_name='__main__')
