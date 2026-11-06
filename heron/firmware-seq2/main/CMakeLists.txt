# Sequence-2 player: layer pipeline + flip-in-code mirroring + stride.
# EMBED_FILES holds only still LAYERS now (bird-only, flat paper canvas)
# under the seq1 filenames, plus the stride pose set (z_*). The MJPEG
# layer streams (strike, flight pair) and the marsh plate live in the
# 'assets' data partition (assets.bin, see make_assets_blob.py) — the
# 16 MB single-segment cap that forced flight out in seq1 applies to
# the whole embedded set, and layers keep the app small.
idf_component_register(SRCS "main.c" "alert_plate_img.c"
                       INCLUDE_DIRS "."
                       REQUIRES waveshare__esp32_p4_wifi6_touch_lcd_7b lvgl__lvgl esp_driver_jpeg esp_partition
                       EMBED_FILES "rest.jpg" "p1_blink.jpg" "p2_sacmid.jpg" "p3_sacr.jpg" "p4_tiltmid.jpg" "p5_tiltfull.jpg" "p6_scan1.jpg" "p7_scan2.jpg" "p8_scan3.jpg" "p9_scanend.jpg" "q1_dep.jpg" "q2_weight.jpg" "q3_tucked.jpg" "q4_fan1.jpg" "q5_fan2.jpg" "q6_fan3.jpg" "q7_leg1.jpg" "q8_leg2.jpg" "q9_full.jpg" "r1_depmid.jpg" "r2_glance.jpg" "r3_shoulder.jpg" "r4_nibble.jpg" "r5_draw.jpg" "r6_chest.jpg" "r7_shake.jpg" "r8_settle.jpg" "s1_rise0.jpg" "s2_rise1.jpg" "s3_pose.jpg" "z_d1_halfrise.jpg" "z_d2_carriage.jpg" "z_wa_swing.jpg" "z_adv_near.jpg" "z_plant_near.jpg" "z_pass1_near.jpg" "z_pass2_near.jpg" "z_adv_far.jpg" "z_plant_far.jpg" "z_pass1_far.jpg" "z_pass2_far.jpg" "z_plant_far_short.jpg" "z_t1_turn.jpg" "z_t2_frontal.jpg" "z_t3_turn.jpg" "z_t4_left.jpg" "z_t5_sink.jpg")
