# Heron — First Light Firmware

One job: boot the Waveshare **ESP32-P4-WIFI6-Touch-LCD-7B** (Rev1.1), bring
the 1024×600 MIPI-DSI panel up through the Waveshare BSP, and show a single
fullscreen image — the approved alert plate
(`art2/plates-fresh/eye-first/final/alert_legfix_approved.png`).

Target toolchain: **ESP-IDF v5.3.1**, target `esp32p4`.

## Why these component versions (verified 2026-11-04)

Checked against the ESP Component Registry component
`waveshare/esp32_p4_wifi6_touch_lcd_7b` (its own `idf_component.yml`):

| BSP version | IDF requirement | Notes |
|---|---|---|
| 3.0.1 (latest) | `>=5.5` | Uses `espressif/esp_lvgl_adapter` + LVGL 9.5 — **not** for IDF 5.3.1 |
| 2.0.0 | `>=5.5` | Same problem |
| **1.0.4** | **`>=5.3`** | Uses `espressif/esp_lvgl_port ^2` — **this is the one** |

So `main/idf_component.yml` pins:

- `waveshare/esp32_p4_wifi6_touch_lcd_7b: "1.0.4"` — newest BSP that
  accepts IDF 5.3.1. Panel driver `esp_lcd_ek79007 1.*`, touch GT911.
- `lvgl/lvgl: "9.2.2"` — the BSP's headers use the LVGL 9 API
  (`lv_display_t`), so LVGL must resolve to v9 even though the BSP's loose
  range says `>=8,<10`. 9.2.2 is the known-good pairing with
  `esp_lvgl_port 2.x` (which floats to the newest 2.x under the BSP's `^2`
  constraint; 2.9.0 was spot-checked to still compile on IDF 5.3.1).

`main/main.c` is written against the BSP 1.0.4 headers:

- `bsp_display_start()` — panel + LVGL port + touch, RGB565, 1024×50 DMA
  draw buffer.
- `bsp_display_brightness_set(100)` — required separately; `start()` only
  initialises the backlight PWM.
- `bsp_display_lock(0)` / `bsp_display_unlock()` around all LVGL calls.

## Board-specific sdkconfig (already in `sdkconfig.defaults`)

- `CONFIG_ESP32P4_SELECTS_REV_LESS_V3=y` + `CONFIG_ESP32P4_REV_MIN_100=y` —
  the board's P4 silicon is rev v1.x; without these the app will not boot
  under IDF 5.3.1 defaults (root cause from xiaozhi-esp32 PR #1943).
- `CONFIG_ESPTOOLPY_FLASHSIZE_32MB=y` — 32 MB flash.
- `CONFIG_SPIRAM=y`, `CONFIG_SPIRAM_SPEED_200M=y` — 32 MB in-package PSRAM.
- Custom `partitions.csv` — one 8 MB factory app; the plate is ~1.2 MB of
  the binary and outgrows the stock single-app partition.

## Build & flash (on the Studio, macOS)

The board is plugged into the Studio. In a terminal:

```sh
# 1. Enter the ESP-IDF v5.3.1 environment
#    (adjust the path if IDF was installed somewhere else)
. ~/esp/esp-idf-v5.3.1/export.sh

# 2. Go to this project
cd /path/to/firmware-first-light

# 3. One-time target selection (also resolves/downloads the components —
#    needs internet on first run; creates dependencies.lock)
idf.py set-target esp32p4

# 4. Build
idf.py build

# 5. Flash + watch the log
idf.py -p /dev/cu.usbmodem83401 flash monitor
```

Exit the monitor with `Ctrl-]`. To just re-flash later:
`idf.py -p /dev/cu.usbmodem83401 flash`.

**Expected result:** the panel lights and shows the heron alert plate,
fullscreen. Serial log ends with
`heron_first_light: First light: alert plate on screen (1024x600 RGB565)`.

### Which serial port?

`/dev/cu.usbmodem83401` was the port the board presented when it was
plugged in on 2026-11-04, but the number can change. Re-check with:

```sh
ls /dev/cu.*
```

Plug the board in and use the newly-appeared `/dev/cu.usbmodem*` (native
USB) or `/dev/cu.usbserial*` / `/dev/cu.wchusbserial*` (the USB-TO-UART
Type-C port) entry. Either of the board's Type-C ports can flash; if
`idf.py flash` can't sync, hold **BOOT**, tap **RESET**, release BOOT, and
run the flash command again.

> Note: opening the serial port resets the ESP32 — that's normal.

## The image

- `main/alert_plate_img.c` / `.h` — LVGL v9 `lv_image_dsc_t`,
  `LV_COLOR_FORMAT_RGB565`, 1024×600, stride 2048, data = **1,228,800
  bytes** (= 1024×600×2), little-endian RGB565 (matches the BSP's
  `BSP_LCD_BIGENDIAN 0` → `swap_bytes=false`).
- Regenerate from the PNG with:

  ```sh
  python3 tools/png_to_lvgl_rgb565.py \
      ../art2/plates-fresh/eye-first/final/alert_legfix_approved.png \
      main/alert_plate_img.c alert_plate_img alert_plate_img.h
  ```

  (paths relative to this project folder; adjust if the layout differs).
  The converter self-checks the byte count and prints the first/last row
  pixel words. The generated array was round-trip verified against the
  PNG: exact within RGB565 quantisation.

## Troubleshooting

- **Build picks BSP 3.x / fails on `esp_lvgl_adapter`** — the pin in
  `main/idf_component.yml` was lost; it must stay `1.0.4` on IDF 5.3.1.
  Delete `dependencies.lock` and `managed_components/` and rebuild.
- **Boots but screen black, log fine** — backlight: `main.c` already calls
  `bsp_display_brightness_set(100)` after `bsp_display_start()`; check the
  log for brightness errors.
- **Image upside down** — do not rotate the PNG. The BSP already configures
  the port with `mirror_x/mirror_y` for this panel's mounting; if a future
  BSP changes that, the knob is the display rotation in the BSP/port, not
  the artwork.
- **`esp_lvgl_port` fails against LVGL 9.2.2 on a future re-resolve** —
  pin `espressif/esp_lvgl_port: "2.6.0"` in `main/idf_component.yml`
  (era-matched to IDF 5.3.1 + LVGL 9.2).

## Layout

```
CMakeLists.txt            project boilerplate
sdkconfig.defaults        chip-rev fix, 32 MB flash, PSRAM, partitions
partitions.csv            8 MB factory app
main/
  CMakeLists.txt
  idf_component.yml       BSP 1.0.4 + LVGL 9.2.2 pins
  main.c                  display start -> brightness -> fullscreen image
  alert_plate_img.c/.h    generated plate (RGB565 LVGL array)
tools/
  png_to_lvgl_rgb565.py   PNG -> LVGL v9 RGB565 converter (re-runnable)
```
