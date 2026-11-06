/*
 * heron — SEQUENCE 2 player (layer pipeline + mirroring + stride,
 * built overnight 2026-11-06 on Jimmy's go).
 *
 * What changed from seq1 (and why): seq1 stored every frame as a
 * finished COMPOSITE (bird multiplied over the marsh plate). Jimmy's
 * ruling (2026-11-05): "why would you need to store the mirror? write
 * the ability to flip the sequence in the code of the program. keep
 * the background the same." Seq2 stores every frame as a BIRD-ONLY
 * LAYER (flat paper canvas) plus the marsh plate once, and composites
 * at runtime: decode layer -> optional horizontal flip -> LUT multiply
 * over the un-moved plate -> present. Layers were recovered from the
 * shipped seq1 composites by division (layer = composite x 255 /
 * plate), then cleaned: pixels belonging to no drawn mark (connected-
 * component test in composite-delta space) and within a small delta
 * of the background snap to exact paper — the bird's own pixels keep
 * the exact division, so the drawings on screen are the ones Jimmy
 * approved; the snap only strips division-amplified JPEG noise out of
 * the empty marsh, which is what makes the span composite fast.
 *
 * The composite core is the bench-V8 design (2026-11-06, Jimmy's go):
 * per-row SPAN compositing (restore last frame's span from the
 * plate-times-paper buffer, scan the layer row's ink span, composite
 * only that span) split across both cores, with decode pipelined on
 * core 1. Bench V8 measured 74.7 ms/frame average against the 83.3 ms
 * tick for the strike — mirrored 12 fps MJPEG fits. Pose sequences
 * composite full-frame on pose change only (dual-core split, ~half a
 * tick), which is effectively free.
 *
 * SIDES: the bird has a home on the LEFT (drawings as stored) and a
 * mirrored home on the RIGHT (flip in code; the background never
 * moves). s_mirrored says which side the bird is on; every behavior
 * renders through the current side. STRIDE is the only side-changer:
 * it walks across the screen, turns around through drawn progressive
 * views (three-quarter, frontal, three-quarter — never a card flip),
 * and settles on the other side's home, toggling s_mirrored.
 *
 * PLAYBACK (Jimmy, 2026-11-06): shuffle-bag, random non-repeating —
 * each bag plays every behavior once in shuffled order with the home
 * rest between, then a fresh bag is drawn; a bag's first behavior is
 * never the previous bag's last. STRIDE EXCEPTION (Jimmy, 2026-11-06):
 * stride triggers only 50% of the time — each bag, a coin flip decides
 * whether stride is in the bag at all (bag of 7 with it, 6 without).
 *
 * STRIDE artwork: drawn fresh by Mordecai 2026-11-06 — the carriage
 * from the project's standing reference photograph
 * (ref_standing_gbh.png, reference library) with the home drawing
 * (K_coil_color_redo.png) as identity/style reference; walk-cycle and
 * turn poses chained from the carriage by local edits. REDO (same
 * day, Jimmy's "dragging his feet" verdict): the gait now follows
 * the measured step cycle — foot-anchored poses, dx only at pass
 * boundaries, head world-locked in the passes (see the STRIDE
 * section comment). The turn is drawn, per Jimmy's honest-turns
 * ruling (2026-11-05).
 *
 * All other artwork/attribution is unchanged from seq1: strike (60
 * frames, choreography fb-weber-sashimi.mp4 + fb-davesmith-strike.mp4),
 * idle / stretch / preen timing tables (their choreography docs),
 * listening (pose anatomy fb-alvarez-standing.mp4), flight pair
 * (Boga slow-motion reels, the Teague takeoff, the Astroland winter
 * flight, Mark Smith's glide-in). Motion reference only throughout;
 * no clip frames appear in the artwork. Marsh plate:
 * marsh_plate_pick.png at the locked home registration.
 *
 * Board : Waveshare ESP32-P4-WIFI6-Touch-LCD-7B (Rev1.1), 1024x600
 * Decode: ESP32-P4 hardware JPEG decoder, PIL JPEG q82 4:2:2
 *         (subsampling=1; SOF luma byte 0x21) layers and plate.
 */
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "esp_err.h"
#include "esp_log.h"
#include "esp_timer.h"

#include "lvgl.h"
#include "bsp/esp32_p4_wifi6_touch_lcd_7b.h"
#include "bsp/display.h"
#include "driver/jpeg_decode.h"

#include "alert_plate_img.h"
#include "esp_partition.h"
#include "esp_random.h"

static const char *TAG = "heron_seq2";

/* ------------------------------------------------------------------ */
/* Assets partition: 0=strike layers, 1=flight out layers,             */
/* 2=flight home layers, 3=plate. Layout per make_assets_blob.py.      */
/* ------------------------------------------------------------------ */
#define ASSETS_MAGIC 0x54534148u /* 'HAST' little-endian */
enum { ASSET_STRIKE = 0, ASSET_FLIGHT_OUT = 1, ASSET_FLIGHT_HOME = 2,
       ASSET_PLATE = 3, ASSET_COUNT = 4 };
static const esp_partition_t *s_assets_part;
static uint32_t s_asset_off[ASSET_COUNT];
static uint32_t s_asset_len[ASSET_COUNT];
static bool s_assets_ok;

static bool assets_init(void)
{
    s_assets_part = esp_partition_find_first(ESP_PARTITION_TYPE_DATA,
                                             ESP_PARTITION_SUBTYPE_ANY, "assets");
    if (s_assets_part == NULL) {
        ESP_LOGW(TAG, "assets partition not found — clips disabled");
        return false;
    }
    esp_partition_mmap_handle_t h;
    const void *p = NULL;
    if (esp_partition_mmap(s_assets_part, 0, 64 * 1024,
                           ESP_PARTITION_MMAP_DATA, &p, &h) != ESP_OK) {
        ESP_LOGW(TAG, "assets header mmap failed — clips disabled");
        return false;
    }
    const uint32_t *hdr = (const uint32_t *)p;
    bool ok = (hdr[0] == ASSETS_MAGIC);
    if (ok) {
        for (int i = 0; i < ASSET_COUNT; i++) {
            s_asset_off[i] = hdr[1 + 2 * i];
            s_asset_len[i] = hdr[2 + 2 * i];
            if (s_asset_off[i] + s_asset_len[i] > s_assets_part->size) {
                ok = false;
            }
        }
    }
    esp_partition_munmap(h);
    if (!ok) {
        ESP_LOGW(TAG, "assets header invalid — clips disabled");
        return false;
    }
    ESP_LOGI(TAG, "assets ready: strike %lu B, out %lu B, home %lu B, plate %lu B",
             (unsigned long)s_asset_len[ASSET_STRIKE],
             (unsigned long)s_asset_len[ASSET_FLIGHT_OUT],
             (unsigned long)s_asset_len[ASSET_FLIGHT_HOME],
             (unsigned long)s_asset_len[ASSET_PLATE]);
    return true;
}

static const uint8_t *asset_map(int idx, esp_partition_mmap_handle_t *out_h)
{
    const void *p = NULL;
    if (esp_partition_mmap(s_assets_part, s_asset_off[idx], s_asset_len[idx],
                           ESP_PARTITION_MMAP_DATA, &p, out_h) != ESP_OK) {
        ESP_LOGW(TAG, "asset %d mmap failed", idx);
        return NULL;
    }
    return (const uint8_t *)p;
}

/* ------------------------------------------------------------------ */
/* Frame geometry + buffers                                            */
/* ------------------------------------------------------------------ */
#define FRAME_W        1024
#define FRAME_H        600
#define FRAME_STRIDE   (FRAME_W * 2)
#define FRAME_BYTES    (FRAME_W * FRAME_H * 2)    /* 1,228,800 */
#define OUT_BUF_BYTES  (FRAME_BYTES + 256 * 1024)
#define IN_BUF_BYTES   (128 * 1024)

#define FLIGHT_GAP_MS  30000   /* Jimmy: 30 s of empty marsh */
#define REST_HOLD_MS   9000

static lv_obj_t *s_img;
static jpeg_decoder_handle_t s_decoder;
static uint8_t *s_in_buf;            /* one encoded JPEG frame */
static uint8_t *s_bird_buf[2];       /* decoded layers (clip pipeline) */
static size_t s_bird_buf_size[2];
static uint8_t *s_pose_buf;          /* decoded layer (pose players) */
static size_t s_pose_buf_size;
static uint8_t *s_canvas;            /* persistent composite on screen */
static size_t s_canvas_size;
static uint8_t *s_plate_buf;         /* decoded marsh plate (RGB565) */
static uint8_t *s_plate_paper;       /* plate x home-paper (background) */

static lv_image_dsc_t s_frame_dsc = {
    .header = {
        .magic = LV_IMAGE_HEADER_MAGIC,
        .cf = LV_COLOR_FORMAT_RGB565,
        .flags = 0,
        .w = FRAME_W,
        .h = FRAME_H,
        .stride = FRAME_STRIDE,
    },
    .data_size = FRAME_BYTES,
    .data = NULL,
};
static bool s_frame_src_set;

static void present_frame(uint8_t *rgb565)
{
    bsp_display_lock(0);
    s_frame_dsc.data = rgb565;
    if (!s_frame_src_set) {
        lv_image_set_src(s_img, &s_frame_dsc);
        lv_obj_set_pos(s_img, 0, 0);
        s_frame_src_set = true;
    }
    lv_obj_invalidate(s_img);
    bsp_display_unlock();
}

static const jpeg_decode_cfg_t s_decode_cfg = {
    .output_format = JPEG_DECODE_OUT_FORMAT_RGB565,
    .rgb_order = JPEG_DEC_RGB_ELEMENT_ORDER_BGR,
};

/* Decode one standalone JPEG into buf. False on any failure. */
static bool decode_jpeg(const uint8_t *jpg, size_t len, uint8_t *buf, size_t buf_size)
{
    if (len > IN_BUF_BYTES) {
        return false;
    }
    memcpy(s_in_buf, jpg, len);
    uint32_t out_size = 0;
    return jpeg_decoder_process(s_decoder, &s_decode_cfg, s_in_buf, len,
                                buf, (uint32_t)buf_size, &out_size) == ESP_OK;
}

static const uint8_t *scan_to_marker(const uint8_t *p, const uint8_t *end, uint8_t marker)
{
    while (p + 1 < end) {
        if (p[0] == 0xFF && p[1] == marker) {
            return p;
        }
        p++;
    }
    return NULL;
}

/* ------------------------------------------------------------------ */
/* LUT multiply (bench-proven): out = layer x plate per channel.       */
/* ------------------------------------------------------------------ */
static uint8_t s_lut_rb[32 * 32];
static uint8_t s_lut_g[64 * 64];

static void build_tables(void)
{
    for (int a = 0; a < 32; a++) {
        for (int b = 0; b < 32; b++) {
            const int a8 = (a << 3) | (a >> 2), b8 = (b << 3) | (b >> 2);
            s_lut_rb[(a << 5) | b] = (uint8_t)(((a8 * b8) / 255) >> 3);
        }
    }
    for (int a = 0; a < 64; a++) {
        for (int b = 0; b < 64; b++) {
            const int a8 = (a << 2) | (a >> 4), b8 = (b << 2) | (b >> 4);
            s_lut_g[(a << 6) | b] = (uint8_t)(((a8 * b8) / 255) >> 2);
        }
    }
}

static inline uint16_t mul_px(uint16_t a, uint16_t p)
{
    const uint32_t r = s_lut_rb[(((a >> 11) & 31) << 5) | ((p >> 11) & 31)];
    const uint32_t g = s_lut_g[(((a >> 5) & 63) << 6) | ((p >> 5) & 63)];
    const uint32_t b = s_lut_rb[((a & 31) << 5) | (p & 31)];
    return (uint16_t)((r << 11) | (g << 5) | b);
}

/* The layers' flat paper, RGB565 (244,233,215) — multiply factor that
 * turns the bare plate into the shipped composites' background. */
#define PAPER565 ((uint16_t)((30 << 11) | (58 << 5) | 26))

/* ------------------------------------------------------------------ */
/* Composite machinery (bench V8 core, generalized: flip flag + dx).   */
/*                                                                     */
/* s_mirrored: false = bird on the LEFT home (layers as drawn),        */
/* true = bird on the RIGHT home (every layer flipped in code; the     */
/* marsh plate itself never moves). Stride is the only toggler.        */
/*                                                                     */
/* Two composite modes over the persistent canvas:                     */
/*  FULL  — every pixel: dst = mul(layer[srcx], plate) inside the      */
/*          bird, plate_paper outside. Used on pose changes.           */
/*  SPANS — per row: restore the previous frame's drawn span from      */
/*          plate_paper, scan the layer row's ink span, composite      */
/*          only that span. Used for 12 fps clips and for stride,      */
/*          where the composite must fit inside one 83 ms tick.        */
/* Both modes run rows [0, FRAME_H/2) on the caller and                */
/* [FRAME_H/2, FRAME_H) on a worker pinned to core 1, joined by task   */
/* notifications — the V8 pattern. srcx maps a destination x back to   */
/* layer space: unflipped srcx = x - dx; flipped srcx = W-1-x-dx       */
/* (dx is always the layer-space advance, so one stride table serves   */
/* both crossing directions).                                          */
/* ------------------------------------------------------------------ */
static bool s_mirrored;

#define PAPER_R5 30
#define PAPER_G6 58
#define PAPER_B5 26
static int16_t s_span_x0[FRAME_H];
static int16_t s_span_x1[FRAME_H];

static inline bool is_ink(uint16_t px)
{
    const int r = (px >> 11) & 31;
    const int g = (px >> 5) & 63;
    const int b = px & 31;
    return (PAPER_R5 - r) >= 3 || (PAPER_G6 - g) >= 5 || (PAPER_B5 - b) >= 3;
}

static inline int src_x(int x, bool flip, int dx)
{
    return flip ? (FRAME_W - 1 - x - dx) : (x - dx);
}

static void comp_full_rows(const uint16_t *bird, int y0, int y1, bool flip, int dx)
{
    const uint16_t *plate = (const uint16_t *)s_plate_buf;
    const uint16_t *paper = (const uint16_t *)s_plate_paper;
    uint16_t *dst = (uint16_t *)s_canvas;
    for (int y = y0; y < y1; y++) {
        const uint16_t *brow = bird + (size_t)y * FRAME_W;
        const uint16_t *prow = plate + (size_t)y * FRAME_W;
        const uint16_t *qrow = paper + (size_t)y * FRAME_W;
        uint16_t *drow = dst + (size_t)y * FRAME_W;
        for (int x = 0; x < FRAME_W; x++) {
            const int sx = src_x(x, flip, dx);
            drow[x] = (sx >= 0 && sx < FRAME_W) ? mul_px(brow[sx], prow[x]) : qrow[x];
        }
    }
}

static void comp_spans_rows(const uint16_t *bird, int y0, int y1, bool flip, int dx)
{
    const uint16_t *plate = (const uint16_t *)s_plate_buf;
    const uint16_t *paper = (const uint16_t *)s_plate_paper;
    uint16_t *dst = (uint16_t *)s_canvas;
    for (int y = y0; y < y1; y++) {
        const uint16_t *prow = plate + (size_t)y * FRAME_W;
        const uint16_t *qrow = paper + (size_t)y * FRAME_W;
        uint16_t *drow = dst + (size_t)y * FRAME_W;
        const uint16_t *brow = bird + (size_t)y * FRAME_W;
        /* Scan the new frame's ink span first (source coords). */
        int sx0 = -1, sx1 = -1;
        for (int x = 0; x < FRAME_W; x++) {
            if (is_ink(brow[x])) { sx0 = x; break; }
        }
        int ndx0 = 0, ndx1 = -1;   /* new span in dst coords; ndx1<0 = none */
        if (sx0 >= 0) {
            for (int x = FRAME_W - 1; x > sx0; x--) {
                if (is_ink(brow[x])) { sx1 = x; break; }
            }
            if (sx1 < 0) sx1 = sx0;
            ndx0 = flip ? (FRAME_W - 1 - sx1 - dx) : (sx0 + dx);
            ndx1 = flip ? (FRAME_W - 1 - sx0 - dx) : (sx1 + dx);
            if (ndx1 < 0 || ndx0 >= FRAME_W) {
                ndx1 = -1;
            } else {
                if (ndx0 < 0) ndx0 = 0;
                if (ndx1 >= FRAME_W) ndx1 = FRAME_W - 1;
            }
        }
        /* Restore ONLY the parts of the previous span the new span does
         * not cover (union restore — consecutive frames overlap heavily,
         * so the restore pass nearly vanishes for near-still spans). */
        if (s_span_x1[y] >= 0) {
            const int ox0 = s_span_x0[y], ox1 = s_span_x1[y];
            if (ndx1 < 0) {
                memcpy(drow + ox0, qrow + ox0, (size_t)(ox1 - ox0 + 1) * 2);
            } else {
                if (ox0 < ndx0) {
                    const int e = ox1 < ndx0 - 1 ? ox1 : ndx0 - 1;
                    memcpy(drow + ox0, qrow + ox0, (size_t)(e - ox0 + 1) * 2);
                }
                if (ox1 > ndx1) {
                    const int s = ox0 > ndx1 + 1 ? ox0 : ndx1 + 1;
                    memcpy(drow + s, qrow + s, (size_t)(ox1 - s + 1) * 2);
                }
            }
            s_span_x1[y] = -1;
        }
        if (ndx1 < 0) {
            continue;
        }
        for (int x = ndx0; x <= ndx1; x++) {
            const int sx = src_x(x, flip, dx);
            drow[x] = (sx >= 0 && sx < FRAME_W) ? mul_px(brow[sx], prow[x]) : qrow[x];
        }
        s_span_x0[y] = (int16_t)ndx0;
        s_span_x1[y] = (int16_t)ndx1;
    }
}

/* Dual-core job runner (the worker half). */
enum { JOB_FULL = 0, JOB_SPANS = 1 };
static TaskHandle_t s_comp_worker;
static TaskHandle_t s_comp_caller;
static const uint16_t *s_job_bird;
static int s_job_mode;
static bool s_job_flip;
static int s_job_dx;
static volatile bool s_comp_stop;

static void comp_worker_task(void *arg)
{
    (void)arg;
    while (!s_comp_stop) {
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        if (s_comp_stop) break;
        if (s_job_mode == JOB_FULL) {
            comp_full_rows(s_job_bird, FRAME_H / 2, FRAME_H, s_job_flip, s_job_dx);
        } else {
            comp_spans_rows(s_job_bird, FRAME_H / 2, FRAME_H, s_job_flip, s_job_dx);
        }
        if (s_comp_caller) xTaskNotifyGive(s_comp_caller);
    }
    vTaskDelete(NULL);
}

/* Composite the decoded layer in `bird` over the plate into the
 * canvas, rows split across both cores. Caller presents the canvas. */
static void comp_dual(const uint16_t *bird, int mode, bool flip, int dx)
{
    s_job_bird = bird;
    s_job_mode = mode;
    s_job_flip = flip;
    s_job_dx = dx;
    s_comp_caller = xTaskGetCurrentTaskHandle();
    xTaskNotifyGive(s_comp_worker);
    if (mode == JOB_FULL) {
        comp_full_rows(bird, 0, FRAME_H / 2, flip, dx);
    } else {
        comp_spans_rows(bird, 0, FRAME_H / 2, flip, dx);
    }
    ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
}

/* Reset the persistent canvas to the bare background and forget all
 * spans — required before a SPANS sequence (clip or stride) starts. */
static void canvas_reset(void)
{
    memcpy(s_canvas, s_plate_paper, FRAME_BYTES);
    for (int y = 0; y < FRAME_H; y++) {
        s_span_x1[y] = -1;
    }
}

/* ------------------------------------------------------------------ */
/* Embedded LAYER stills (EMBED_FILES). In seq2 these files hold the   */
/* bird-only layers under the seq1 filenames — the symbols are the     */
/* same, the content is layers now, composited at runtime.             */
/* ------------------------------------------------------------------ */
extern const uint8_t rest_jpg_start[] asm("_binary_rest_jpg_start");
extern const uint8_t rest_jpg_end[]   asm("_binary_rest_jpg_end");

/* Decode the rest LAYER, composite it on the current side, present.
 * This is the bird's still position between sequences. */
static void show_rest(void)
{
    if (decode_jpeg(rest_jpg_start, (size_t)(rest_jpg_end - rest_jpg_start),
                    s_pose_buf, s_pose_buf_size)) {
        comp_dual((const uint16_t *)s_pose_buf, JOB_FULL, s_mirrored, 0);
        present_frame(s_canvas);
    } else {
        ESP_LOGW(TAG, "rest layer decode failed — skipped");
    }
}

/* Put the bare marsh plate on screen (the bird is away, mid-flight). */
static void show_plate(void)
{
    present_frame(s_plate_buf);
}

/* Generic timing-table pose player: decode + full-composite only when
 * the schedule changes pose; held ticks repeat for free. Every pose
 * renders on the current side (flip = s_mirrored, dx = 0). */
static void play_table(const char *name, const uint8_t *const *starts,
                       const uint8_t *const *ends, const uint8_t *sched,
                       int nticks)
{
    ESP_LOGI(TAG, "%s start — %d ticks @ 12 fps, timing-table player (side: %s)",
             name, nticks, s_mirrored ? "right/mirrored" : "left");
    const TickType_t period = pdMS_TO_TICKS(1000) / 12;
    TickType_t last = xTaskGetTickCount();
    int cur_pose = -1;
    for (int t = 0; t < nticks; t++) {
        const int pose = sched[t];
        if (pose != cur_pose) {
            if (decode_jpeg(starts[pose], (size_t)(ends[pose] - starts[pose]),
                            s_pose_buf, s_pose_buf_size)) {
                comp_dual((const uint16_t *)s_pose_buf, JOB_FULL, s_mirrored, 0);
                present_frame(s_canvas);
                cur_pose = pose;
            } else {
                ESP_LOGW(TAG, "%s tick %d: pose %d decode failed — skipped", name, t, pose);
            }
        }
        vTaskDelayUntil(&last, period);
    }
}

/* ---- IDLE: 300 ticks / 25.0 s, 9 drawings + home (idle.md S.1a) ---- */
extern const uint8_t p1_blink_jpg_start[] asm("_binary_p1_blink_jpg_start");
extern const uint8_t p1_blink_jpg_end[]   asm("_binary_p1_blink_jpg_end");
extern const uint8_t p2_sacmid_jpg_start[] asm("_binary_p2_sacmid_jpg_start");
extern const uint8_t p2_sacmid_jpg_end[]   asm("_binary_p2_sacmid_jpg_end");
extern const uint8_t p3_sacr_jpg_start[] asm("_binary_p3_sacr_jpg_start");
extern const uint8_t p3_sacr_jpg_end[]   asm("_binary_p3_sacr_jpg_end");
extern const uint8_t p4_tiltmid_jpg_start[] asm("_binary_p4_tiltmid_jpg_start");
extern const uint8_t p4_tiltmid_jpg_end[]   asm("_binary_p4_tiltmid_jpg_end");
extern const uint8_t p5_tiltfull_jpg_start[] asm("_binary_p5_tiltfull_jpg_start");
extern const uint8_t p5_tiltfull_jpg_end[]   asm("_binary_p5_tiltfull_jpg_end");
extern const uint8_t p6_scan1_jpg_start[] asm("_binary_p6_scan1_jpg_start");
extern const uint8_t p6_scan1_jpg_end[]   asm("_binary_p6_scan1_jpg_end");
extern const uint8_t p7_scan2_jpg_start[] asm("_binary_p7_scan2_jpg_start");
extern const uint8_t p7_scan2_jpg_end[]   asm("_binary_p7_scan2_jpg_end");
extern const uint8_t p8_scan3_jpg_start[] asm("_binary_p8_scan3_jpg_start");
extern const uint8_t p8_scan3_jpg_end[]   asm("_binary_p8_scan3_jpg_end");
extern const uint8_t p9_scanend_jpg_start[] asm("_binary_p9_scanend_jpg_start");
extern const uint8_t p9_scanend_jpg_end[]   asm("_binary_p9_scanend_jpg_end");

static const uint8_t *const idle_pose_start[10] = {
    rest_jpg_start, p1_blink_jpg_start, p2_sacmid_jpg_start,
    p3_sacr_jpg_start, p4_tiltmid_jpg_start, p5_tiltfull_jpg_start,
    p6_scan1_jpg_start, p7_scan2_jpg_start, p8_scan3_jpg_start,
    p9_scanend_jpg_start,
};
static const uint8_t *const idle_pose_end[10] = {
    rest_jpg_end, p1_blink_jpg_end, p2_sacmid_jpg_end,
    p3_sacr_jpg_end, p4_tiltmid_jpg_end, p5_tiltfull_jpg_end,
    p6_scan1_jpg_end, p7_scan2_jpg_end, p8_scan3_jpg_end,
    p9_scanend_jpg_end,
};
static const uint8_t idle_sched[300] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 3, 3, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 7, 7, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

static void play_idle(void)
{
    play_table("idle", idle_pose_start, idle_pose_end, idle_sched, 300);
}

/* ---- STRETCH: 96 ticks / 8.0 s, 9 drawings + home (stretch.md) ----- */
extern const uint8_t q1_dep_jpg_start[] asm("_binary_q1_dep_jpg_start");
extern const uint8_t q1_dep_jpg_end[]   asm("_binary_q1_dep_jpg_end");
extern const uint8_t q2_weight_jpg_start[] asm("_binary_q2_weight_jpg_start");
extern const uint8_t q2_weight_jpg_end[]   asm("_binary_q2_weight_jpg_end");
extern const uint8_t q3_tucked_jpg_start[] asm("_binary_q3_tucked_jpg_start");
extern const uint8_t q3_tucked_jpg_end[]   asm("_binary_q3_tucked_jpg_end");
extern const uint8_t q4_fan1_jpg_start[] asm("_binary_q4_fan1_jpg_start");
extern const uint8_t q4_fan1_jpg_end[]   asm("_binary_q4_fan1_jpg_end");
extern const uint8_t q5_fan2_jpg_start[] asm("_binary_q5_fan2_jpg_start");
extern const uint8_t q5_fan2_jpg_end[]   asm("_binary_q5_fan2_jpg_end");
extern const uint8_t q6_fan3_jpg_start[] asm("_binary_q6_fan3_jpg_start");
extern const uint8_t q6_fan3_jpg_end[]   asm("_binary_q6_fan3_jpg_end");
extern const uint8_t q7_leg1_jpg_start[] asm("_binary_q7_leg1_jpg_start");
extern const uint8_t q7_leg1_jpg_end[]   asm("_binary_q7_leg1_jpg_end");
extern const uint8_t q8_leg2_jpg_start[] asm("_binary_q8_leg2_jpg_start");
extern const uint8_t q8_leg2_jpg_end[]   asm("_binary_q8_leg2_jpg_end");
extern const uint8_t q9_full_jpg_start[] asm("_binary_q9_full_jpg_start");
extern const uint8_t q9_full_jpg_end[]   asm("_binary_q9_full_jpg_end");

static const uint8_t *const stretch_pose_start[10] = {
    rest_jpg_start, q1_dep_jpg_start, q2_weight_jpg_start,
    q3_tucked_jpg_start, q4_fan1_jpg_start, q5_fan2_jpg_start,
    q6_fan3_jpg_start, q7_leg1_jpg_start, q8_leg2_jpg_start,
    q9_full_jpg_start,
};
static const uint8_t *const stretch_pose_end[10] = {
    rest_jpg_end, q1_dep_jpg_end, q2_weight_jpg_end,
    q3_tucked_jpg_end, q4_fan1_jpg_end, q5_fan2_jpg_end,
    q6_fan3_jpg_end, q7_leg1_jpg_end, q8_leg2_jpg_end,
    q9_full_jpg_end,
};
static const uint8_t stretch_sched[96] = { 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 8, 8, 8, 7, 7, 7, 6, 6, 6, 5, 5, 5, 4, 4, 4, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0 };

static void play_stretch(void)
{
    play_table("stretch", stretch_pose_start, stretch_pose_end, stretch_sched, 96);
}

/* ---- PREEN: 132 ticks / 11.0 s, 9 drawings + home (preen.md) ------ */
/* Pose 7 (the wing bout) plays on stretch's FAN_2 blob — Jimmy's      */
/* approved fallback; no duplicate storage.                            */
extern const uint8_t r1_depmid_jpg_start[] asm("_binary_r1_depmid_jpg_start");
extern const uint8_t r1_depmid_jpg_end[]   asm("_binary_r1_depmid_jpg_end");
extern const uint8_t r2_glance_jpg_start[] asm("_binary_r2_glance_jpg_start");
extern const uint8_t r2_glance_jpg_end[]   asm("_binary_r2_glance_jpg_end");
extern const uint8_t r3_shoulder_jpg_start[] asm("_binary_r3_shoulder_jpg_start");
extern const uint8_t r3_shoulder_jpg_end[]   asm("_binary_r3_shoulder_jpg_end");
extern const uint8_t r4_nibble_jpg_start[] asm("_binary_r4_nibble_jpg_start");
extern const uint8_t r4_nibble_jpg_end[]   asm("_binary_r4_nibble_jpg_end");
extern const uint8_t r5_draw_jpg_start[] asm("_binary_r5_draw_jpg_start");
extern const uint8_t r5_draw_jpg_end[]   asm("_binary_r5_draw_jpg_end");
extern const uint8_t r6_chest_jpg_start[] asm("_binary_r6_chest_jpg_start");
extern const uint8_t r6_chest_jpg_end[]   asm("_binary_r6_chest_jpg_end");
extern const uint8_t r7_shake_jpg_start[] asm("_binary_r7_shake_jpg_start");
extern const uint8_t r7_shake_jpg_end[]   asm("_binary_r7_shake_jpg_end");
extern const uint8_t r8_settle_jpg_start[] asm("_binary_r8_settle_jpg_start");
extern const uint8_t r8_settle_jpg_end[]   asm("_binary_r8_settle_jpg_end");

static const uint8_t *const preen_pose_start[10] = {
    rest_jpg_start, r1_depmid_jpg_start, r2_glance_jpg_start,
    r3_shoulder_jpg_start, r4_nibble_jpg_start, r5_draw_jpg_start,
    r6_chest_jpg_start, q5_fan2_jpg_start, r7_shake_jpg_start,
    r8_settle_jpg_start,
};
static const uint8_t *const preen_pose_end[10] = {
    rest_jpg_end, r1_depmid_jpg_end, r2_glance_jpg_end,
    r3_shoulder_jpg_end, r4_nibble_jpg_end, r5_draw_jpg_end,
    r6_chest_jpg_end, q5_fan2_jpg_end, r7_shake_jpg_end,
    r8_settle_jpg_end,
};
static const uint8_t preen_sched[132] = { 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 3, 3, 3, 2, 2, 2, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 7, 8, 7, 8, 7, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

static void play_preen(void)
{
    play_table("preen", preen_pose_start, preen_pose_end, preen_sched, 132);
}

/* ---- LISTENING: 252 ticks / 21.0 s, 3 drawings + home -------------- */
/* Rise 36, the pose held on its single frame 180 ticks (exactly       */
/* 15.0 s), settle 36 back down the same grades (Jimmy's design).      */
extern const uint8_t s1_rise0_jpg_start[] asm("_binary_s1_rise0_jpg_start");
extern const uint8_t s1_rise0_jpg_end[]   asm("_binary_s1_rise0_jpg_end");
extern const uint8_t s2_rise1_jpg_start[] asm("_binary_s2_rise1_jpg_start");
extern const uint8_t s2_rise1_jpg_end[]   asm("_binary_s2_rise1_jpg_end");
extern const uint8_t s3_pose_jpg_start[]  asm("_binary_s3_pose_jpg_start");
extern const uint8_t s3_pose_jpg_end[]    asm("_binary_s3_pose_jpg_end");

static const uint8_t *const listen_pose_start[4] = {
    rest_jpg_start, s1_rise0_jpg_start, s2_rise1_jpg_start, s3_pose_jpg_start,
};
static const uint8_t *const listen_pose_end[4] = {
    rest_jpg_end, s1_rise0_jpg_end, s2_rise1_jpg_end, s3_pose_jpg_end,
};
static const uint8_t listen_sched[252] = { 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

static void play_listening(void)
{
    play_table("listening", listen_pose_start, listen_pose_end, listen_sched, 252);
}

/* ------------------------------------------------------------------ */
/* Layer-clip player (bench V6/V8 pipeline): a decode task on core 1   */
/* fills the two bird buffers ahead of the composite; the caller       */
/* span-composites each decoded layer on the current side, presents    */
/* the persistent canvas, and paces to 12 fps with vTaskDelayUntil.    */
/* ------------------------------------------------------------------ */
static QueueHandle_t s_ready_q;
static QueueHandle_t s_free_q;
static volatile bool s_dec_stop;
static const uint8_t *s_dec_start;
static const uint8_t *s_dec_end;

typedef struct { const uint8_t *cursor; const uint8_t *end; } frame_iter_t;

static bool decode_next(frame_iter_t *it, uint8_t *buf, size_t buf_size)
{
    const uint8_t *soi = scan_to_marker(it->cursor, it->end, 0xD8);
    if (soi == NULL) return false;
    const uint8_t *eoi = scan_to_marker(soi + 2, it->end, 0xD9);
    if (eoi == NULL) return false;
    const size_t flen = (size_t)(eoi + 2 - soi);
    it->cursor = eoi + 2;
    if (flen > IN_BUF_BYTES) return false;
    memcpy(s_in_buf, soi, flen);
    uint32_t out_size = 0;
    return jpeg_decoder_process(s_decoder, &s_decode_cfg, s_in_buf, flen,
                                buf, (uint32_t)buf_size, &out_size) == ESP_OK;
}

static void decode_task(void *arg)
{
    (void)arg;
    frame_iter_t it = { s_dec_start, s_dec_end };
    while (!s_dec_stop) {
        int slot;
        if (xQueueReceive(s_free_q, &slot, pdMS_TO_TICKS(100)) != pdTRUE) {
            continue;
        }
        if (!decode_next(&it, s_bird_buf[slot], s_bird_buf_size[slot])) {
            break; /* blob exhausted */
        }
        xQueueSend(s_ready_q, &slot, portMAX_DELAY);
    }
    vTaskDelete(NULL);
}

static void play_layer_clip(const char *name, const uint8_t *start, const uint8_t *end)
{
    ESP_LOGI(TAG, "clip start: %s — layer stream, side: %s", name,
             s_mirrored ? "right/mirrored" : "left");
    canvas_reset();

    s_ready_q = xQueueCreate(2, sizeof(int));
    s_free_q = xQueueCreate(2, sizeof(int));
    int s0 = 0, s1 = 1;
    xQueueSend(s_free_q, &s0, 0);
    xQueueSend(s_free_q, &s1, 0);
    s_dec_start = start;
    s_dec_end = end;
    s_dec_stop = false;
    xTaskCreatePinnedToCore(decode_task, "seq2_dec", 4096, NULL, 6, NULL, 1);

    const TickType_t period = pdMS_TO_TICKS(1000) / 12;
    TickType_t last = xTaskGetTickCount();
    int frames = 0, busts = 0;
    int64_t t_start = 0, prev_done = 0, max_gap = 0;
    while (1) {
        int slot;
        if (xQueueReceive(s_ready_q, &slot, pdMS_TO_TICKS(500)) != pdTRUE) {
            break;
        }
        if (frames == 0) {
            t_start = esp_timer_get_time();
            prev_done = t_start;
        }
        comp_dual((const uint16_t *)s_bird_buf[slot], JOB_SPANS, s_mirrored, 0);
        present_frame(s_canvas);
        const int64_t now = esp_timer_get_time();
        const int64_t gap = now - prev_done;
        if (frames > 0 && gap > max_gap) max_gap = gap;
        if (frames > 0 && gap > 83333) busts++;
        prev_done = now;
        frames++;
        xQueueSend(s_free_q, &slot, 0);
        vTaskDelayUntil(&last, period);
    }
    const int64_t wall = frames ? (prev_done - t_start) : 0;
    s_dec_stop = true;
    vTaskDelay(pdMS_TO_TICKS(150));
    vQueueDelete(s_ready_q);
    vQueueDelete(s_free_q);
    ESP_LOGI(TAG, "clip done: %s — %d frames, avg %lu us/frame, worst gap %lu us, gaps over 83.3 ms: %d",
             name, frames,
             frames ? (unsigned long)(wall / frames) : 0UL,
             (unsigned long)max_gap, busts);
}

static void play_strike(void)
{
    if (!s_assets_ok) {
        ESP_LOGW(TAG, "strike skipped — assets unavailable");
        return;
    }
    esp_partition_mmap_handle_t h;
    const uint8_t *p = asset_map(ASSET_STRIKE, &h);
    if (p == NULL) return;
    play_layer_clip("strike (60 frames)", p, p + s_asset_len[ASSET_STRIKE]);
    esp_partition_munmap(h);
}

/* The flight pair: OUT -> 30 s of empty marsh -> HOME. From the right
 * side both clips play mirrored (out exits left, home enters from the
 * right) — the bird always lands on the side it started from. */
static void play_flight(void)
{
    if (!s_assets_ok) {
        ESP_LOGW(TAG, "flight skipped — assets unavailable");
        return;
    }
    esp_partition_mmap_handle_t h;
    const uint8_t *p = asset_map(ASSET_FLIGHT_OUT, &h);
    if (p == NULL) return;
    play_layer_clip("flight OUT (36 frames)", p, p + s_asset_len[ASSET_FLIGHT_OUT]);
    esp_partition_munmap(h);

    show_plate();
    ESP_LOGI(TAG, "flight: bird away — holding the empty marsh %d ms", FLIGHT_GAP_MS);
    vTaskDelay(pdMS_TO_TICKS(FLIGHT_GAP_MS));

    p = asset_map(ASSET_FLIGHT_HOME, &h);
    if (p == NULL) return;
    play_layer_clip("flight HOME (53 frames)", p, p + s_asset_len[ASSET_FLIGHT_HOME]);
    esp_partition_munmap(h);
}

/* ------------------------------------------------------------------ */
/* STRIDE — the side-changer.                                          */
/*                                                                     */
/* REDO 2026-11-06 (Jimmy's verdict on v1: "unnatural, like he is      */
/* dragging his feet" — v1 slid whole poses at progressive dx, so      */
/* planted feet slid through the water). The redo follows the          */
/* measured step cycle in sequences/choreography/stride.md: per step,  */
/* the root stays still through fold / advance / toe-first plant, and  */
/* travel happens only in the body pass, with the planted foot         */
/* WORLD-PINNED (poses are foot-anchored at registration; dx changes   */
/* only at pass boundaries, by reach*k, k=0.960 — per-pass pin error   */
/* ~3 device px) and the head held world-locked (pass poses drawn      */
/* with the head in place, K6). 9 full steps + a short closing step    */
/* land the feet on the mirrored home stance (~1 canvas px), then     */
/* the drawn turn + sink, as before.                                   */
/*                                                                     */
/* Poses: 0=HOME(rest) 1=D1 half-rise 2=D2 carriage 3=WA fold (near)  */
/* 4=ADV_N 5=PLANT_N 6=PASS1_N 7=PASS2_N (= far fold, body passed)     */
/* 8=ADV_F 9=PLANT_F 10=PASS1_F 11=PASS2_F (= near fold, body passed)  */
/* 12=PLANT_F_SHORT (closing step) 13=T1 14=T2 15=T3 16=T4 17=T5.      */
/*                                                                     */
/* The schedule is a baked run-length table (stride_sched.inc,        */
/* generated from sequences/stride/stride2_preview.py — the preview   */
/* Jimmy approved). The composite's flip flag is the side the bird     */
/* starts on, so the SAME table walks it back the other way next       */
/* time. At the settle, s_mirrored toggles and show_rest draws the     */
/* new side's home.                                                    */
/* ------------------------------------------------------------------ */
extern const uint8_t z_d1_halfrise_jpg_start[] asm("_binary_z_d1_halfrise_jpg_start");
extern const uint8_t z_d1_halfrise_jpg_end[]   asm("_binary_z_d1_halfrise_jpg_end");
extern const uint8_t z_d2_carriage_jpg_start[] asm("_binary_z_d2_carriage_jpg_start");
extern const uint8_t z_d2_carriage_jpg_end[]   asm("_binary_z_d2_carriage_jpg_end");
extern const uint8_t z_wa_swing_jpg_start[] asm("_binary_z_wa_swing_jpg_start");
extern const uint8_t z_wa_swing_jpg_end[]   asm("_binary_z_wa_swing_jpg_end");
extern const uint8_t z_adv_near_jpg_start[] asm("_binary_z_adv_near_jpg_start");
extern const uint8_t z_adv_near_jpg_end[]   asm("_binary_z_adv_near_jpg_end");
extern const uint8_t z_plant_near_jpg_start[] asm("_binary_z_plant_near_jpg_start");
extern const uint8_t z_plant_near_jpg_end[]   asm("_binary_z_plant_near_jpg_end");
extern const uint8_t z_pass1_near_jpg_start[] asm("_binary_z_pass1_near_jpg_start");
extern const uint8_t z_pass1_near_jpg_end[]   asm("_binary_z_pass1_near_jpg_end");
extern const uint8_t z_pass2_near_jpg_start[] asm("_binary_z_pass2_near_jpg_start");
extern const uint8_t z_pass2_near_jpg_end[]   asm("_binary_z_pass2_near_jpg_end");
extern const uint8_t z_adv_far_jpg_start[] asm("_binary_z_adv_far_jpg_start");
extern const uint8_t z_adv_far_jpg_end[]   asm("_binary_z_adv_far_jpg_end");
extern const uint8_t z_plant_far_jpg_start[] asm("_binary_z_plant_far_jpg_start");
extern const uint8_t z_plant_far_jpg_end[]   asm("_binary_z_plant_far_jpg_end");
extern const uint8_t z_pass1_far_jpg_start[] asm("_binary_z_pass1_far_jpg_start");
extern const uint8_t z_pass1_far_jpg_end[]   asm("_binary_z_pass1_far_jpg_end");
extern const uint8_t z_pass2_far_jpg_start[] asm("_binary_z_pass2_far_jpg_start");
extern const uint8_t z_pass2_far_jpg_end[]   asm("_binary_z_pass2_far_jpg_end");
extern const uint8_t z_plant_far_short_jpg_start[] asm("_binary_z_plant_far_short_jpg_start");
extern const uint8_t z_plant_far_short_jpg_end[]   asm("_binary_z_plant_far_short_jpg_end");
extern const uint8_t z_t1_turn_jpg_start[] asm("_binary_z_t1_turn_jpg_start");
extern const uint8_t z_t1_turn_jpg_end[]   asm("_binary_z_t1_turn_jpg_end");
extern const uint8_t z_t2_frontal_jpg_start[] asm("_binary_z_t2_frontal_jpg_start");
extern const uint8_t z_t2_frontal_jpg_end[]   asm("_binary_z_t2_frontal_jpg_end");
extern const uint8_t z_t3_turn_jpg_start[] asm("_binary_z_t3_turn_jpg_start");
extern const uint8_t z_t3_turn_jpg_end[]   asm("_binary_z_t3_turn_jpg_end");
extern const uint8_t z_t4_left_jpg_start[] asm("_binary_z_t4_left_jpg_start");
extern const uint8_t z_t4_left_jpg_end[]   asm("_binary_z_t4_left_jpg_end");
extern const uint8_t z_t5_sink_jpg_start[] asm("_binary_z_t5_sink_jpg_start");
extern const uint8_t z_t5_sink_jpg_end[]   asm("_binary_z_t5_sink_jpg_end");

static const uint8_t *const stride_pose_start[18] = {
    rest_jpg_start, z_d1_halfrise_jpg_start, z_d2_carriage_jpg_start,
    z_wa_swing_jpg_start, z_adv_near_jpg_start, z_plant_near_jpg_start,
    z_pass1_near_jpg_start, z_pass2_near_jpg_start, z_adv_far_jpg_start,
    z_plant_far_jpg_start, z_pass1_far_jpg_start, z_pass2_far_jpg_start,
    z_plant_far_short_jpg_start, z_t1_turn_jpg_start, z_t2_frontal_jpg_start,
    z_t3_turn_jpg_start, z_t4_left_jpg_start, z_t5_sink_jpg_start,
};
static const uint8_t *const stride_pose_end[18] = {
    rest_jpg_end, z_d1_halfrise_jpg_end, z_d2_carriage_jpg_end,
    z_wa_swing_jpg_end, z_adv_near_jpg_end, z_plant_near_jpg_end,
    z_pass1_near_jpg_end, z_pass2_near_jpg_end, z_adv_far_jpg_end,
    z_plant_far_jpg_end, z_pass1_far_jpg_end, z_pass2_far_jpg_end,
    z_plant_far_short_jpg_end, z_t1_turn_jpg_end, z_t2_frontal_jpg_end,
    z_t3_turn_jpg_end, z_t4_left_jpg_end, z_t5_sink_jpg_end,
};

typedef struct { uint8_t pose; uint8_t ticks; int16_t dx; } stride_run_t;
#include "stride_sched.inc"

#define STRIDE_MAX_TICKS 176
static uint8_t s_stride_pose[STRIDE_MAX_TICKS];
static int16_t s_stride_dx[STRIDE_MAX_TICKS];

static int stride_build_schedule(void)
{
    int n = 0;
    for (int r = 0; r < STRIDE_NUM_RUNS; r++) {
        for (int k = 0; k < STRIDE_RUNS[r].ticks; k++) {
            s_stride_pose[n] = STRIDE_RUNS[r].pose;
            s_stride_dx[n] = STRIDE_RUNS[r].dx;
            n++;
        }
    }
    return n;
}

static void play_stride(void)
{
    const bool from_mirrored = s_mirrored;
    const int nticks = stride_build_schedule();
    ESP_LOGI(TAG, "stride start — crossing %s -> %s, %d ticks @ 12 fps",
             from_mirrored ? "right" : "left", from_mirrored ? "left" : "right", nticks);
    canvas_reset();
    const TickType_t period = pdMS_TO_TICKS(1000) / 12;
    TickType_t last = xTaskGetTickCount();
    int cur_pose = -1;
    for (int t = 0; t < nticks; t++) {
        const int pose = s_stride_pose[t];
        if (pose != cur_pose) {
            if (decode_jpeg(stride_pose_start[pose],
                            (size_t)(stride_pose_end[pose] - stride_pose_start[pose]),
                            s_bird_buf[0], s_bird_buf_size[0])) {
                cur_pose = pose;
            } else {
                ESP_LOGW(TAG, "stride tick %d: pose %d decode failed — skipped", t, pose);
            }
        }
        if (cur_pose >= 0) {
            comp_dual((const uint16_t *)s_bird_buf[0], JOB_SPANS, from_mirrored, s_stride_dx[t]);
            present_frame(s_canvas);
        }
        vTaskDelayUntil(&last, period);
    }
    s_mirrored = !from_mirrored;
    ESP_LOGI(TAG, "stride done — bird now on the %s side", s_mirrored ? "right" : "left");
}

/* ------------------------------------------------------------------ */
/* Playback: shuffle-bag with the 50% stride rule (Jimmy, 2026-11-06). */
/* ------------------------------------------------------------------ */
typedef void (*behavior_fn_t)(void);
enum { B_STRIKE = 0, B_IDLE, B_STRETCH, B_PREEN, B_FLIGHT, B_LISTENING,
       B_STRIDE, B_COUNT };
static const struct { const char *name; behavior_fn_t fn; } s_behaviors[B_COUNT] = {
    { "strike",    play_strike },
    { "idle",      play_idle },
    { "stretch",   play_stretch },
    { "preen",     play_preen },
    { "flight",    play_flight },
    { "listening", play_listening },
    { "stride",    play_stride },
};

static void player_task(void *arg)
{
    (void)arg;
    vTaskDelay(pdMS_TO_TICKS(1500));

    uint32_t bag_no = 0;
    int prev_last = -1;
    while (1) {
        /* The stride coin flip: half of all bags include stride. */
        const bool with_stride = (esp_random() & 1u) != 0;
        int ids[B_COUNT];
        int n = 0;
        for (int i = 0; i < B_COUNT; i++) {
            if (i == B_STRIDE && !with_stride) continue;
            ids[n++] = i;
        }
        for (int i = n - 1; i > 0; i--) {
            const int j = (int)(esp_random() % (uint32_t)(i + 1));
            const int tmp = ids[i]; ids[i] = ids[j]; ids[j] = tmp;
        }
        if (prev_last >= 0 && ids[0] == prev_last) {
            const int j = 1 + (int)(esp_random() % (uint32_t)(n - 1));
            const int tmp = ids[0]; ids[0] = ids[j]; ids[j] = tmp;
        }
        bag_no++;
        char names[160];
        int off = 0;
        for (int i = 0; i < n; i++) {
            off += snprintf(names + off, sizeof(names) - (size_t)off, "%s%s",
                            i ? ", " : "", s_behaviors[ids[i]].name);
        }
        ESP_LOGI(TAG, "shuffle bag %lu (%d behaviors, stride %s, bird on %s): %s",
                 (unsigned long)bag_no, n, with_stride ? "IN" : "out",
                 s_mirrored ? "right" : "left", names);
        for (int k = 0; k < n; k++) {
            const int b = ids[k];
            s_behaviors[b].fn();
            show_rest();
            ESP_LOGI(TAG, "%s done (bag %lu, %d of %d) — resting %d ms",
                     s_behaviors[b].name, (unsigned long)bag_no, k + 1, n, REST_HOLD_MS);
            vTaskDelay(pdMS_TO_TICKS(REST_HOLD_MS));
        }
        prev_last = ids[n - 1];
    }
}

void app_main(void)
{
    ESP_LOGI(TAG, "heron — SEQUENCE 2 player (layers + flip-in-code + stride)");

    lv_display_t *disp = bsp_display_start();
    if (disp == NULL) {
        ESP_LOGE(TAG, "bsp_display_start() failed — no display");
        return;
    }
    ESP_ERROR_CHECK(bsp_display_brightness_set(100));

    bsp_display_lock(0);
    lv_obj_t *scr = lv_screen_active();
    lv_obj_remove_flag(scr, LV_OBJ_FLAG_SCROLLABLE);
    s_img = lv_image_create(scr);
    lv_image_set_src(s_img, &alert_plate_img);
    lv_obj_set_pos(s_img, 0, 0);
    lv_obj_remove_flag(s_img, LV_OBJ_FLAG_SCROLLABLE);
    bsp_display_unlock();

    jpeg_decode_engine_cfg_t eng_cfg = {
        .intr_priority = 0,
        .timeout_ms = 100,
    };
    esp_err_t err = jpeg_new_decoder_engine(&eng_cfg, &s_decoder);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "jpeg_new_decoder_engine: %s — staying on the still plate",
                 esp_err_to_name(err));
        while (1) { vTaskDelay(pdMS_TO_TICKS(1000)); }
    }

    jpeg_decode_memory_alloc_cfg_t in_alloc_cfg = {
        .buffer_direction = JPEG_DEC_ALLOC_INPUT_BUFFER,
    };
    jpeg_decode_memory_alloc_cfg_t out_alloc_cfg = {
        .buffer_direction = JPEG_DEC_ALLOC_OUTPUT_BUFFER,
    };
    size_t in_size = 0;
    s_in_buf = jpeg_alloc_decoder_mem(IN_BUF_BYTES, &in_alloc_cfg, &in_size);
    s_bird_buf[0] = jpeg_alloc_decoder_mem(OUT_BUF_BYTES, &out_alloc_cfg, &s_bird_buf_size[0]);
    s_bird_buf[1] = jpeg_alloc_decoder_mem(OUT_BUF_BYTES, &out_alloc_cfg, &s_bird_buf_size[1]);
    s_pose_buf = jpeg_alloc_decoder_mem(OUT_BUF_BYTES, &out_alloc_cfg, &s_pose_buf_size);
    s_canvas = jpeg_alloc_decoder_mem(OUT_BUF_BYTES, &out_alloc_cfg, &s_canvas_size);
    s_plate_buf = jpeg_alloc_decoder_mem(OUT_BUF_BYTES, &out_alloc_cfg, &in_size);
    s_plate_paper = jpeg_alloc_decoder_mem(OUT_BUF_BYTES, &out_alloc_cfg, &in_size);
    if (s_in_buf == NULL || s_bird_buf[0] == NULL || s_bird_buf[1] == NULL ||
        s_pose_buf == NULL || s_canvas == NULL || s_plate_buf == NULL ||
        s_plate_paper == NULL) {
        ESP_LOGE(TAG, "decoder buffer allocation failed — staying on the still plate");
        while (1) { vTaskDelay(pdMS_TO_TICKS(1000)); }
    }
    ESP_LOGI(TAG, "buffers ready (bird x2, pose, canvas, plate, plate_paper)");

    build_tables();
    s_assets_ok = assets_init();

    /* Decode the plate once; build plate_paper = plate x paper (the
     * background of every shipped composite) and seed the canvas. */
    bool plate_ok = false;
    if (s_assets_ok) {
        esp_partition_mmap_handle_t h;
        const uint8_t *p = asset_map(ASSET_PLATE, &h);
        if (p != NULL) {
            plate_ok = decode_jpeg(p, s_asset_len[ASSET_PLATE], s_plate_buf, OUT_BUF_BYTES);
            esp_partition_munmap(h);
        }
    }
    if (!plate_ok) {
        ESP_LOGE(TAG, "plate decode failed — cannot composite; staying on the boot plate");
        while (1) { vTaskDelay(pdMS_TO_TICKS(1000)); }
    }
    {
        const uint16_t *plate = (const uint16_t *)s_plate_buf;
        uint16_t *paper = (uint16_t *)s_plate_paper;
        for (int i = 0; i < FRAME_W * FRAME_H; i++) {
            paper[i] = mul_px(plate[i], PAPER565);
        }
    }
    canvas_reset();

    s_comp_stop = false;
    xTaskCreatePinnedToCore(comp_worker_task, "seq2_hi", 4096, NULL, 6,
                            &s_comp_worker, 1);

    show_rest();
    ESP_LOGI(TAG, "home frame composited live from the rest layer + plate");

    xTaskCreate(player_task, "heron_player", 12288, NULL, 5, NULL);
    ESP_LOGI(TAG, "player task running — seq2 is live");
}
