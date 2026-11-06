/*
 * heron_line.h — the LINE HERON: a great blue heron drawn as ONE
 * continuous black line on plate paper, animated by the measured rig.
 *
 * Jimmy's spec (2026-11-04 21:20-21:21): regenerated from scratch,
 * black line only, scant detail — "almost just an outline of the bird",
 * "a single line to draw the bird, more or less". Working loop first.
 *
 * This module is the single source of truth for pose, outline and
 * schedule math. The firmware (main.c) and the host proof renderer
 * (host/host_main.c) link the SAME code, so what is verified on the
 * host is what runs on the board.
 *
 * Geometry: the outline is one polyline. It starts at the tail tip,
 * runs along the back, up the back of the neck, over the head and the
 * bill, back down the throat, along the belly, dives down each leg
 * (and back up the same path) as excursions, and closes along the
 * undertail. Poses are keyframed parameter sets; neck shapes are
 * 5-point control polygons (root + 4) riding a resampled chain, so
 * the neck UNFOLDS between shapes instead of stretching arbitrarily.
 * Legs are two-bone IK from authored foot positions (ankle at ~49%
 * of leg length, per the leg canon). Home stance is anchored to the
 * approved alert plate: feet midpoint (325,546), hip origin (328,335).
 */
#pragma once

#include <stdint.h>
#include <stdbool.h>

#define HL_W 1024
#define HL_H 600

/* RGB565: plate paper (247,232,210) and pure black ink. */
#define HL_PAPER 0xF75Au
#define HL_INK   0x0000u

/* Behavior ids */
enum {
    HL_IDLE = 0,
    HL_PREEN,
    HL_STRIDE,
    HL_STRIKE,
    HL_MISS,
    HL_STRETCH,
    HL_FLIGHT,
    HL_COURTSHIP,
    HL_NBEHAV
};

const char *hl_behavior_name(int id);
float hl_behavior_duration(int id);   /* seconds; HL_IDLE returns 0 (open-ended) */

/* ---- pose parameters (one interpolated state of the bird) -------- */
typedef struct {
    float hx, hy;          /* hip-origin offset from home, px (world) */
    float pitch;           /* body pitch about the hip origin, rad (+ = breast down) */
    float facing;          /* +1 faces right, -1 faces left (flight turns) */
    float neck[5][2];      /* neck control points rel neck root, body frame */
    float head_pitch;      /* extra head rotation, rad (+ = bill down) */
    float neck_w;          /* neck width scale (slimming at extension) */
    float wing;            /* standing wing excursion 0..1 (stretch) */
    float wing_amp;        /* flight wingbeat amplitude 0..1 */
    float wing_phase;      /* flight wingbeat phase, rad */
    float footF[2];        /* front foot position */
    float footR[2];        /* rear foot position */
    int   feet_body;       /* 1: feet are body-frame offsets (airborne) */
    float rise;            /* courtship rise: extra leg straighten, px up */
    float scale;           /* whole-bird scale about the hip (flight) */
} hl_params;

/* Evaluate a behavior's pose at time t (seconds into the behavior).
 * t_abs is the scene's absolute clock (idle breathing phase). */
void hl_pose_at(int behavior, float t, float t_abs, hl_params *out);

/* ---- scene: scheduler + ripples + rendering ---------------------- */
#define HL_MAX_RIPPLES 24

typedef struct {
    float x, y, t0;
    float scale;           /* ring size multiplier (steps < strikes) */
} hl_ripple;

typedef struct {
    uint16_t *fb;          /* HL_W*HL_H RGB565 framebuffer (caller's) */
    uint32_t rng;          /* xorshift32 state */
    float t_abs;           /* absolute clock, s */
    int state;             /* HL_IDLE or a behavior id */
    float state_t;         /* time inside current state, s */
    float state_dur;       /* scheduled duration of current state, s */
    int bag[14];
    int bag_n;             /* tickets left in bag */
    int last_played;       /* last behavior drawn (-1 none) */
    int proof_speed;       /* nonzero: idle holds compressed for bench demo */
    hl_ripple ripples[HL_MAX_RIPPLES];
    int ripples_n;
    float ripple_clock;    /* last time ripple spawns were checked */
    int ripple_stage;      /* per-state spawn bookkeeping */
} hl_scene;

void hl_scene_init(hl_scene *s, uint16_t *fb, uint32_t seed, int proof_speed);
/* Force the scene into a behavior (host proofs; also used internally). */
void hl_scene_force(hl_scene *s, int behavior);
/* Advance the scene by dt seconds and render one frame into s->fb. */
void hl_scene_step(hl_scene *s, float dt);
/* Render a single pose (no scheduler) — host stills/tests. */
void hl_render_pose(uint16_t *fb, const hl_params *p, const hl_ripple *rip, int nrip, float t_abs);
