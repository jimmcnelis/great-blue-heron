# FLIP+COMPOSITE BENCH: bird-layer MJPEG + marsh plate JPEG embedded.
idf_component_register(SRCS "main.c" "alert_plate_img.c"
                       INCLUDE_DIRS "."
                       REQUIRES waveshare__esp32_p4_wifi6_touch_lcd_7b lvgl__lvgl esp_driver_jpeg
                       EMBED_FILES "bird.mjpeg" "plate.jpg")
