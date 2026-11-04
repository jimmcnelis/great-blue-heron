"""Creature Engine — a species-agnostic pipeline for generated cartoon creatures.

Packages (data + a thin rig/clip module) plug into this engine:
  species package     -> packages/<id>/species.yaml (+ rig.py, clips.py, behaviors.yaml)
  environment package -> packages/<id>/environment.yaml   (or scene-local env file)
  style pack          -> packages/<id>/style.yaml
  scene               -> packages/<id>/scene.yaml (composition: characters, inputs, interactions)

Engine stages:
  package.py  load + validate packages against schemas/, resolve cross-references
  anim.py     keyframe animation engine (generalized from heron v1 clips.Anim)
  rigcore.py  design-space drawing primitives + layered renderer support
  corpus.py   corpus builder: roster (data) -> poses -> rig frames + events
  behavior.py declarative behavior policy (pacing per external mode) + reactions
  effects.py  procedural caused-mark runtime (the heron ink system, generalized)
  episode.py  episode player: corpus trajectories + effects compositing -> frames
  qa.py       pluggable QA validators (core set + style-pack-selected checks)
"""
