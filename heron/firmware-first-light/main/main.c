/*
 * heron first light — boot, bring up the panel through the Waveshare BSP,
 * and show one fullscreen image: the approved alert plate.
 *
 * Board : Waveshare ESP32-P4-WIFI6-Touch-LCD-7B (Rev1.1), 1024x600 MIPI-DSI
 * BSP   : waveshare/esp32_p4_wifi6_touch_lcd_7b 1.0.4 (see main/idf_component.yml)
 * API   : written against the BSP 1.0.4 headers —
 *         bsp_display_start()          -> lv_display_t*
 *         bsp_display_brightness_set() -> backlight must be set separately
 *         bsp_display_lock/unlock()    -> LVGL mutex around all lv_* calls
 */
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_err.h"
#include "esp_log.h"

#include "lvgl.h"
#include "bsp/esp32_p4_wifi6_touch_lcd_7b.h"
#include "bsp/display.h"

#include "alert_plate_img.h"

static const char *TAG = "heron_first_light";

void app_main(void)
{
    /* Panel + LVGL port + GT911 touch, all initialised by the BSP.
     * Defaults in BSP 1.0.4: RGB565, single 1024x50 draw buffer (DMA),
     * LVGL task started by esp_lvgl_port. */
    lv_display_t *disp = bsp_display_start();
    if (disp == NULL) {
        ESP_LOGE(TAG, "bsp_display_start() failed — no display");
        return;
    }

    /* bsp_display_start() only initialises the backlight PWM; the BSP
     * header requires brightness to be enabled separately. */
    ESP_ERROR_CHECK(bsp_display_brightness_set(100));

    /* All LVGL calls must hold the LVGL mutex (0 = wait forever). */
    bsp_display_lock(0);

    lv_obj_t *scr = lv_screen_active();
    lv_obj_remove_flag(scr, LV_OBJ_FLAG_SCROLLABLE);

    lv_obj_t *img = lv_image_create(scr);
    lv_image_set_src(img, &alert_plate_img);
    /* The plate is exactly 1024x600, i.e. fullscreen — park it at the origin
     * and make sure a stray touch-drag can never shift it. */
    lv_obj_set_pos(img, 0, 0);
    lv_obj_remove_flag(img, LV_OBJ_FLAG_SCROLLABLE);

    bsp_display_unlock();

    ESP_LOGI(TAG, "First light: alert plate on screen (%dx%d RGB565)",
             BSP_LCD_H_RES, BSP_LCD_V_RES);

    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
