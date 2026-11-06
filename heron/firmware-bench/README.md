# Heron — Living Loop Firmware, Stage A (Motion Proof)

Forked from `firmware-first-light` (same proven display path, same
component stack). One job: prove **motion** on the physical board.

**What it does**

1. Boots to the approved alert plate — identical first-light path
   (`bsp_display_start()` → brightness → plate in a fullscreen LVGL
   image widget).
2. A player task then loops the two accepted idle cycles forever,
   alternating: **idle1** (attempt 1, the video-generated breath,
   10 s) → **idle2** (attempt 2, the procedural warp loop, 1 s) → …
   Both clips start and end on the shared alert stance, so the hard
   cuts between plate, clips, and passes are invisible.
3. Frames are MJPEG clips embedded in the app binary, decoded by the
   ESP32-P4 **hardware JPEG decoder** (`esp_driver_jpeg`,
   YUV422 → RGB565) into double-buffered PSRAM frame buffers and
   presented through the *same* LVGL image widget as the plate, at
   12 fps.

No scheduler, no other behaviors — those are **Stage B**, gated on
this proof passing on real hardware.

**Target:** Waveshare ESP32-P4-WIFI6-Touch-LCD-7B (Rev1.1, ESP32-P4
silicon **rev v3.2**, 32 MB flash), ESP-IDF **v5.5.5**, target
`esp32p4`. Component pins (in `main/idf_component.yml`, unchanged
from first light): BSP `waveshare/esp32_p4_wifi6_touch_lcd_7b`
**1.0.4**, `espressif/esp_lvgl_port` **2.9.0** (via the BSP),
LVGL **9.3.0**. No chip-revision symbols anywhere — v5.5's default
REV_MIN_300 profile is correct for rev v3.2 silicon.

## Build & flash (on the Studio, macOS)

```sh
# 1. Enter the ESP-IDF v5.5.5 environment
. ~/esp-idf55/export.sh

# 2. Go to this project (staged copy on the Studio)
cd ~/heron-living-loop

# 3. One-time target selection (also resolves/downloads components —
#    needs internet on first run; creates dependencies.lock)
idf.py set-target esp32p4

# 4. ⚠ Apply the BSP patch (see "Known unknowns" #2) before building.

# 5. Build
idf.py build

# 6. Flash + watch the log
idf.py -p /dev/cu.usbmodem83401 flash monitor
```

Exit the monitor with `Ctrl-]`. Re-flash later:
`idf.py -p /dev/cu.usbmodem83401 flash`. The port number can change;
re-check with `ls /dev/cu.*` (opening the port resets the board —
normal).

## Success criteria

- **Serial log** shows, in order:
  - `heron_living_loop: heron living loop — STAGE A motion proof`
  - `boot plate on screen (1024x600 RGB565)`
  - `decoder buffers: in … B, out … + … B (PSRAM)`
  - `player task running — idle loop is live`
  - `clip start: idle1 …` then `clip start: idle2 …`, repeating
  - `living loop pass N complete (idle1 + idle2)` with **N advancing**
  - first frame of each clip logs `decoded frame size 1228800 bytes
    (expect 1228800)` — any other value means the decoder padded the
    output; tell Mordecai the number.
- **On the panel:** the plate appears at boot; ~1.5 s later the bird
  starts to **breathe** (idle1's slow generated breath, then idle2's
  subtler warp), and keeps moving — still looping, no freeze, after
  several minutes. Colors match the first-light plate.
- The board sits rotated 180° in its case and the image reads
  **upright** — same as first light. No rotation/mirror settings were
  added; if the picture is ever upside down, the fix is not in this
  code (see the first-light README).

## The clips

| Clip | Source (anim/final) | Frames | fps | Duration | Bytes |
|---|---|---|---|---|---|
| `main/idle1.mjpeg` | `attempt1.mp4` (1024×600 @ 24 fps) | 120 | 12 | 10.0 s | 3,822,207 |
| `main/idle2.mjpeg` | `attempt2.mp4` (1024×600 @ 12 fps) | 12 | 12 | 1.0 s | 487,210 |
| **Total embedded** | | | | | **4,309,417** (≤ 5 MB cap) |

Encoding: MJPEG, `yuvj422p` (4:2:2 — the P4 decoder rounds 4:2:0
heights up to a 16-pixel boundary, which would pad 600 → 608; 4:2:2
decodes to exactly 1024×600 RGB565 = 1,228,800 bytes), ffmpeg quality
`q9`. Idle is a slow breath, so 12 fps is visually smooth and halves
the payload vs 24 fps. Average frame ≈ 31.9 KB (idle1) / 40.6 KB
(idle2); largest single frame 42,007 B (player input buffer: 128 KB).

Regenerate (on the VM, from the anim folder):

```sh
ffmpeg -i attempt1.mp4 -vf fps=12 -q:v 9 -pix_fmt yuvj422p -codec:v mjpeg idle1.mjpeg
ffmpeg -i attempt2.mp4            -q:v 9 -pix_fmt yuvj422p -codec:v mjpeg idle2.mjpeg
```

Frame boundaries are found on-device by scanning SOI/EOI markers
(`FF D8`/`FF D9`); baseline JPEG byte-stuffing (a `0xFF` in entropy
data is always followed by `0x00`) makes that scan exact. It was
validated offline against these files: the scanner consumes each
blob exactly (120 / 12 frames, zero trailing bytes) and sample frames
extracted by the same algorithm decode standalone at 1024×600. The
embedded blobs are linked via `EMBED_FILES` in `main/CMakeLists.txt`
(no storage partition in Stage A).

App size estimate: first-light binary ≈ 2.5 MB (plate included) +
4.31 MB MJPEG ≈ **6.6–6.9 MB** in the **12 MB** factory partition —
≈ 5 MB of headroom for Stage B growth. Decoder buffers add
≈ 2 × 1.5 MB of the 32 MB PSRAM.

## Known unknowns — read before judging the first flash

1. **JPEG RGB565 byte/element order.** The player decodes with
   `.rgb_order = JPEG_DEC_RGB_ELEMENT_ORDER_BGR` in `play_clip()`
   (`main/main.c`) — the order Espressif's own decode example uses,
   and the one the v5.5 header pairs with the small-endian output
   that the proven plate data uses. It is still not provable
   off-device: if the panel shows the bird with **red and blue
   swapped** (rusty thighs gone blue, blue-grey plumage gone rusty),
   the remedy is exactly one line: change it to
   `JPEG_DEC_RGB_ELEMENT_ORDER_RGB`, rebuild, reflash. Jimmy's eyes
   on the real panel are the test. (A subtler variant: if colors are
   right but the image looks byte-swapped/garbled, say so — that's a
   different knob, and Mordecai will adjust.)
2. **BSP `<string.h>` patch — must be re-applied to THIS project.**
   BSP 1.0.4's `esp32_p4_wifi6_touch_lcd_7b.c` calls `memcpy` without
   `#include <string.h>` and the build treats it as an error. After
   the first `idf.py set-target`/build fetch creates
   `managed_components/` on the Studio, add `#include <string.h>`
   to that file's include block (the parent agent does this, as for
   first light). If the component is ever re-fetched, re-apply.
3. **Touch is unused in Stage A.** The board is rotated 180° in its
   case; GT911 orientation vs the flipped board is unverified and
   out of scope until a stage needs touch.

## Layout

```
CMakeLists.txt            project boilerplate (heron_living_loop)
sdkconfig.defaults        32 MB flash, PSRAM 200 MHz, custom partitions, RGB565
partitions.csv            12 MB factory app (grown from first light's 8 MB)
main/
  CMakeLists.txt          SRCS + REQUIRES esp_driver_jpeg + EMBED_FILES clips
  idf_component.yml       BSP 1.0.4 + LVGL 9.3.0 pins (from first light)
  main.c                  boot plate -> HW-JPEG idle player task
  alert_plate_img.c/.h    the boot plate (RGB565 LVGL array, from first light)
  idle1.mjpeg             attempt1 @ 12 fps q9 4:2:2 (3,822,207 B)
  idle2.mjpeg             attempt2 @ 12 fps q9 4:2:2 (487,210 B)
tools/
  png_to_lvgl_rgb565.py   PNG -> LVGL v9 RGB565 converter (from first light)
STAGE_MANIFEST.md         file-by-file staging routes for the Studio
```
