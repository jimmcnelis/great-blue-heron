/*
 * heron_line.c — pose, outline, schedule and rasterizer for the LINE
 * HERON. See heron_line.h for the design. Plain C, no allocation, no
 * platform calls: identical code runs in the firmware and the host
 * proof renderer.
 */
#include "heron_line.h"

#include <math.h>
#include <string.h>

/* ------------------------------------------------------------------ */
/* Fixed geometry (pixels; canvas 1024x600, y down, bird faces +x).    */
/* Body frame origin = hip centre. Home: hip origin at (328,335),      */
/* feet planted at (343,546) front / (307,546) rear — measured from    */
/* the approved alert plate.                                           */
/* ------------------------------------------------------------------ */
#define HIP_HOME_X 328.0f
#define HIP_HOME_Y 335.0f
#define FOOT_F_HOME_X 343.0f
#define FOOT_R_HOME_X 307.0f
#define FOOT_Y 546.0f

/* Body outline control points, body frame (tail -> back -> shoulder,
 * breast, belly segments split where the legs dive). */
static const float BODY_BACK[][2] = {
    {-283, 25}, {-246, -72}, {-194, -146}, {-103, -179},
    {2, -187}, {102, -182}, {187, -170}, {254, -152},
};
static const float BODY_BELLY_A[][2] = {   /* breast -> front hip */
    {327, -45}, {240, -9}, {122, 3}, {44, 6},
};
static const float BODY_BELLY_B[][2] = {   /* between the legs */
    {-2, 7},
};
static const float BODY_BELLY_C[][2] = {   /* rear hip -> undertail */
    {-118, 4}, {-222, 12}, {-260, 20}, {-276, 27},
};
#define HIP_F_X 17.0f
#define HIP_F_Y (-2.0f)
#define HIP_R_X (-18.0f)
#define HIP_R_Y (-2.0f)
#define NECK_ROOT_X 290.0f
#define NECK_ROOT_Y (-127.0f)

/* Neck shapes are 5 control points rel neck root (root first),
 * authored inline in the keyframe tables below: ALERT (S at rest),
 * COIL (deep S, pre-strike), AIM, STRIKE (unfolded spear), MISS,
 * PREEN (head to back), SKY (courtship), FLIGHT (tight S), STRETCH. */

/* ------------------------------------------------------------------ */
/* Keyframed behaviors                                                 */
/* ------------------------------------------------------------------ */
typedef struct { float t; hl_params p; } hl_key;

#define BASE_PARAMS { 0,0, 0, 1, {{0,0},{40,30},{58,-38},{84,-92},{144,-128}}, \
                      0.08f, 1, 0, 0,0, {FOOT_F_HOME_X, FOOT_Y}, {FOOT_R_HOME_X, FOOT_Y}, 0, 0, 1 }
#define P(...) (hl_params)BASE_PARAMS

/* PREEN — head goes to the back, nibbles, returns. 10 s. */
static const hl_key KEYS_PREEN[] = {
    { 0.0f, BASE_PARAMS },
    { 1.4f, BASE_PARAMS },
    { 2.6f, { 0,0, 0.02f, 1, {{0,0},{14,26},{-26,-10},{-64,-22},{-92,-14}}, 0.95f, 1, 0, 0,0, {FOOT_F_HOME_X, FOOT_Y}, {FOOT_R_HOME_X, FOOT_Y}, 0, 0 } },
    { 6.8f, { 0,0, 0.02f, 1, {{0,0},{14,26},{-26,-10},{-64,-22},{-92,-14}}, 0.95f, 1, 0, 0,0, {FOOT_F_HOME_X, FOOT_Y}, {FOOT_R_HOME_X, FOOT_Y}, 0, 0 } },
    { 8.2f, BASE_PARAMS },
    { 10.0f, BASE_PARAMS },
};
/* STRIKE — coil, aim, 0.18 s unfold to the water, withdraw. 9 s. */
static const hl_key KEYS_STRIKE[] = {
    { 0.0f, BASE_PARAMS },
    { 1.6f, BASE_PARAMS },
    { 2.4f, { 4,6, 0.06f, 1, {{0,0},{38,52},{12,2},{-2,-58},{58,-98}}, 0.1f, 1, 0, 0,0, {FOOT_F_HOME_X, FOOT_Y}, {FOOT_R_HOME_X, FOOT_Y}, 0, 0 } },
    { 3.1f, { 8,10, 0.10f, 1, {{0,0},{48,48},{88,52},{118,58},{150,66}}, 0.2f, 0.95f, 0, 0,0, {FOOT_F_HOME_X, FOOT_Y}, {FOOT_R_HOME_X, FOOT_Y}, 0, 0 } },
    { 3.5f, { 8,10, 0.10f, 1, {{0,0},{48,48},{88,52},{118,58},{150,66}}, 0.2f, 0.95f, 0, 0,0, {FOOT_F_HOME_X, FOOT_Y}, {FOOT_R_HOME_X, FOOT_Y}, 0, 0 } },
    { 3.68f, { 14,20, 0.28f, 1, {{0,0},{45,50},{80,88},{105,108},{127,122}}, 0.15f, 0.8f, 0, 0,0, {FOOT_F_HOME_X, FOOT_Y}, {FOOT_R_HOME_X, FOOT_Y}, 0, 0 } },
    { 4.3f, { 14,20, 0.28f, 1, {{0,0},{45,50},{80,88},{105,108},{127,122}}, 0.15f, 0.8f, 0, 0,0, {FOOT_F_HOME_X, FOOT_Y}, {FOOT_R_HOME_X, FOOT_Y}, 0, 0 } },
    { 5.3f, { 4,6, 0.06f, 1, {{0,0},{38,52},{12,2},{-2,-58},{58,-98}}, 0.1f, 1, 0, 0,0, {FOOT_F_HOME_X, FOOT_Y}, {FOOT_R_HOME_X, FOOT_Y}, 0, 0 } },
    { 6.4f, BASE_PARAMS },
    { 9.0f, BASE_PARAMS },
};
/* MISS — a strike at the wrong spot, head-shake, slow scan back. 10 s. */
static const hl_key KEYS_MISS[] = {
    { 0.0f, BASE_PARAMS },
    { 1.6f, BASE_PARAMS },
    { 2.4f, { 4,6, 0.06f, 1, {{0,0},{38,52},{12,2},{-2,-58},{58,-98}}, 0.1f, 1, 0, 0,0, {FOOT_F_HOME_X, FOOT_Y}, {FOOT_R_HOME_X, FOOT_Y}, 0, 0 } },
    { 3.1f, { 6,8, 0.08f, 1, {{0,0},{48,48},{88,52},{118,58},{150,66}}, 0.2f, 0.95f, 0, 0,0, {FOOT_F_HOME_X, FOOT_Y}, {FOOT_R_HOME_X, FOOT_Y}, 0, 0 } },
    { 3.5f, { 6,8, 0.08f, 1, {{0,0},{48,48},{88,52},{118,58},{150,66}}, 0.2f, 0.95f, 0, 0,0, {FOOT_F_HOME_X, FOOT_Y}, {FOOT_R_HOME_X, FOOT_Y}, 0, 0 } },
    { 3.85f, { 8,16, 0.22f, 1, {{0,0},{38,42},{66,72},{86,90},{102,100}}, 0.3f, 0.85f, 0, 0,0, {FOOT_F_HOME_X, FOOT_Y}, {FOOT_R_HOME_X, FOOT_Y}, 0, 0 } },
    { 5.0f, { 8,16, 0.22f, 1, {{0,0},{38,42},{66,72},{86,90},{102,100}}, 0.3f, 0.85f, 0, 0,0, {FOOT_F_HOME_X, FOOT_Y}, {FOOT_R_HOME_X, FOOT_Y}, 0, 0 } },
    { 7.0f, { 4,6, 0.06f, 1, {{0,0},{38,52},{12,2},{-2,-58},{58,-98}}, 0.1f, 1, 0, 0,0, {FOOT_F_HOME_X, FOOT_Y}, {FOOT_R_HOME_X, FOOT_Y}, 0, 0 } },
    { 8.2f, BASE_PARAMS },
    { 10.0f, BASE_PARAMS },
};
/* STRETCH — wing + same-side leg sweep back, neck long. 9 s. */
static const hl_key KEYS_STRETCH[] = {
    { 0.0f, BASE_PARAMS },
    { 1.2f, BASE_PARAMS },
    { 3.2f, { 0,-4, -0.03f, 1, {{0,0},{62,-6},{128,-10},{196,-12},{262,-10}}, 0, 1, 1.0f, 0,0, {FOOT_F_HOME_X, FOOT_Y}, {185.0f, FOOT_Y}, 0, 0 } },
    { 5.6f, { 0,-4, -0.03f, 1, {{0,0},{62,-6},{128,-10},{196,-12},{262,-10}}, 0, 1, 1.0f, 0,0, {FOOT_F_HOME_X, FOOT_Y}, {185.0f, FOOT_Y}, 0, 0 } },
    { 7.4f, BASE_PARAMS },
    { 9.0f, BASE_PARAMS },
};
/* STRIDE — stalk right with a freeze, cautious retreat home. 11 s.
 * Feet are authored in world coords; the renderer adds step lift. */
#define SKEY(t_, hx_, fx_, rx_) \
    { t_, { hx_,0, 0.03f, 1, {{0,0},{40,30},{58,-38},{84,-92},{144,-128}}, -0.03f, 1, 0, 0,0, \
            {fx_, FOOT_Y}, {rx_, FOOT_Y}, 0, 0 } }
static const hl_key KEYS_STRIDE[] = {
    SKEY(0.0f, 0, 343, 307),   SKEY(1.2f, 8, 343, 307),
    SKEY(1.7f, 30, 415, 307),  SKEY(2.2f, 40, 415, 307),
    SKEY(2.7f, 62, 415, 380),  SKEY(3.2f, 74, 415, 380),
    SKEY(3.7f, 92, 470, 380),  SKEY(4.2f, 92, 470, 380),
    SKEY(7.4f, 92, 470, 380),  SKEY(7.8f, 74, 470, 380),
    SKEY(8.3f, 48, 470, 307),  SKEY(8.7f, 38, 470, 307),
    SKEY(9.2f, 22, 405, 307),  SKEY(9.7f, 10, 405, 307),
    SKEY(10.2f, 0, 343, 307),  SKEY(11.0f, 0, 343, 307),
};
#undef SKEY
/* FLIGHT — takeoff, circuit right, turn, return leg, turn, land home.
 * Feet: world while grounded, body-frame trailing while airborne
 * (converted per-key at evaluation). 13 s. */
#define FKEY(t_, hx_, hy_, pitch_, facing_, fb_, sc_) \
    { t_, { hx_, hy_, pitch_, facing_, {{0,0},{30,16},{20,-24},{42,-50},{84,-64}}, 0, 0.9f, 0, 0,0, \
            {343.0f, 546.0f}, {307.0f, 546.0f}, fb_, 0, sc_ } }
static const hl_key KEYS_FLIGHT[] = {
    { 0.0f, BASE_PARAMS },
    FKEY(0.9f, 2, 22, 0.14f, 1, 0, 1.0f),
    FKEY(1.5f, 44, -18, -0.10f, 1, 1, 0.92f),
    FKEY(3.0f, 150, -64, -0.04f, 1, 1, 0.66f),
    FKEY(4.6f, 225, -118, 0.0f, 1, 1, 0.62f),
    FKEY(5.2f, 232, -126, 0.0f, -1, 1, 0.62f),
    FKEY(7.0f, 120, -132, 0.0f, -1, 1, 0.62f),
    FKEY(8.8f, 96, -122, 0.0f, -1, 1, 0.62f),
    FKEY(9.4f, 92, -104, 0.05f, 1, 1, 0.64f),
    FKEY(10.6f, 40, -48, 0.10f, 1, 1, 0.78f),
    FKEY(11.6f, 0, 0, 0.05f, 1, 0, 0.92f),
    { 12.4f, BASE_PARAMS },
    { 13.0f, BASE_PARAMS },
};
#undef FKEY
/* COURTSHIP — rise, bill skyward, sway, settle. 11 s. */
static const hl_key KEYS_COURTSHIP[] = {
    { 0.0f, BASE_PARAMS },
    { 1.2f, { 0,-16, -0.05f, 1, {{0,0},{40,30},{58,-38},{84,-92},{144,-128}}, 0, 1, 0, 0,0, {FOOT_F_HOME_X, FOOT_Y}, {FOOT_R_HOME_X, FOOT_Y}, 0, 0 } },
    { 2.2f, { 0,-30, -0.05f, 1, {{0,0},{24,-8},{14,-26},{38,-40},{66,-46}}, -1.05f, 0.8f, 0, 0,0, {FOOT_F_HOME_X, FOOT_Y}, {FOOT_R_HOME_X, FOOT_Y}, 0, 0 } },
    { 8.2f, { 0,-30, -0.05f, 1, {{0,0},{24,-8},{14,-26},{38,-40},{66,-46}}, -1.05f, 0.8f, 0, 0,0, {FOOT_F_HOME_X, FOOT_Y}, {FOOT_R_HOME_X, FOOT_Y}, 0, 0 } },
    { 9.6f, { 0,-8, -0.02f, 1, {{0,0},{40,30},{58,-38},{84,-92},{144,-128}}, 0, 1, 0, 0,0, {FOOT_F_HOME_X, FOOT_Y}, {FOOT_R_HOME_X, FOOT_Y}, 0, 0 } },
    { 11.0f, BASE_PARAMS },
};

typedef struct { const hl_key *keys; int n; float dur; } hl_track;
static const hl_track TRACKS[HL_NBEHAV] = {
    { NULL, 0, 0 },                                                   /* idle */
    { KEYS_PREEN, (int)(sizeof(KEYS_PREEN)/sizeof(hl_key)), 10.0f },
    { KEYS_STRIDE, (int)(sizeof(KEYS_STRIDE)/sizeof(hl_key)), 11.0f },
    { KEYS_STRIKE, (int)(sizeof(KEYS_STRIKE)/sizeof(hl_key)), 9.0f },
    { KEYS_MISS, (int)(sizeof(KEYS_MISS)/sizeof(hl_key)), 10.0f },
    { KEYS_STRETCH, (int)(sizeof(KEYS_STRETCH)/sizeof(hl_key)), 9.0f },
    { KEYS_FLIGHT, (int)(sizeof(KEYS_FLIGHT)/sizeof(hl_key)), 13.0f },
    { KEYS_COURTSHIP, (int)(sizeof(KEYS_COURTSHIP)/sizeof(hl_key)), 11.0f },
};

static const char *NAMES[HL_NBEHAV] = {
    "idle", "preen", "stride", "strike", "miss", "stretch", "flight", "courtship",
};
const char *hl_behavior_name(int id) { return (id >= 0 && id < HL_NBEHAV) ? NAMES[id] : "?"; }
float hl_behavior_duration(int id) { return (id >= 0 && id < HL_NBEHAV) ? TRACKS[id].dur : 0; }

/* ------------------------------------------------------------------ */
static float clampf(float v, float a, float b) { return v < a ? a : (v > b ? b : v); }
static float lerpf(float a, float b, float u) { return a + (b - a) * u; }
static float smooth(float u) { u = clampf(u, 0, 1); return u * u * (3 - 2 * u); }

/* Feet conversion for one key: body-frame feet are offsets trailing
 * the body; convert with that key's own body transform. */
static void key_feet_world(const hl_params *p, float outF[2], float outR[2])
{
    if (!p->feet_body) {
        outF[0] = p->footF[0]; outF[1] = p->footF[1];
        outR[0] = p->footR[0]; outR[1] = p->footR[1];
        return;
    }
    /* airborne: feet trail behind/below the hips, body frame */
    float scl = (p->scale > 0.05f && p->scale < 3.0f) ? p->scale : 1.0f;
    const float tf[2] = {-272.0f * scl, 40.0f * scl}, tr[2] = {-296.0f * scl, 54.0f * scl};
    float c = cosf(p->pitch * p->facing), s = sinf(p->pitch * p->facing);
    float hx = HIP_HOME_X + p->hx, hy = HIP_HOME_Y + p->hy;
    outF[0] = hx + c * (p->facing * tf[0]) - s * tf[1];
    outF[1] = hy + s * (p->facing * tf[0]) + c * tf[1];
    outR[0] = hx + c * (p->facing * tr[0]) - s * tr[1];
    outR[1] = hy + s * (p->facing * tr[0]) + c * tr[1];
}

static void lerp_params(const hl_params *a, const hl_params *b, float u, hl_params *o)
{
    o->hx = lerpf(a->hx, b->hx, u);
    o->hy = lerpf(a->hy, b->hy, u);
    o->pitch = lerpf(a->pitch, b->pitch, u);
    o->facing = lerpf(a->facing, b->facing, u);
    for (int i = 0; i < 5; i++)
        for (int j = 0; j < 2; j++)
            o->neck[i][j] = lerpf(a->neck[i][j], b->neck[i][j], u);
    o->head_pitch = lerpf(a->head_pitch, b->head_pitch, u);
    o->neck_w = lerpf(a->neck_w, b->neck_w, u);
    o->wing = lerpf(a->wing, b->wing, u);
    o->wing_amp = 0; o->wing_phase = 0;
    float af[2], ar[2], bf[2], br[2];
    key_feet_world(a, af, ar);
    key_feet_world(b, bf, br);
    /* stride step lift: a foot travelling horizontally arcs up */
    float uF = u, lift;
    o->footF[0] = lerpf(af[0], bf[0], uF);
    o->footF[1] = lerpf(af[1], bf[1], uF);
    lift = fabsf(bf[0] - af[0]);
    if (lift > 20.0f) o->footF[1] -= sinf(3.14159265f * uF) * (lift * 0.30f < 26.0f ? lift * 0.30f : 26.0f);
    o->footR[0] = lerpf(ar[0], br[0], u);
    o->footR[1] = lerpf(ar[1], br[1], u);
    lift = fabsf(br[0] - ar[0]);
    if (lift > 20.0f) o->footR[1] -= sinf(3.14159265f * u) * (lift * 0.30f < 26.0f ? lift * 0.30f : 26.0f);
    o->feet_body = 0;
    o->rise = 0;
    o->scale = lerpf(a->scale, b->scale, u);
}

void hl_pose_at(int behavior, float t, float t_abs, hl_params *out)
{
    hl_params base = P();
    if (behavior == HL_IDLE || behavior < 0 || behavior >= HL_NBEHAV || TRACKS[behavior].keys == NULL) {
        *out = base;
        /* breathing: belly-root sway, slow and small; stillness first */
        float br = sinf(t_abs * 6.2831853f * 0.20f);
        out->hy += br * 1.4f;
        out->neck[1][0] += sinf(t_abs * 6.2831853f * 0.11f) * 1.6f;
        out->neck[3][1] += br * 1.1f;
        return;
    }
    const hl_track *tr = &TRACKS[behavior];
    if (t <= tr->keys[0].t) {
        *out = tr->keys[0].p;
    } else if (t >= tr->keys[tr->n - 1].t) {
        *out = tr->keys[tr->n - 1].p;
    } else {
        int i = 0;
        while (i < tr->n - 2 && t > tr->keys[i + 1].t) i++;
        float span = tr->keys[i + 1].t - tr->keys[i].t;
        float u = span > 0 ? smooth((t - tr->keys[i].t) / span) : 0;
        lerp_params(&tr->keys[i].p, &tr->keys[i + 1].p, u, out);
    }
    /* the breath rides under every behavior, faintly */
    out->hy += sinf(t_abs * 6.2831853f * 0.20f) * 0.8f;

    if (behavior == HL_PREEN && t > 2.6f && t < 6.8f) {
        /* nibbling: small fast head tremor while the bill works */
        out->neck[4][0] += sinf(t * 6.2831853f * 2.1f) * 2.4f;
        out->neck[4][1] += sinf(t * 6.2831853f * 2.7f) * 1.8f;
        out->head_pitch += sinf(t * 6.2831853f * 2.1f) * 0.04f;
    }
    if (behavior == HL_MISS && t > 5.0f && t < 6.0f) {
        /* the head-shake: no, nothing there */
        out->head_pitch += sinf((t - 5.0f) * 6.2831853f * 4.5f) * 0.055f;
        out->neck[4][0] += sinf((t - 5.0f) * 6.2831853f * 4.5f) * 3.0f;
    }
    if (behavior == HL_COURTSHIP) {
        if (t > 3.0f && t < 8.2f) {           /* sway on straight legs */
            float sw = sinf((t - 3.0f) * 6.2831853f * 0.16f);
            out->hx += sw * 7.0f;
            out->neck[3][0] += sw * 5.0f;
            out->neck[4][0] += sw * 7.0f;
        }
        if (t > 2.2f && t < 3.1f) {           /* bill snaps */
            float ph = (t - 2.2f) / 0.3f;
            out->head_pitch += sinf(ph * 3.14159265f) * -0.10f * (sinf(ph * 9.4247f) > 0 ? 1.0f : 0.3f);
        }
    }
    if (behavior == HL_FLIGHT) {
        /* wingbeat: 2.85 Hz takeoff/climb, 2.7 Hz cruise, flare slow */
        float ph = 0;
        if (t > 1.1f) {
            float t1 = t - 1.1f;
            /* piecewise-integrated phase: no snap at rate changes */
            float cyc = 2.85f * (t1 < 1.9f ? t1 : 1.9f)
                      + 2.70f * (t1 > 1.9f ? (t1 < 9.3f ? t1 : 9.3f) - 1.9f : 0)
                      + 1.70f * (t1 > 9.3f ? t1 - 9.3f : 0);
            ph = 6.2831853f * cyc;
            out->wing_amp = clampf((t - 1.1f) / 0.7f, 0, 1);
            if (t > 6.4f && t < 7.8f) out->wing_amp = 0.35f;   /* glide */
            if (t > 11.3f) out->wing_amp = clampf((12.2f - t) / 0.9f, 0, 1);
        }
        out->wing_phase = ph;
    }
}

/* ------------------------------------------------------------------ */
/* Outline builder                                                     */
/* ------------------------------------------------------------------ */
#define MAX_PTS 640
typedef struct { float x, y; } pt;
static pt OUT[MAX_PTS];
static int OUT_N;
static pt EYE_PT;
static void push(float x, float y)
{
    if (OUT_N < MAX_PTS) { OUT[OUT_N].x = x; OUT[OUT_N].y = y; OUT_N++; }
}

/* Catmull-Rom through control points, appending samples (the first
 * control point is appended by the caller / previous segment). */
static void cr_append(const pt *cp, int n, int per_seg)
{
    for (int i = 0; i < n - 1; i++) {
        pt p0 = cp[i > 0 ? i - 1 : 0], p1 = cp[i], p2 = cp[i + 1], p3 = cp[i + 2 < n ? i + 2 : n - 1];
        for (int j = (i == 0 ? 0 : 1); j <= per_seg; j++) {
            float u = (float)j / per_seg, u2 = u * u, u3 = u2 * u;
            float x = 0.5f * ((2 * p1.x) + (-p0.x + p2.x) * u + (2 * p0.x - 5 * p1.x + 4 * p2.x - p3.x) * u2 + (-p0.x + 3 * p1.x - 3 * p2.x + p3.x) * u3);
            float y = 0.5f * ((2 * p1.y) + (-p0.y + p2.y) * u + (2 * p0.y - 5 * p1.y + 4 * p2.y - p3.y) * u2 + (-p0.y + 3 * p1.y - 3 * p2.y + p3.y) * u3);
            push(x, y);
        }
    }
}

/* body-frame -> world */
typedef struct { float hx, hy, c, s, f, scl; } xform;
static pt xpt(const xform *X, float lx, float ly)
{
    float mx = X->f * lx * X->scl;
    float my = ly * X->scl;
    pt w = { X->hx + X->c * mx - X->s * my, X->hy + X->s * mx + X->c * my };
    return w;
}

/* Ankle: at 49% of the leg (canon: ankle joint ~49% down), bowed a
 * little backward; the bow grows as the leg compresses (crouch,
 * swing) and stays small when the leg trails straight in flight. */
static pt leg_ankle(pt hip, pt foot, float facing)
{
    float dx = foot.x - hip.x, dy = foot.y - hip.y;
    float d = hypotf(dx, dy);
    float bend = 6.0f + clampf((205.0f - d) * 0.30f, 0.0f, 26.0f);
    pt a = { hip.x + dx * 0.49f - facing * bend, hip.y + dy * 0.49f };
    return a;
}

static void leg_excursion(const xform *X, float hipx, float hipy, pt foot, const hl_params *p)
{
    pt hip = xpt(X, hipx, hipy);
    pt ank = leg_ankle(hip, foot, p->facing);
    push(hip.x, hip.y);
    push(ank.x, ank.y);
    push(foot.x, foot.y);
    push(foot.x + p->facing * 20.0f, foot.y);          /* toes */
    push(foot.x, foot.y);
    push(ank.x, ank.y);
    push(hip.x, hip.y);
}

static int build_outline(const hl_params *p)
{
    OUT_N = 0;
    xform X = { HIP_HOME_X + p->hx, HIP_HOME_Y + p->hy,
                cosf(p->pitch), p->facing * sinf(p->pitch), p->facing,
                (p->scale > 0.05f && p->scale < 3.0f) ? p->scale : 1.0f };

    /* --- tail + back (with the stretch-wing excursion folded in) --- */
    pt back[16];
    int nb = 0;
    for (int i = 0; i < 8; i++) {
        back[nb++] = (pt){ BODY_BACK[i][0], BODY_BACK[i][1] };
        if (i == 4 && p->wing > 0.02f) {  /* wing excursion, mid-back */
            float s = p->wing;
            back[nb++] = (pt){ lerpf(130, 30, s), lerpf(-181, -196, s) };
            back[nb++] = (pt){ lerpf(160, -305, s), lerpf(-175, -120, s) };
            back[nb++] = (pt){ lerpf(185, -40, s), lerpf(-169, -120, s) };
        }
    }
    pt backw[16];
    for (int i = 0; i < nb; i++) backw[i] = xpt(&X, back[i].x, back[i].y);
    cr_append(backw, nb, 5);

    /* --- flight wings: fan excursions at the shoulder. The wing
     * rotates about the shoulder through the beat: tip angle sweeps
     * from up-back (upstroke) to up-forward (downstroke) so the wing
     * stays a readable shape above the back in profile. ------------ */
    if (p->wing_amp > 0.02f) {
        pt sho = xpt(&X, 254, -152);
        float grow = 0.25f + 0.75f * p->wing_amp;
        for (int wgi = 0; wgi < 2; wgi++) {
            float ph = p->wing_phase + (wgi ? 0.8f : 0.0f);
            float R = 175.0f * grow * (wgi ? 0.78f : 1.0f);
            float a = -1.5708f - 0.96f * sinf(ph);       /* tip angle */
            float bx = wgi ? -26.0f : 0.0f, by = wgi ? 13.0f : 0.0f;
            pt base = xpt(&X, 254 + bx, -152 + by);
            pt lead = xpt(&X, 254 + bx + cosf(a - 0.30f) * R * 0.52f,
                             -152 + by + sinf(a - 0.30f) * R * 0.52f);
            pt tip  = xpt(&X, 254 + bx + cosf(a) * R,
                             -152 + by + sinf(a) * R);
            pt trai = xpt(&X, 254 + bx + cosf(a + 0.52f) * R * 0.60f,
                             -152 + by + sinf(a + 0.52f) * R * 0.60f);
            if (wgi == 0) push(sho.x, sho.y);
            push(lead.x, lead.y); push(tip.x, tip.y); push(trai.x, trai.y);
            push(base.x, base.y);
        }
    }

    /* --- neck: control polygon -> centerline -> two sides ---------- */
    pt ctrl[5];
    for (int i = 0; i < 5; i++)
        ctrl[i] = xpt(&X, NECK_ROOT_X + p->neck[i][0], NECK_ROOT_Y + p->neck[i][1]);
    pt center[40];
    {
        pt tmp[48];
        int tn = 0;
        for (int i = 0; i < 4; i++) {
            pt p0 = ctrl[i > 0 ? i - 1 : 0], p1 = ctrl[i], p2 = ctrl[i + 1], p3 = ctrl[i + 2 < 5 ? i + 2 : 4];
            for (int j = (i == 0 ? 0 : 1); j <= 10; j++) {
                float u = (float)j / 10, u2 = u * u, u3 = u2 * u;
                tmp[tn].x = 0.5f * ((2 * p1.x) + (-p0.x + p2.x) * u + (2 * p0.x - 5 * p1.x + 4 * p2.x - p3.x) * u2 + (-p0.x + 3 * p1.x - 3 * p2.x + p3.x) * u3);
                tmp[tn].y = 0.5f * ((2 * p1.y) + (-p0.y + p2.y) * u + (2 * p0.y - 5 * p1.y + 4 * p2.y - p3.y) * u2 + (-p0.y + 3 * p1.y - 3 * p2.y + p3.y) * u3);
                tn++;
            }
        }
        /* arc-length resample to 26 points */
        float total = 0;
        for (int i = 1; i < tn; i++) total += hypotf(tmp[i].x - tmp[i - 1].x, tmp[i].y - tmp[i - 1].y);
        float step = total / 25.0f, acc = 0;
        int ti = 1;
        center[0] = tmp[0];
        for (int k = 1; k < 26; k++) {
            float want = step * k;
            while (ti < tn && acc + hypotf(tmp[ti].x - tmp[ti - 1].x, tmp[ti].y - tmp[ti - 1].y) < want) {
                acc += hypotf(tmp[ti].x - tmp[ti - 1].x, tmp[ti].y - tmp[ti - 1].y);
                ti++;
            }
            if (ti >= tn) { center[k] = tmp[tn - 1]; continue; }
            float seg = hypotf(tmp[ti].x - tmp[ti - 1].x, tmp[ti].y - tmp[ti - 1].y);
            float fr = seg > 0 ? (want - acc) / seg : 0;
            center[k].x = lerpf(tmp[ti - 1].x, tmp[ti].x, fr);
            center[k].y = lerpf(tmp[ti - 1].y, tmp[ti].y, fr);
        }
    }
    /* back side of neck, root -> head */
    for (int k = 0; k < 26; k++) {
        pt a = center[k > 0 ? k - 1 : 0], b = center[k < 25 ? k + 1 : 25];
        float tx = b.x - a.x, ty = b.y - a.y, L = hypotf(tx, ty) + 1e-6f;
        float u = k / 25.0f;
        float w = (30.0f + (20.0f - 30.0f) * u) * (1.0f + 0.12f * sinf(3.14159265f * u)) * p->neck_w;
        push(center[k].x + (ty / L) * w * 0.5f, center[k].y + (-tx / L) * w * 0.5f);
    }
    /* --- head: crown, bill, chin ------------------------------------ */
    pt E = center[25];
    float tx = center[25].x - center[23].x, ty = center[25].y - center[23].y;
    float L = hypotf(tx, ty) + 1e-6f;
    float ca = cosf(p->head_pitch * p->facing), sa = p->facing * sinf(p->head_pitch * p->facing);
    float dx = (tx / L) * ca - (ty / L) * sa, dy = (tx / L) * sa + (ty / L) * ca;
    float px = dy, py = -dx;                     /* up-side normal */
    push(E.x + dx * 34 + px * 11, E.y + dy * 34 + py * 11);          /* crown */
    push(E.x + dx * 102 + px * 1, E.y + dy * 102 + py * 1);          /* bill tip */
    push(E.x + dx * 72 - px * 7, E.y + dy * 72 - py * 7);            /* chin */
    /* throat side of neck, head -> root */
    for (int k = 25; k >= 0; k--) {
        pt a = center[k > 0 ? k - 1 : 0], b = center[k < 25 ? k + 1 : 25];
        float gx = b.x - a.x, gy = b.y - a.y, G = hypotf(gx, gy) + 1e-6f;
        float u = k / 25.0f;
        float w = (30.0f + (20.0f - 30.0f) * u) * (1.0f + 0.12f * sinf(3.14159265f * u)) * p->neck_w;
        push(center[k].x - (gy / G) * w * 0.5f, center[k].y - (-gx / G) * w * 0.5f);
    }
    /* --- breast + belly A ------------------------------------------- */
    {
        pt pts[8]; int n = 0;
        pts[n++] = xpt(&X, 292, -84);            /* chest curve point */
        for (int i = 0; i < 4; i++) pts[n++] = xpt(&X, BODY_BELLY_A[i][0], BODY_BELLY_A[i][1]);
        cr_append(pts, n, 5);
    }
    /* --- legs + belly between/after ---------------------------------- */
    leg_excursion(&X, HIP_F_X, HIP_F_Y, (pt){ p->footF[0], p->footF[1] }, p);
    push(xpt(&X, BODY_BELLY_B[0][0], BODY_BELLY_B[0][1]).x,
         xpt(&X, BODY_BELLY_B[0][0], BODY_BELLY_B[0][1]).y);
    leg_excursion(&X, HIP_R_X, HIP_R_Y, (pt){ p->footR[0], p->footR[1] }, p);
    {
        pt pts[4];
        for (int i = 0; i < 4; i++) pts[i] = xpt(&X, BODY_BELLY_C[i][0], BODY_BELLY_C[i][1]);
        cr_append(pts, 4, 5);
    }
    /* close: undertail -> tail tip (first point) */
    push(OUT[0].x, OUT[0].y);

    /* eye: a tiny curl near the head — the one allowed "lift" */
    /* (drawn by the rasterizer as a separate mini-polyline) */
    EYE_PT.x = E.x + dx * 30 + px * 5;
    EYE_PT.y = E.y + dy * 30 + py * 5;
    return OUT_N;
}

/* ------------------------------------------------------------------ */
/* Rasterizer                                                          */
/* ------------------------------------------------------------------ */
static void stamp(uint16_t *fb, int x, int y, int r, uint16_t col)
{
    for (int dy = -r; dy <= r; dy++)
        for (int dx = -r; dx <= r; dx++) {
            if (dx * dx + dy * dy > r * r + r) continue;
            int X = x + dx, Y = y + dy;
            if (X >= 0 && X < HL_W && Y >= 0 && Y < HL_H) fb[Y * HL_W + X] = col;
        }
}
static void seg(uint16_t *fb, float x0, float y0, float x1, float y1, int r, uint16_t col)
{
    float dx = x1 - x0, dy = y1 - y0;
    int n = (int)(fmaxf(fabsf(dx), fabsf(dy))) + 1;
    if (n < 1) n = 1;
    for (int i = 0; i <= n; i++)
        stamp(fb, (int)lroundf(x0 + dx * i / n), (int)lroundf(y0 + dy * i / n), r, col);
}

void hl_render_pose(uint16_t *fb, const hl_params *p, const hl_ripple *rip, int nrip, float t_abs)
{
    uint32_t *w = (uint32_t *)fb;
    uint32_t paper2 = HL_PAPER | (HL_PAPER << 16);
    for (int i = 0; i < HL_W * HL_H / 2; i++) w[i] = paper2;

    /* ripple rings: caused marks only, expanding, thinning, gone */
    for (int i = 0; i < nrip; i++) {
        float age = t_abs - rip[i].t0;
        if (age < 0 || age > 1.6f) continue;
        float u = age / 1.6f;
        float R = (6.0f + 30.0f * u) * rip[i].scale;
        int thick = (u < 0.55f) ? 1 : 0;
        for (int a = 0; a < 72; a++) {
            float th = a * 6.2831853f / 72.0f;
            int X = (int)lroundf(rip[i].x + cosf(th) * R);
            int Y = (int)lroundf(rip[i].y + 2 + sinf(th) * R * 0.30f);
            stamp(fb, X, Y, thick, HL_INK);
        }
    }

    int n = build_outline(p);
    for (int i = 1; i < n; i++)
        seg(fb, OUT[i - 1].x, OUT[i - 1].y, OUT[i].x, OUT[i].y, 1, HL_INK);
    /* eye curl */
    for (int a = 0; a < 10; a++) {
        float t0 = a * 6.2831853f / 10.0f, t1 = (a + 1) * 6.2831853f / 10.0f;
        seg(fb, EYE_PT.x + cosf(t0) * 3.2f, EYE_PT.y + sinf(t0) * 3.2f,
                EYE_PT.x + cosf(t1) * 3.2f, EYE_PT.y + sinf(t1) * 3.2f, 0, HL_INK);
    }
}

/* ------------------------------------------------------------------ */
/* Scene: shuffle-bag living loop (living_loop_scheduler.py rules)     */
/* ------------------------------------------------------------------ */
static uint32_t rng_next(hl_scene *s)
{
    uint32_t x = s->rng;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    s->rng = x;
    return x;
}
static float rng_unit(hl_scene *s) { return (rng_next(s) >> 8) * (1.0f / 16777216.0f); }

static const int BAG_RECIPE[HL_NBEHAV] = { 0, 3, 3, 2, 2, 2, 1, 1 };  /* by behavior id */
static void reshuffle(hl_scene *s)
{
    int n = 0;
    for (int b = 1; b < HL_NBEHAV; b++)
        for (int k = 0; k < BAG_RECIPE[b]; k++) s->bag[n++] = b;
    for (int i = n - 1; i > 0; i--) {
        int j = (int)(rng_next(s) % (uint32_t)(i + 1));
        int tmp = s->bag[i]; s->bag[i] = s->bag[j]; s->bag[j] = tmp;
    }
    if (s->last_played >= 0 && s->bag[0] == s->last_played) {
        for (int i = 1; i < n; i++)
            if (s->bag[i] != s->last_played) {
                int tmp = s->bag[0]; s->bag[0] = s->bag[i]; s->bag[i] = tmp;
                break;
            }
    }
    s->bag_n = n;
}
static float idle_hold(hl_scene *s)
{
    if (s->proof_speed) return 2.0f + rng_unit(s) * 3.0f;
    return 20.0f + rng_unit(s) * 70.0f;
}

void hl_scene_init(hl_scene *s, uint16_t *fb, uint32_t seed, int proof_speed)
{
    memset(s, 0, sizeof(*s));
    s->fb = fb;
    s->rng = seed ? seed : 0x9E3779B9u;
    s->proof_speed = proof_speed;
    s->state = HL_IDLE;
    s->state_t = 0;
    s->last_played = -1;
    reshuffle(s);
    s->state_dur = idle_hold(s);
}
void hl_scene_force(hl_scene *s, int behavior)
{
    s->state = behavior;
    s->state_t = 0;
    s->ripple_stage = 0;
    s->state_dur = (behavior == HL_IDLE) ? 1e9f : hl_behavior_duration(behavior);
    if (behavior != HL_IDLE) s->last_played = behavior;
}

/* ripple spawn events: {behavior, state_t, x, scale} */
typedef struct { int b; float t, x, scale; } spawn_ev;
static const spawn_ev SPAWNS[] = {
    { HL_STRIKE, 3.68f, 820, 1.0f }, { HL_STRIKE, 3.95f, 820, 0.8f },
    { HL_MISS, 3.85f, 700, 0.9f },
    { HL_STRIDE, 1.7f, 415, 0.55f }, { HL_STRIDE, 2.7f, 380, 0.55f },
    { HL_STRIDE, 3.7f, 470, 0.55f }, { HL_STRIDE, 8.3f, 307, 0.55f },
    { HL_STRIDE, 9.2f, 405, 0.55f }, { HL_STRIDE, 10.2f, 343, 0.55f },
    { HL_FLIGHT, 1.5f, 325, 0.9f }, { HL_FLIGHT, 11.6f, 325, 0.9f },
    { HL_STRETCH, 3.2f, 185, 0.5f },
};
static void check_spawns(hl_scene *s)
{
    int idx = 0;
    for (unsigned i = 0; i < sizeof(SPAWNS) / sizeof(SPAWNS[0]); i++) {
        if (SPAWNS[i].b != s->state) continue;
        if (idx++ < s->ripple_stage) continue;
        if (s->state_t >= SPAWNS[i].t) {
            if (s->ripples_n < HL_MAX_RIPPLES) {
                s->ripples[s->ripples_n].x = SPAWNS[i].x;
                s->ripples[s->ripples_n].y = FOOT_Y;
                s->ripples[s->ripples_n].t0 = s->t_abs;
                s->ripples[s->ripples_n].scale = SPAWNS[i].scale;
                s->ripples_n++;
            }
            s->ripple_stage++;
        }
        break;
    }
}

void hl_scene_step(hl_scene *s, float dt)
{
    s->t_abs += dt;
    s->state_t += dt;
    check_spawns(s);
    /* prune dead ripples */
    int m = 0;
    for (int i = 0; i < s->ripples_n; i++)
        if (s->t_abs - s->ripples[i].t0 <= 1.7f) s->ripples[m++] = s->ripples[i];
    s->ripples_n = m;

    if (s->state_t >= s->state_dur) {
        if (s->state == HL_IDLE) {
            if (s->bag_n <= 0) reshuffle(s);
            int b = s->bag[0];
            memmove(&s->bag[0], &s->bag[1], sizeof(int) * (unsigned)(s->bag_n - 1));
            s->bag_n--;
            hl_scene_force(s, b);
        } else {
            s->state = HL_IDLE;
            s->state_t = 0;
            s->state_dur = idle_hold(s);
        }
    }
    hl_params p;
    hl_pose_at(s->state, s->state_t, s->t_abs, &p);
    hl_render_pose(s->fb, &p, s->ripples, s->ripples_n, s->t_abs);
}
