# Line heron: main.c (display plumbing + player) and heron_line.c
# (pose/outline/scheduler/rasterizer — shared verbatim with the host
# proof renderer in ../host). No embedded assets: the bird is drawn.
idf_component_register(SRCS "main.c" "heron_line.c"
                       INCLUDE_DIRS "."
                       REQUIRES waveshare__esp32_p4_wifi6_touch_lcd_7b lvgl__lvgl)
