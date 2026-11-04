# Heron device — REVISED spec: 1024×600 / ESP32-P4 (2026-11-02)

Supersedes device-800x480-spec.md (the 4.3″ S3 build) as the leading product
configuration, following Jimmy's art pick (naturalist plate, design for a
larger screen) and the two-style-pack trial. **Order status (2026-11-02):
Jimmy said "go ahead and order a kit" (PETG excluded — he has some), but
NO order was placed anywhere: Amazon refused the agent session, and Jimmy
chose to buy it himself from exact Amazon links sent to him in chat (his
standing small-purchase preference). Waveshare's own store lists the board
at $46.99 if Amazon's price runs well above ~$65.**

## Core
- Waveshare ESP32-P4-WIFI6-Touch-LCD-7B (BASIC — no camera): 7″ 1024×600 IPS,
  EK79007, 2-lane MIPI-DSI @ 1 Gbps/lane, GT911 touch, ESP32-P4 (dual RISC-V
  360 MHz) + ESP32-C6 Wi-Fi 6/BLE coprocessor, 32 MB PSRAM, USB-C 5 V (~600 mA).
- Price seen 2026-11-02: $51.99 (Sunsky, in stock); EU €67–99; US landed
  planning number ~$60.
- PERFORMANCE VERIFIED (sources in chat 2026-11-02): panel timing 60 Hz class
  (52 MHz pclk); Espressif-measured full-frame DSI throughput at 1024×600 =
  55 fps RGB565 / 50 fps RGB888 vs our 24 fps authoring cadence (>2× headroom);
  pose net ~41k params is negligible on the P4 (PPA + 2D-DMA assist rendering;
  static-first frames mostly unchanged → real load well under worst case).
- ⚠ MIC: the BASIC 7B carries an onboard microphone (as does the whole P4
  voice-panel class). **Jimmy ruled 2026-11-02: "it can have a mic — not a
  hard no in this case."** Scoped exception for this kit; the no-camera rule
  stands (order the BASIC, never the -C camera variant).

## Voice phrases (Jimmy, 2026-11-02, after the mic ruling)

- Jimmy's idea: "maybe the creatures respond to simple phrases." Recognition
  is **on-device phrase-spotting only** — a wake name plus a small fixed
  vocabulary; nothing recorded, nothing transmitted, nothing to the cloud.
  The honest sell line: *"it hears a few words and keeps nothing."*
- Phrases are just another input on the creature's event bus, alongside
  presence, light, touch, and time.
- Starter vocabulary sketched for the heron: its name → alert/look;
  "go fishing" → the fish-now behavior; "fly away" / "come back" →
  departure/return; "stretch" → wing stretch; "goodnight" → one-leg doze +
  dim; "good bird" → ruffle-shake.
- Design rule (Mordecai's, filed with the idea): phrases **nudge, never
  command** — the creature usually obliges at the right moment and
  sometimes ignores you; tunable per creature like every other input.

## Status
- **ORDERED BY JIMMY 2026-11-02** (Amazon, himself, from links Mordecai
  supplied — Amazon refuses the agent browser outright): the 7B BASIC board
  + Anker brick + UGREEN right-angle cable + M3 kit. **Sensors SKIPPED by
  Jimmy for now** — LD2410C + BH1750 deferred, not cancelled; both bolt on
  later (presence/light are creature inputs; early trials can simulate them).

## Rest of build (unchanged from the 800×480 spec unless noted)
- HLK-LD2410C mmWave presence: $5–8
- BH1750 light sensor: $2–3
- Certified 5 V/3 A USB-C brick: ~$10 (uprated from 2 A for the ~3 W draw)
- Right-angle USB-C cable: ~$6
- PETG filament, 7″ case (~150–200 g): ~$6–9 — **material SETTLED by Jimmy
  2026-11-02: PETG for everything, prototype included** (PLA considered and
  passed over; PETG's ~80 °C softening point covers sunlit-window placement).
  Case to be designed with vent slots over the SoC and panel back edge.
- M3 hardware/standoffs: ~$3
- Optional physical "fish now" button: $2–4 (touch tap can serve)
- Misc wiring/connectors: ~$2

## Total
- **≈ $90–115 per unit prototype; ~$100 planning number** (vs $65–85 for the
  4.3″ build — the delta is almost entirely the bigger board).
- Local retail plausibility at this BOM: ~$199–249 (vs $129–179 before).
- Power ~3 W, USB-C, instant-on class retained. Case still printed on the
  Bambu X1 Carbon.
