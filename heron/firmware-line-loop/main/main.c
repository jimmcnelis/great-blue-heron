/*
 * heron LINE LOOP — a great blue heron drawn as one continuous black
 * line on plate paper, living on the board. No video assets: the
 * firmware rasterizes the line into an RGB565 framebuffer every frame
 * (heron_line.c — the same code the host proof renderer verifies).
 *
 * Display path is the proven Stage A path (BSP 1.0.4 + LVGL 9.3.0,
 * image descriptor presented under the display lock). The board sits
 * rotated 180 deg in its case and reads upright as configured here;
 * no rotation or mirroring is applied.
 *
 * Timing: TRUE by default — behaviors play at authored speed, idle
 * holds run 20-90 s. Define HL_PROOF_SPEED (e.g. via CFLAGS) to
 * compress idle holds to 2-5 s for a bench demo.
 */
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_err.h"
#include "esp_log.h"
#include "esp_random.h"
#include "esp_heap_caps.h"

#include "lvgl.h"
#include "bsp/esp32_p4_wifi6_touch_lcd_7b.h"
#include "bsp/display.h"

#include "heron_line.h"

#ifndef HL_PROOF_SPEED
#define HL_PROOF_SPEED 0
#endif

static const char *TAG = "heron_line_loop";

#define FRAME_BYTES (HL_W * HL_H * 2)

static lv_obj_t *s_img;
static uint16_t *s_fb;               /* scene canvas in PSRAM */
static hl_scene s_scene;

static lv_image_dsc_t s_frame_dsc = {
    .header = {
        .magic = LV_IMAGE_HEADER_MAGIC,
        .cf = LV_COLOR_FORMAT_RGB565,
        .flags = 0,
        .w = HL_W,
        .h = HL_H,
        .stride = HL_W * 2,
    },
    .data_size = FRAME_BYTES,
    .data = NULL,
};
static bool s_frame_src_set;

static void present_frame(void)
{
    bsp_display_lock(0);
    s_frame_dsc.data = (const uint8_t *)s_fb;
    if (!s_frame_src_set) {
        lv_image_set_src(s_img, &s_frame_dsc);
        lv_obj_set_pos(s_img, 0, 0);
        s_frame_src_set = true;
    }
    lv_obj_invalidate(s_img);
    bsp_display_unlock();
}

static void player_task(void *arg)
{
    (void)arg;
    const TickType_t period = pdMS_TO_TICKS(1000) / 12;
    TickType_t last = xTaskGetTickCount();
    int prev_state = -1;
    while (1) {
        hl_scene_step(&s_scene, 1.0f / 12.0f);
        present_frame();
        if (s_scene.state != prev_state) {
            ESP_LOGI(TAG, "now: %s", hl_behavior_name(s_scene.state));
            prev_state = s_scene.state;
        }
        vTaskDelayUntil(&last, period);
    }
}

void app_main(void)
{
    ESP_LOGI(TAG, "heron LINE LOOP — one black line, living loop");
    ESP_LOGI(TAG, "proof speed: %s", HL_PROOF_SPEED ? "ON (holds 2-5 s)" : "off (true timing)");

    lv_display_t *disp = bsp_display_start();
    if (disp == NULL) {
        ESP_LOGE(TAG, "bsp_display_start() failed — no display");
        return;
    }
    ESP_ERROR_CHECK(bsp_display_brightness_set(100));

    s_fb = heap_caps_malloc(FRAME_BYTES, MALLOC_CAP_SPIRAM);
    if (s_fb == NULL) {
        ESP_LOGE(TAG, "framebuffer allocation failed");
        return;
    }

    hl_scene_init(&s_scene, s_fb, esp_random(), HL_PROOF_SPEED);
    hl_scene_step(&s_scene, 0.0f);   /* first frame: the bird at rest */

    bsp_display_lock(0);
    lv_obj_t *scr = lv_screen_active();
    lv_obj_remove_flag(scr, LV_OBJ_FLAG_SCROLLABLE);
    s_img = lv_image_create(scr);
    lv_obj_remove_flag(s_img, LV_OBJ_FLAG_SCROLLABLE);
    bsp_display_unlock();
    present_frame();

    ESP_LOGI(TAG, "line heron on screen (%dx%d RGB565)", BSP_LCD_H_RES, BSP_LCD_V_RES);
    xTaskCreate(player_task, "heron_player", 8192, NULL, 5, NULL);
    ESP_LOGI(TAG, "player task running — the loop is live");
}
