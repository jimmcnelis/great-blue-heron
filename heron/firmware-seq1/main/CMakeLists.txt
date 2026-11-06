# Sequence-1 player: main.c (boot + MJPEG player), alert_plate_img.c (the
# embedded boot plate — regenerated from the marsh home frame) and the
# sequence clip + rest still embedded as binary blobs.
# EMBED_FILES places seq1.mjpeg / rest.jpg in .rodata and generates the
# _binary_seq1_mjpeg_start/_end (+ rest_jpg) symbols main.c links against.
# esp_driver_jpeg: the ESP32-P4 hardware JPEG decoder (driver/jpeg_decode.h).
# The FLIGHT clips + plate are NOT embedded: esptool caps one flash
# segment at 16 MB, so large MJPEG assets live in the 'assets' data
# partition (assets.bin, see make_assets_blob.py) and are memory-mapped
# at runtime by main.c.
idf_component_register(SRCS "main.c" "alert_plate_img.c"
                       INCLUDE_DIRS "."
                       REQUIRES waveshare__esp32_p4_wifi6_touch_lcd_7b lvgl__lvgl esp_driver_jpeg esp_partition
                       EMBED_FILES "seq1.mjpeg" "rest.jpg" "p1_blink.jpg" "p2_sacmid.jpg" "p3_sacr.jpg" "p4_tiltmid.jpg" "p5_tiltfull.jpg" "p6_scan1.jpg" "p7_scan2.jpg" "p8_scan3.jpg" "p9_scanend.jpg" "q1_dep.jpg" "q2_weight.jpg" "q3_tucked.jpg" "q4_fan1.jpg" "q5_fan2.jpg" "q6_fan3.jpg" "q7_leg1.jpg" "q8_leg2.jpg" "q9_full.jpg" "r1_depmid.jpg" "r2_glance.jpg" "r3_shoulder.jpg" "r4_nibble.jpg" "r5_draw.jpg" "r6_chest.jpg" "r7_shake.jpg" "r8_settle.jpg" "s1_rise0.jpg" "s2_rise1.jpg" "s3_pose.jpg")
