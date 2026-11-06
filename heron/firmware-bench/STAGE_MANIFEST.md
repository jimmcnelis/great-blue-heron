# Stage Manifest — firmware-living-loop (Stage A)

Every file in this project, its size, and how it reaches the Studio
staging copy (`~/heron-living-loop/`). Byte sizes are exact as built
on the VM, 2026-11-04.

## (a) Text channel — parent writes these to the Studio directly

| File | Bytes |
|---|---|
| `CMakeLists.txt` | 195 |
| `partitions.csv` | 179 |
| `sdkconfig.defaults` | 1,571 |
| `README.md` | 7,362 |
| `STAGE_MANIFEST.md` | this file |
| `main/CMakeLists.txt` | 634 |
| `main/main.c` | 12,097 |
| `main/alert_plate_img.h` | 301 |
| `main/idf_component.yml` | 1,107 |
| `tools/png_to_lvgl_rgb565.py` | 4,076 |

## (b) Spark pull route — too large and/or binary for the text channel

Stage these at the same relative paths under jim's home on the Spark,
then on the Studio pull each with
`~/bin/mordecai_spark_pull.sh <path-relative-to-jim-home> ~/heron-living-loop/<same-relative-path>`
and verify md5 after the pull.

| File | Bytes | md5 |
|---|---|---|
| `main/alert_plate_img.c` | 7,537,871 | `3c1ef737c91b4f32438aef6b59296310` |
| `main/idle1.mjpeg` | 3,822,207 | `330d1d6c5b4ae067dc045395657694e6` |
| `main/idle2.mjpeg` | 487,210 | `a4eb55fb36404e46bbae61ca846eb2da` |

Note: `main/alert_plate_img.c` is byte-identical to the first-light
file already flashed and proven on this board (same md5 as the copy
staged for first light) — if the Studio's `~/heron-first-light/main/`
copy is still in place it can simply be copied from there instead.

## (c) Managed-components patch reminder

After the first `idf.py set-target esp32p4` (or first build attempt)
fetches components into `~/heron-living-loop/managed_components/` on
the Studio, and **before** building:

- Open `managed_components/waveshare__esp32_p4_wifi6_touch_lcd_7b/esp32_p4_wifi6_touch_lcd_7b.c`
- Add `#include <string.h>` to its include block (BSP 1.0.4 calls
  `memcpy` without it; the build errors out otherwise).

Same one-line patch as first light. If `managed_components/` is ever
deleted or the component re-fetched, re-apply it.
