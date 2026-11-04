# Heron — bigger-screen device: spec & build list (800×480)

Prepared 2026-11-02 at Jimmy's request. **Conditional:** parts are bought only if the
heron proves itself on the bench BOX-3 first, and only with Jimmy's double
confirmation at buy time. Prices are street prices seen 2026-11-02 (search-verified
where noted) — re-verify at purchase; they drift.

## The device in one paragraph

A framed, always-on art object: 800×480 IPS panel driven by an ESP32-S3, the heron
simulation (160×96 palette grid, exact ×5) filling the screen edge to edge, an
mmWave presence sensor hidden inside a 3D-printed case (radar passes through
PETG), an ambient-light sensor for night dimming, tap-to-fish via the panel's
capacitive touch (plus an optional physical button), powered over USB-C at 5 V.
No camera, no microphone, radios never initialized in the shipping firmware —
presence without surveillance. Instant-on (<1 s), ~2–3 W worst case.

## Core spec

| Item | Spec |
|---|---|
| Display | 4.3″ IPS, 800×480, 65K color, 160° viewing angle, capacitive 5-point touch |
| Brain | ESP32-S3N16R8 — dual-core 240 MHz, 16 MB flash, 8 MB PSRAM |
| Model grid | 160×96 palette-indexed ×5 → 800×480 full-bleed |
| Presence | HLK-LD2410C 24 GHz mmWave — moving + still presence, ≤6 m, ±60°, UART 256000, 5 V, 16×22 mm |
| Light | BH1750 (I2C) — auto-dim / night sleep |
| Input | Panel touch (tap = fish now); optional side button |
| Power | USB-C, 5 V ⎓ ~2 A certified brick; ~2–3 W total at full brightness |
| Case | PETG, Bambu-printed frame + easel back, vents high/low, radar window = the case wall itself |
| Firmware | ESP-IDF/Arduino + esp_lcd RGB panel; springs + state machine ported from the sim; presence events: approach / watched / empty |

## Build list (per unit, prototype quantity)

| # | Part | Notes | Est. |
|---|---|---|---|
| 1 | **Waveshare ESP32-S3-Touch-LCD-4.3** | The core: S3 + 4.3″ 800×480 IPS + touch + USB-C on one board, 106×68 mm. Seen €39.90 (EU retail) and ~$26–33 (marketplace) — expect ~$35–45 landed US. A 5″ sibling exists in the same family if more presence is wanted at the same resolution; avoid the 4.3C variant (adds microphones we don't want). | ~$35–45 |
| 2 | **HLK-LD2410C** mmWave presence module | UART to the S3; mounts inside the case behind the front wall. Seen $4.90–8. | ~$5–8 |
| 3 | **BH1750** light-sensor module | I2C; sits behind a pinhole or the case's top vent slot. | ~$2–3 |
| 4 | USB-C brick, 5 V/2 A+, certified (e.g. Anker) | Ship-with or spec-as-required; no no-name bricks. | ~$10 |
| 5 | USB-C cable, right-angle, 1 m | Strain-relieved exit at the case back. | ~$6 |
| 6 | PETG filament ~150–250 g | Frame, back, easel foot; matte black or color-matched to order. | ~$4–6 |
| 7 | M3 heat-set inserts + screws, standoffs | Board mounts on its own posts inside the frame. | ~$3 |
| 8 | (Optional) 12 mm metal momentary button | Physical "fish now" for the touch-averse. | ~$2–4 |
| 9 | Misc wire / JST leads | Sensor leads, button leads. | ~$2 |

**Per-unit total: ≈ $65–85** at prototype quantity (call it ~$55–75 once the
marketplace board price is the norm). Consistent with a $129–179 local retail.

## Assembly & product notes

- Board is 106×68 mm → case lands ~125×85×28 mm at 4.3″. Print orientation:
  face-down bezel print for a clean front; radar sits behind the upper bezel —
  keep metal fasteners out of its ±60° cone.
- Thermals: S3 + backlight in a sealed box — vent slots top and bottom edge,
  backlight is the main heat source; night dim doubles as thermal relief.
- The LD2410C's gate energies need per-room tuning (its app/UART config);
  ship with a conservative living-room profile, tune on the bench unit.
- Firmware lineage: same discipline as Skunkflame/portrait — no radios
  initialized, checksum banner on serial, watchdog on.
- Updates: USB-C reflash at the bench; no OTA in the local product (nothing
  to phone home to — that's the pitch).

## Display explorations (2026-11-02 — not decided, filed)

Jimmy raised OLED/monochrome and then dot-matrix as alternative faces. Surveyed:

- **HUB75 RGB LED matrix (true dots, full color):** 64×64 P2.5 panel (160×160 mm)
  $25.99 Waveshare / $36.99 Apollo / $12–18 direct; 128×64 strip ~$12–45;
  Waveshare ESP32-S3-RGB-Matrix driver $24.99. Two 64×64 chained vertically =
  64×128 tall stage. Grammar forced: bird of light on BLACK (white field = all
  dots lit = heat + amps). Panels rated 5 V/4 A peak each; our sparse scene uses
  a fraction, brightness-capped. Style study: art-candidates/heron dots color.
- **Mono OLED strips (SSD1322, 16 grays):** 256×64 — 3.2″ module ≈ $22, 5.5″ ≈
  $58–70 (white/green/yellow/blue). SPI, trivial for the S3. Taxes: 4:1 strip
  format (small bird, long creek) and OLED burn-in (mitigated by zone movement
  + presence-driven sleep). Style studies: the two OLED mono treatments.
- **Flip-dot:** physical B/W dots, zero-power hold — several hundred dollars per
  panel; charm object, not a product.
- **Dots as rendering ($0):** the spec'd 800×480 IPS (or the BOX-3) can draw
  every palette cell as a round dot with gutters — dot texture becomes a style
  dial, color and the white void survive. Pragmatic winner for the style;
  HUB75 is the winner for a physical dot object.

## Gate before buying

1. Heron v1 verdict on the bench BOX-3 (320×240, full-bleed 160×120).
2. Jimmy's double confirmation on the buy list.
3. Then: one prototype unit → case iterations → small batch.
