"""Package loading + validation.

Layout convention: a package directory holds YAML documents named by kind
(species.yaml / environment.yaml / style.yaml / scene.yaml / behaviors.yaml)
plus the Python modules those documents reference. Scenes reference species
and environment packages BY ID; ids resolve to directories under the
packages root.
"""
import importlib.util
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ENGINE_DIR = Path(__file__).resolve().parent
SCHEMA_DIR = ENGINE_DIR.parent / 'schemas'


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def validate(doc, schema_name):
    schema = json.loads((SCHEMA_DIR / schema_name).read_text())
    errors = sorted(Draft202012Validator(schema).iter_errors(doc),
                    key=lambda e: list(e.path))
    if errors:
        msgs = [f"{'.'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]
        raise ValueError(f"{schema_name} validation failed:\n  - " + "\n  - ".join(msgs))
    return doc


def import_module(pkg_dir, module_name, qualname):
    path = Path(pkg_dir) / module_name
    spec = importlib.util.spec_from_file_location(qualname, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[qualname] = mod
    spec.loader.exec_module(mod)
    return mod


class Species:
    def __init__(self, pkg_dir):
        self.dir = Path(pkg_dir)
        self.data = validate(load_yaml(self.dir / 'species.yaml'), 'species.schema.json')
        self.id = self.data['id']
        pal = self.data['palette']
        self.palette_names = list(pal.keys())          # insertion order = local indices
        self.palette_rgb = [tuple(pal[n]['rgb']) for n in self.palette_names]
        self.index = {n: i for i, n in enumerate(self.palette_names)}
        self.defaults = {k: v['default'] for k, v in self.data['pose_params'].items()}
        self.life_layer = self.data.get('life_layer', [])
        rig = self.data['rig']
        self.rig_module = import_module(self.dir, rig['module'], f"pkg_{self.id}_rig")
        self.render_fn = getattr(self.rig_module, rig['render_fn'])
        self.default_pose_fn = getattr(self.rig_module, rig['default_pose_fn'])
        clips = self.data['clips']
        self.clips_module = import_module(self.dir, clips['module'], f"pkg_{self.id}_clips")
        self.roster = clips['roster']
        self.behaviors = None
        bf = self.data.get('behaviors_file', 'behaviors.yaml')
        if (self.dir / bf).exists():
            self.behaviors = validate(load_yaml(self.dir / bf), 'behaviors.schema.json')

    @property
    def design_space(self):
        ds = self.data['design_space']
        return (float(ds['width']), float(ds['height']))

    def default_pose(self):
        return self.default_pose_fn()


class SceneObject:
    """A placed OBJECT instance: an object package + placement + state.

    Objects are the non-living cast (landmarks, structures, vegetation,
    vessels). The package's rig renders deterministically from state —
    render(state, ctx) -> (grid, anchors), the species rig contract with
    state in place of pose. Objects have no corpus, no behaviors, no life
    layer, and nothing learned: state comes from the scene placement, the
    input bus/modes, or an interaction outcome's set_state.
    """

    def __init__(self, pkg_dir, placement, zones):
        self.dir = Path(pkg_dir)
        self.data = validate(load_yaml(self.dir / 'object.yaml'), 'object.schema.json')
        self.id = self.data['id']
        pal = self.data['palette']
        self.palette_names = list(pal.keys())
        self.palette_rgb = [tuple(pal[n]['rgb']) for n in self.palette_names]
        self.index = {n: i for i, n in enumerate(self.palette_names)}
        rig = self.data['rig']
        self.rig_module = import_module(self.dir, rig['module'], f"pkg_{self.id}_objrig")
        self.render_fn = getattr(self.rig_module, rig.get('render_fn', 'render'))
        fn = rig.get('default_state_fn', 'default_state')
        self.default_state_fn = getattr(self.rig_module, fn)
        # placement: zone wins for x (and y when the zone declares one);
        # explicit x/y in the scene entry override either.
        self.instance_id = placement['id']
        self.layer = placement.get('layer', 'back')
        self._anchor_cache = None
        x, y = placement.get('x'), placement.get('y')
        zone = placement.get('zone')
        if zone is not None:
            z = zones[zone]
            if x is None:
                x = z['x']
            if y is None:
                y = z.get('y', 0.0)
        self.state = self.default_state_fn()
        self.state.update({k: v['default'] for k, v in
                           self.data.get('state_params', {}).items()})
        self.state.update({'root_x': float(x or 0.0), 'root_y': float(y or 0.0),
                           'scale': float(placement.get('scale', 1.0))})
        self.state.update(placement.get('state', {}))

    @property
    def design_space(self):
        ds = self.data['design_space']
        return (float(ds['width']), float(ds['height']))

    def ctx(self, scene):
        return {
            'design_w': scene.design_w, 'design_h': scene.design_h,
            'grid_w': scene.grid_w, 'grid_h': scene.grid_h,
            'fps': scene.fps, 'palette_index': self.index,
            'palette_size': len(self.palette_names),
            'zones': scene.environment.zones,
            'style': scene.style,
            # the world's clip planes bind objects as they bind creatures
            # (in implied-water, lighthouse piles below the surface plane
            # stay hidden under the blank, exactly like the heron's feet)
            'clip_planes': [p for p in
                            scene.environment.canvas_law.get('clip_planes', [])
                            if p.get('applies_to', 'all') in ('all', 'grounded')],
        }

    def render(self, scene):
        grid, anchors = self.render_fn(dict(self.state), self.ctx(scene))
        return grid, anchors


class Environment:
    def __init__(self, pkg_dir):
        self.dir = Path(pkg_dir)
        self.data = validate(load_yaml(self.dir / 'environment.yaml'),
                             'environment.schema.json')
        self.id = self.data['id']
        self.zones = self.data.get('zones', {})
        self.effect_map = self.data.get('effect_map', {})
        self.canvas_law = self.data['canvas_law']

    def mirror_zone(self, name):
        z = self.zones.get(name, {})
        return z.get('mirror_of', name)


class Style:
    def __init__(self, pkg_dir):
        self.dir = Path(pkg_dir)
        self.data = validate(load_yaml(self.dir / 'style.yaml'), 'style.schema.json')
        self.id = self.data['id']
        self.qa_checks = self.data.get('qa_checks', [])
        rules = self.data.get('render_rules', {})
        self.supersample = int(rules.get('supersample', 4))


class Scene:
    """A composition: environment + style + characters (+ interactions).

    The scene owns the stage: grid, fps, and design space. Every character's
    species must declare the same design space (validator rule) — a species
    authored for a different stage size is a different package variant.
    """

    def __init__(self, scene_dir, packages_root):
        self.dir = Path(scene_dir)
        self.data = validate(load_yaml(self.dir / 'scene.yaml'), 'scene.schema.json')
        self.id = self.data['id']
        root = Path(packages_root)
        self.environment = Environment(root / self.data['environment'])
        self.style = Style(root / self.data['style'])
        self.characters = {}      # instance id -> Species
        self.char_order = []
        for ch in self.data['characters']:
            sp = Species(root / ch['species'])
            self.characters[ch['id']] = sp
            self.char_order.append(ch['id'])
        # design-space agreement
        spaces = {sp.design_space for sp in self.characters.values()}
        if len(spaces) != 1:
            raise ValueError(f"scene {self.id}: characters disagree on design space: {spaces}")
        self.design_w, self.design_h = spaces.pop()
        # objects: placed instances of object packages (the non-living cast)
        self.objects = {}         # instance id -> SceneObject
        self.object_order = []    # placement order = composite order within a layer
        for ob in self.data.get('objects', []):
            so = SceneObject(root / ob['package'], ob, self.environment.zones)
            if so.design_space != (self.design_w, self.design_h):
                raise ValueError(
                    f"scene {self.id}: object {so.id} design space {so.design_space} "
                    f"!= scene {(self.design_w, self.design_h)}")
            if so.palette_names[0] != self.characters[self.char_order[0]].palette_names[0]:
                raise ValueError(
                    f"scene {self.id}: object {so.id} palette index 0 "
                    f"'{so.palette_names[0]}' is not the scene background entry")
            self.objects[so.instance_id] = so
            self.object_order.append(so.instance_id)
        # environment color names must resolve in the union of palettes
        names = set()
        for sp in self.characters.values():
            names |= set(sp.palette_names)
        for so in self.objects.values():
            names |= set(so.palette_names)
        for mark in self.environment.canvas_law.get('static_marks', []):
            if mark['color'] not in names:
                raise ValueError(f"env static mark color '{mark['color']}' not in any palette")
        self.grid_w = int(self.data['grid']['width'])
        self.grid_h = int(self.data['grid']['height'])
        self.fps = float(self.data.get('fps', 12))

    def palette_rgb(self, char_id):
        import numpy as np
        return np.array(self.characters[char_id].palette_rgb, dtype=np.uint8)

    def object_anchor(self, instance_id, anchor_name):
        """Grid-coords anchor of a placed object (rendered on demand).
        Behaviors/interactions resolve affordances to this — e.g. a heron
        'perch' behavior targeting the lighthouse's gallery anchor."""
        so = self.objects[instance_id]
        if so._anchor_cache is None:
            _, so._anchor_cache = so.render(self)
        return so._anchor_cache[anchor_name]

    def object_affordance(self, instance_id, action):
        """The anchor name an object's package declares for an action
        (perch / look_at / shelter …), or None if it doesn't offer it."""
        so = self.objects[instance_id]
        for aff in so.data.get('affordances', []):
            if aff['action'] == action:
                return aff['anchor']
        return None

    def ctx(self, char_id):
        """Render context handed to a species rig/clip module."""
        sp = self.characters[char_id]
        return {
            'design_w': self.design_w, 'design_h': self.design_h,
            'grid_w': self.grid_w, 'grid_h': self.grid_h,
            'fps': self.fps, 'palette_index': sp.index,
            'palette_size': len(sp.palette_names),
            'zones': self.environment.zones,
            'style': self.style,
            'life_layer': sp.life_layer,
            'clip_planes': self.environment.canvas_law.get('clip_planes', []),
        }
