/*
 * heron — SPAN COMPOSITE BENCH v7 (pipelined, strike layers) (2026-11-05, Jimmy: "composite only
 * the bird's bounding box and benchmark").
 *
 * The bird's bounding box was measured offline from the 60 bird-layer
 * frames (ink = any channel >= 18 below paper, union over all frames,
 * device px): x 24..842, y 106..585 = 64.0% of the frame; per-frame
 * boxes are 59.7-64.0% (the strike's reach sets the union). All
 * variants composite FLIPPED (the two-side case); the flipped box is
 * x 181..999, same y.
 *
 *   V4  Fresh canvas per frame: bbox = LUT multiply; outside the box
 *       the plate is copied verbatim (no bird read outside the box).
 *   V5  Persistent canvas: at boot the canvas is filled with frame 0's
 *       full composite; per frame ONLY the bbox region is recomputed
 *       in place — the exterior costs zero traffic after boot.
 *   V6  V5 + pipelined decode: a decode task fills two bird buffers
 *       ahead while the composite task works — throughput per frame
 *       is what counts (wall time / frames + worst frame gap).
 *
 * Reference (bench v2): full-frame LUT composite 76 ms, decode 8.4 ms.
 */
#include <stddef.h>
#include <stdint.h>
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

static const char *TAG = "heron_bench3";

extern const uint8_t bird_mjpeg_start[] asm("_binary_bird_mjpeg_start");
extern const uint8_t bird_mjpeg_end[] asm("_binary_bird_mjpeg_end");
extern const uint8_t plate_jpg_start[] asm("_binary_plate_jpg_start");
extern const uint8_t plate_jpg_end[] asm("_binary_plate_jpg_end");

#define FRAME_W        1024
#define FRAME_H        600
#define FRAME_STRIDE   (FRAME_W * 2)
#define FRAME_BYTES    (FRAME_W * FRAME_H * 2)
#define OUT_BUF_BYTES  (FRAME_BYTES + 256 * 1024)
#define IN_BUF_BYTES   (128 * 1024)
#define BUDGET_US      83333

/* Bird bbox (unflipped source coordinates), measured offline. */
#define BB_X0 24
#define BB_X1 842
#define BB_Y0 106
#define BB_Y1 585

static lv_obj_t *s_img;
static jpeg_decoder_handle_t s_decoder;
static uint8_t *s_in_buf;
static uint8_t *s_out_buf[2];
static size_t s_out_buf_size[2];
static uint8_t *s_bird_buf[2];
static size_t s_bird_buf_size[2];
static uint8_t *s_plate_buf;

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

/* ---- LUT multiply (as bench v2) ----------------------------------- */
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

/* Composite rows [y0,y1) over the full width, flipped source. */
static void comp_rows_flip(const uint16_t *bird, const uint16_t *plate, uint16_t *dst,
                           int y0, int y1)
{
    for (int y = y0; y < y1; y++) {
        const uint16_t *brow = bird + (size_t)y * FRAME_W;
        const uint16_t *prow = plate + (size_t)y * FRAME_W;
        uint16_t *drow = dst + (size_t)y * FRAME_W;
        for (int x = 0; x < FRAME_W; x++) {
            drow[x] = mul_px(brow[FRAME_W - 1 - x], prow[x]);
        }
    }
}

/* Composite ONLY the flipped bbox region into dst (dst elsewhere is
 * the caller's business). Flipped dst box: x in [W-1-BB_X1, W-1-BB_X0]. */
static void comp_bbox_flip(const uint16_t *bird, const uint16_t *plate, uint16_t *dst)
{
    const int dx0 = FRAME_W - 1 - BB_X1;
    const int dx1 = FRAME_W - 1 - BB_X0;
    for (int y = BB_Y0; y <= BB_Y1; y++) {
        const uint16_t *brow = bird + (size_t)y * FRAME_W;
        const uint16_t *prow = plate + (size_t)y * FRAME_W;
        uint16_t *drow = dst + (size_t)y * FRAME_W;
        for (int x = dx0; x <= dx1; x++) {
            drow[x] = mul_px(brow[FRAME_W - 1 - x], prow[x]);
        }
    }
}

/* V4 exterior: copy the plate everywhere outside the flipped bbox. */
static void fill_exterior_plate(const uint16_t *plate, uint16_t *dst)
{
    const int dx0 = FRAME_W - 1 - BB_X1;
    const int dx1 = FRAME_W - 1 - BB_X0;
    for (int y = 0; y < FRAME_H; y++) {
        const uint16_t *prow = plate + (size_t)y * FRAME_W;
        uint16_t *drow = dst + (size_t)y * FRAME_W;
        if (y < BB_Y0 || y > BB_Y1) {
            memcpy(drow, prow, FRAME_STRIDE);
        } else {
            memcpy(drow, prow, (size_t)dx0 * 2);
            memcpy(drow + dx1 + 1, prow + dx1 + 1, (size_t)(FRAME_W - 1 - dx1) * 2);
        }
    }
}

/* ---- frame iteration helpers -------------------------------------- */
static const jpeg_decode_cfg_t s_decode_cfg = {
    .output_format = JPEG_DECODE_OUT_FORMAT_RGB565,
    .rgb_order = JPEG_DEC_RGB_ELEMENT_ORDER_BGR,
};

/* Decode frame idx from the blob into buf. Returns false at the end. */
static bool decode_frame_at(const uint8_t *cursor_start, int want, uint8_t *buf, size_t buf_size)
{
    const uint8_t *cursor = cursor_start;
    int idx = 0;
    while (cursor < bird_mjpeg_end) {
        const uint8_t *soi = scan_to_marker(cursor, bird_mjpeg_end, 0xD8);
        if (soi == NULL) return false;
        const uint8_t *eoi = scan_to_marker(soi + 2, bird_mjpeg_end, 0xD9);
        if (eoi == NULL) return false;
        const size_t flen = (size_t)(eoi + 2 - soi);
        cursor = eoi + 2;
        if (idx == want) {
            memcpy(s_in_buf, soi, flen);
            uint32_t out_size = 0;
            return jpeg_decoder_process(s_decoder, &s_decode_cfg, s_in_buf, flen,
                                        buf, (uint32_t)buf_size, &out_size) == ESP_OK;
        }
        idx++;
    }
    return false;
}

typedef struct {
    const uint8_t *cursor;
} frame_iter_t;

/* Decode the next frame from the iterator into buf. */
static bool decode_next(frame_iter_t *it, uint8_t *buf, size_t buf_size)
{
    const uint8_t *soi = scan_to_marker(it->cursor, bird_mjpeg_end, 0xD8);
    if (soi == NULL) return false;
    const uint8_t *eoi = scan_to_marker(soi + 2, bird_mjpeg_end, 0xD9);
    if (eoi == NULL) return false;
    const size_t flen = (size_t)(eoi + 2 - soi);
    it->cursor = eoi + 2;
    memcpy(s_in_buf, soi, flen);
    uint32_t out_size = 0;
    return jpeg_decoder_process(s_decoder, &s_decode_cfg, s_in_buf, flen,
                                buf, (uint32_t)buf_size, &out_size) == ESP_OK;
}

/* ---- V4 / V5 serial variants --------------------------------------- */
static void run_serial(const char *name, bool persistent_canvas)
{
    uint16_t *canvas = (uint16_t *)s_out_buf[0];
    uint16_t *birdbuf = (uint16_t *)s_out_buf[1];
    if (persistent_canvas) {
        /* Boot fill: frame 0's full composite becomes the canvas. */
        if (!decode_frame_at(bird_mjpeg_start, 0, s_out_buf[1], s_out_buf_size[1])) {
            ESP_LOGE(TAG, "%s: frame 0 decode failed", name);
            return;
        }
        comp_rows_flip(birdbuf, (const uint16_t *)s_plate_buf, canvas, 0, FRAME_H);
    }
    for (int pass = 0; pass < 2; pass++) {
        uint64_t sum_dec = 0, sum_comp = 0, sum_tot = 0, max_tot = 0;
        int busts = 0, frames = 0;
        frame_iter_t it = { bird_mjpeg_start };
        while (1) {
            const int64_t t0 = esp_timer_get_time();
            if (!decode_next(&it, s_out_buf[1], s_out_buf_size[1])) break;
            const int64_t t1 = esp_timer_get_time();
            if (!persistent_canvas) {
                fill_exterior_plate((const uint16_t *)s_plate_buf, canvas);
            }
            comp_bbox_flip(birdbuf, (const uint16_t *)s_plate_buf, canvas);
            const int64_t t2 = esp_timer_get_time();
            sum_dec += (uint64_t)(t1 - t0);
            sum_comp += (uint64_t)(t2 - t1);
            sum_tot += (uint64_t)(t2 - t0);
            if ((uint64_t)(t2 - t0) > max_tot) max_tot = (uint64_t)(t2 - t0);
            if ((t2 - t0) > BUDGET_US) busts++;
            frames++;
            present_frame((uint8_t *)canvas);
        }
        ESP_LOGI(TAG, "BENCH3 %s pass %d: frames %d | decode avg %lu us | comp avg %lu us | TOTAL avg %lu us, max %lu us | over 83.3 ms: %d",
                 name, pass, frames,
                 (unsigned long)(sum_dec / (uint64_t)frames),
                 (unsigned long)(sum_comp / (uint64_t)frames),
                 (unsigned long)(sum_tot / (uint64_t)frames),
                 (unsigned long)max_tot, busts);
    }
}

/* ---- V6 pipelined ---------------------------------------------------- */
static QueueHandle_t s_ready_q;   /* bird buffer indices ready to composite */
static QueueHandle_t s_free_q;    /* bird buffer indices free to decode into */
static volatile bool s_v6_stop;

static void decode_task(void *arg)
{
    (void)arg;
    frame_iter_t it = { bird_mjpeg_start };
    while (!s_v6_stop) {
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

static void run_v6(void)
{
    uint16_t *canvas = (uint16_t *)s_out_buf[0];
    /* Boot fill (serial, frame 0). */
    if (!decode_frame_at(bird_mjpeg_start, 0, s_out_buf[1], s_out_buf_size[1])) {
        ESP_LOGE(TAG, "V6: frame 0 decode failed");
        return;
    }
    comp_rows_flip((const uint16_t *)s_out_buf[1], (const uint16_t *)s_plate_buf,
                   canvas, 0, FRAME_H);

    for (int pass = 0; pass < 2; pass++) {
        s_ready_q = xQueueCreate(2, sizeof(int));
        s_free_q = xQueueCreate(2, sizeof(int));
        int s0 = 0, s1 = 1;
        xQueueSend(s_free_q, &s0, 0);
        xQueueSend(s_free_q, &s1, 0);
        s_v6_stop = false;
        xTaskCreatePinnedToCore(decode_task, "bench3_dec", 4096, NULL, 6, NULL, 1);

        int frames = 0, busts = 0;
        int64_t pass_start = 0, prev_done = 0, max_gap = 0;
        while (frames < 60) {
            int slot;
            if (xQueueReceive(s_ready_q, &slot, pdMS_TO_TICKS(500)) != pdTRUE) {
                break;
            }
            if (frames == 0) {
                pass_start = esp_timer_get_time();
                prev_done = pass_start;
            }
            comp_bbox_flip((const uint16_t *)s_bird_buf[slot],
                           (const uint16_t *)s_plate_buf, canvas);
            present_frame((uint8_t *)canvas);
            const int64_t now = esp_timer_get_time();
            const int64_t gap = now - prev_done;
            if (frames > 0 && gap > max_gap) max_gap = gap;
            if (frames > 0 && gap > BUDGET_US) busts++;
            prev_done = now;
            frames++;
            xQueueSend(s_free_q, &slot, 0);
        }
        const int64_t wall = esp_timer_get_time() - pass_start;
        s_v6_stop = true;
        vTaskDelay(pdMS_TO_TICKS(150));
        vQueueDelete(s_ready_q);
        vQueueDelete(s_free_q);
        ESP_LOGI(TAG, "BENCH3 V6 pipelined+bbox pass %d: frames %d | throughput avg %lu us/frame | worst frame gap %lu us | gaps over 83.3 ms: %d",
                 pass, frames,
                 (unsigned long)(wall / (uint64_t)frames),
                 (unsigned long)max_gap, busts);
    }
}


/* ---- V7 pipelined + SPAN flip-composite (2026-11-06) ---------------
 * Persistent canvas (starts as pure plate). Per frame, per row:
 * restore last frame's drawn span from the plate (memcpy), scan the
 * bird layer row for its ink span, composite ONLY that span flipped
 * (LUT multiply), remember the span. The strike's changed PIXELS are
 * ~6% of frame and its row spans ~30% — versus the 64% bbox V4-V6
 * recomputed every frame. Ink test: any channel clearly below the
 * layer's paper value in RGB565 units. */
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

static uint64_t s_span_px_acc;
static uint64_t s_span_px_acc_b;

static void comp_spans_rows(const uint16_t *bird, const uint16_t *plate,
                            uint16_t *dst, int y0, int y1, uint64_t *acc)
{
    for (int y = y0; y < y1; y++) {
        const uint16_t *prow = plate + (size_t)y * FRAME_W;
        uint16_t *drow = dst + (size_t)y * FRAME_W;
        if (s_span_x1[y] >= 0) {
            const int rx0 = s_span_x0[y], rx1 = s_span_x1[y];
            memcpy(drow + rx0, prow + rx0, (size_t)(rx1 - rx0 + 1) * 2);
            s_span_x1[y] = -1;
        }
        const uint16_t *brow = bird + (size_t)y * FRAME_W;
        int sx0 = -1, sx1 = -1;
        for (int x = 0; x < FRAME_W; x++) {
            if (is_ink(brow[x])) { sx0 = x; break; }
        }
        if (sx0 < 0) {
            continue;
        }
        for (int x = FRAME_W - 1; x > sx0; x--) {
            if (is_ink(brow[x])) { sx1 = x; break; }
        }
        if (sx1 < 0) sx1 = sx0;
        const int dx0 = FRAME_W - 1 - sx1;
        const int dx1 = FRAME_W - 1 - sx0;
        for (int x = dx0; x <= dx1; x++) {
            drow[x] = mul_px(brow[FRAME_W - 1 - x], prow[x]);
        }
        s_span_x0[y] = (int16_t)dx0;
        s_span_x1[y] = (int16_t)dx1;
        *acc += (uint64_t)(dx1 - dx0 + 1);
    }
}

static void comp_spans_flip(const uint16_t *bird, const uint16_t *plate, uint16_t *dst)
{
    comp_spans_rows(bird, plate, dst, 0, FRAME_H, &s_span_px_acc);
}

static void run_v7(void)
{
    uint16_t *canvas = (uint16_t *)s_out_buf[0];
    memcpy(canvas, s_plate_buf, FRAME_BYTES);
    for (int y = 0; y < FRAME_H; y++) {
        s_span_x1[y] = -1;
    }

    for (int pass = 0; pass < 2; pass++) {
        s_ready_q = xQueueCreate(2, sizeof(int));
        s_free_q = xQueueCreate(2, sizeof(int));
        int s0 = 0, s1 = 1;
        xQueueSend(s_free_q, &s0, 0);
        xQueueSend(s_free_q, &s1, 0);
        s_v6_stop = false;
        xTaskCreatePinnedToCore(decode_task, "bench3_dec", 4096, NULL, 6, NULL, 1);

        int frames = 0, busts = 0;
        int64_t pass_start = 0, prev_done = 0, max_gap = 0;
        s_span_px_acc = 0;
        while (frames < 60) {
            int slot;
            if (xQueueReceive(s_ready_q, &slot, pdMS_TO_TICKS(500)) != pdTRUE) {
                break;
            }
            if (frames == 0) {
                pass_start = esp_timer_get_time();
                prev_done = pass_start;
            }
            comp_spans_flip((const uint16_t *)s_bird_buf[slot],
                            (const uint16_t *)s_plate_buf, canvas);
            present_frame((uint8_t *)canvas);
            const int64_t now = esp_timer_get_time();
            const int64_t gap = now - prev_done;
            if (frames > 0 && gap > max_gap) max_gap = gap;
            if (frames > 0 && gap > BUDGET_US) busts++;
            prev_done = now;
            frames++;
            xQueueSend(s_free_q, &slot, 0);
        }
        const int64_t wall = esp_timer_get_time() - pass_start;
        s_v6_stop = true;
        vTaskDelay(pdMS_TO_TICKS(150));
        vQueueDelete(s_ready_q);
        vQueueDelete(s_free_q);
        ESP_LOGI(TAG, "BENCH3 V7 pipelined+spans pass %d: frames %d | throughput avg %lu us/frame | worst frame gap %lu us | gaps over 83.3 ms: %d | span coverage avg %.1f%%",
                 pass, frames,
                 (unsigned long)(wall / (uint64_t)frames),
                 (unsigned long)max_gap, busts,
                 (double)s_span_px_acc / (double)frames / (double)(FRAME_W * FRAME_H) * 100.0);
    }
}


/* ---- V8 dual-core spans (2026-11-06, Jimmy's go) -------------------
 * V7's span composite split by rows across both cores: main task takes
 * rows [0, FRAME_H/2), a worker pinned to core 1 takes [FRAME_H/2,
 * FRAME_H). Span state is per-row, so the halves are independent; a
 * task-notification pair joins them each frame before present. Decode
 * stays pipelined on core 1 as in V6/V7. */
static TaskHandle_t s_v8_worker;
static TaskHandle_t s_v8_main;
static const uint16_t *s_v8_bird;
static uint16_t *s_v8_canvas;
static volatile bool s_v8_stop;

static void v8_worker_task(void *arg)
{
    (void)arg;
    while (!s_v8_stop) {
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        if (s_v8_stop) break;
        comp_spans_rows(s_v8_bird, (const uint16_t *)s_plate_buf, s_v8_canvas,
                        FRAME_H / 2, FRAME_H, &s_span_px_acc_b);
        if (s_v8_main) xTaskNotifyGive(s_v8_main);
    }
    vTaskDelete(NULL);
}

static void run_v8(void)
{
    uint16_t *canvas = (uint16_t *)s_out_buf[0];
    memcpy(canvas, s_plate_buf, FRAME_BYTES);
    for (int y = 0; y < FRAME_H; y++) {
        s_span_x1[y] = -1;
    }
    s_v8_main = xTaskGetCurrentTaskHandle();
    s_v8_stop = false;
    xTaskCreatePinnedToCore(v8_worker_task, "bench3_hi", 4096, NULL, 6,
                            &s_v8_worker, 1);

    for (int pass = 0; pass < 2; pass++) {
        s_ready_q = xQueueCreate(2, sizeof(int));
        s_free_q = xQueueCreate(2, sizeof(int));
        int s0 = 0, s1 = 1;
        xQueueSend(s_free_q, &s0, 0);
        xQueueSend(s_free_q, &s1, 0);
        s_v6_stop = false;
        xTaskCreatePinnedToCore(decode_task, "bench3_dec", 4096, NULL, 6, NULL, 1);

        int frames = 0, busts = 0;
        int64_t pass_start = 0, prev_done = 0, max_gap = 0;
        s_span_px_acc = 0;
        s_span_px_acc_b = 0;
        while (frames < 60) {
            int slot;
            if (xQueueReceive(s_ready_q, &slot, pdMS_TO_TICKS(500)) != pdTRUE) {
                break;
            }
            if (frames == 0) {
                pass_start = esp_timer_get_time();
                prev_done = pass_start;
            }
            s_v8_bird = (const uint16_t *)s_bird_buf[slot];
            s_v8_canvas = canvas;
            xTaskNotifyGive(s_v8_worker);
            comp_spans_rows(s_v8_bird, (const uint16_t *)s_plate_buf, canvas,
                            0, FRAME_H / 2, &s_span_px_acc);
            ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
            present_frame((uint8_t *)canvas);
            const int64_t now = esp_timer_get_time();
            const int64_t gap = now - prev_done;
            if (frames > 0 && gap > max_gap) max_gap = gap;
            if (frames > 0 && gap > BUDGET_US) busts++;
            prev_done = now;
            frames++;
            xQueueSend(s_free_q, &slot, 0);
        }
        const int64_t wall = esp_timer_get_time() - pass_start;
        s_v6_stop = true;
        vTaskDelay(pdMS_TO_TICKS(150));
        vQueueDelete(s_ready_q);
        vQueueDelete(s_free_q);
        ESP_LOGI(TAG, "BENCH3 V8 dual-core+spans pass %d: frames %d | throughput avg %lu us/frame | worst frame gap %lu us | gaps over 83.3 ms: %d | span coverage avg %.1f%%",
                 pass, frames,
                 (unsigned long)(wall / (uint64_t)frames),
                 (unsigned long)max_gap, busts,
                 (double)(s_span_px_acc + s_span_px_acc_b) / (double)frames / (double)(FRAME_W * FRAME_H) * 100.0);
    }
    s_v8_stop = true;
    xTaskNotifyGive(s_v8_worker);
    vTaskDelay(pdMS_TO_TICKS(50));
}

static void bench_task(void *arg)
{
    (void)arg;
    build_tables();

    const size_t plen = (size_t)(plate_jpg_end - plate_jpg_start);
    memcpy(s_in_buf, plate_jpg_start, plen);
    uint32_t out_size = 0;
    esp_err_t err = jpeg_decoder_process(s_decoder, &s_decode_cfg, s_in_buf, plen,
                                         s_plate_buf, OUT_BUF_BYTES, &out_size);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "plate decode %s — bench aborted", esp_err_to_name(err));
        vTaskDelete(NULL);
    }
    ESP_LOGI(TAG, "plate decoded: %lu bytes", (unsigned long)out_size);

    run_v8();
    ESP_LOGI(TAG, "BENCH3 COMPLETE");
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

void app_main(void)
{
    ESP_LOGI(TAG, "heron — BBOX COMPOSITE BENCH v3");
    ESP_LOGI(TAG, "embedded payload: bird %u bytes + plate %u bytes",
             (unsigned)(bird_mjpeg_end - bird_mjpeg_start),
             (unsigned)(plate_jpg_end - plate_jpg_start));

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
        ESP_LOGE(TAG, "jpeg_new_decoder_engine: %s", esp_err_to_name(err));
        while (1) {
            vTaskDelay(pdMS_TO_TICKS(1000));
        }
    }

    jpeg_decode_memory_alloc_cfg_t in_alloc_cfg = {
        .buffer_direction = JPEG_DEC_ALLOC_INPUT_BUFFER,
    };
    jpeg_decode_memory_alloc_cfg_t out_alloc_cfg = {
        .buffer_direction = JPEG_DEC_ALLOC_OUTPUT_BUFFER,
    };
    size_t in_size = 0;
    s_in_buf = jpeg_alloc_decoder_mem(IN_BUF_BYTES, &in_alloc_cfg, &in_size);
    s_out_buf[0] = jpeg_alloc_decoder_mem(OUT_BUF_BYTES, &out_alloc_cfg, &s_out_buf_size[0]);
    s_out_buf[1] = jpeg_alloc_decoder_mem(OUT_BUF_BYTES, &out_alloc_cfg, &s_out_buf_size[1]);
    s_bird_buf[0] = jpeg_alloc_decoder_mem(OUT_BUF_BYTES, &out_alloc_cfg, &s_bird_buf_size[0]);
    s_bird_buf[1] = jpeg_alloc_decoder_mem(OUT_BUF_BYTES, &out_alloc_cfg, &s_bird_buf_size[1]);
    size_t plate_size = 0;
    s_plate_buf = jpeg_alloc_decoder_mem(OUT_BUF_BYTES, &out_alloc_cfg, &plate_size);
    if (s_in_buf == NULL || s_out_buf[0] == NULL || s_out_buf[1] == NULL ||
        s_bird_buf[0] == NULL || s_bird_buf[1] == NULL || s_plate_buf == NULL) {
        ESP_LOGE(TAG, "decoder buffer allocation failed");
        while (1) {
            vTaskDelay(pdMS_TO_TICKS(1000));
        }
    }
    ESP_LOGI(TAG, "decoder buffers ready (in %u B)", (unsigned)in_size);

    xTaskCreate(bench_task, "heron_bench", 8192, NULL, 5, NULL);
    ESP_LOGI(TAG, "bench task running");
}
