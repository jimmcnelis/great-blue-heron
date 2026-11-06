# Stage A player: main.c (boot + MJPEG idle player), alert_plate_img.c (the
# embedded boot plate) and the two idle clips embedded as binary blobs.
# EMBED_FILES places idle1.mjpeg / idle2.mjpeg in .rodata and generates the
# _binary_idle1_mjpeg_start/_end (+ idle2) symbols main.c links against.
# esp_driver_jpeg: the ESP32-P4 hardware JPEG decoder (driver/jpeg_decode.h).
idf_component_register(SRCS "main.c" "alert_plate_img.c"
                       INCLUDE_DIRS "."
                       REQUIRES waveshare__esp32_p4_wifi6_touch_lcd_7b lvgl__lvgl esp_driver_jpeg
                       EMBED_FILES "idle1.mjpeg" "idle2.mjpeg")
