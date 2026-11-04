# Heron board — arrival day checklist (Wed Nov 4, 2026)

Prepared 2026-11-03 evening, ahead of delivery. Spec source:
`device-1024x600-spec.md` (same folder). Jimmy's standing order stands:
the install-ready draft is a **goal, not a reason to skip iteration
gates** — this checklist covers the hardware only; no heron firmware
gets flashed until Jimmy judges the rig/motion work in chat.

## 1. Verify it's the right board (before anything else)
- [ ] Box/board reads **Waveshare ESP32-P4-WIFI6-Touch-LCD-7B, BASIC**
- [ ] **No camera module** — the -C camera variant is the wrong unit;
      the no-camera rule stands (mic exception only)
- [ ] Panel is 7″ 1024×600 (EK79007, GT911 touch)
- [ ] Note/photograph board revision + silkscreen markings for
      firmware targeting later

## 2. Kit inventory (Jimmy's Amazon order, 2026-11-02)
- [ ] 7B BASIC board
- [ ] Anker 5 V/3 A USB-C brick
- [ ] UGREEN right-angle USB-C cable, 3 ft
- [ ] Litorange M3 standoff/screw kit (320 pc)
- Sensors (LD2410C presence, BH1750 light) were **skipped by Jimmy** —
  not missing if absent; they bolt on later, early trials simulate them.

## 3. Bench power-on (factory state only)
- [ ] Power from the Anker brick (board wants USB-C 5 V, ~600 mA)
- [ ] Factory demo boots; panel lights evenly, no dead rows/columns
- [ ] Touch responds (GT911) — tap corners + center
- [ ] Leave it at factory state; this is a hardware pass/fail check,
      not a flash session

## 4. Case fit
- [ ] Dry-fit board against the printed PETG case
      (`case-1024x600/` — dock-split design is the settled one)
- [ ] Check vent slots land over the SoC / panel back edge per spec
- [ ] M3 standoffs from the kit match the board's mounting holes

## Hold point
Rig rebuild is the critical path (head-anchor done Nov 3 evening,
body-mass round dispatched, decoder retrain last). When Jimmy gives
the motion verdict, the install step starts from §3's verified board —
not from an unopened box.
