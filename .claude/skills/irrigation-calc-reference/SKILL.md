---
name: irrigation-calc-reference
description: The formulas, units and agronomy choices behind the AgroPilot daily irrigation plan (Kc by growth stage, soil bucket, irrigate-at-half rule, drip run time), with three hand-calculated cases. Use whenever you write, change, review or test the irrigation engine or the plan numbers in services/planner-service, or explain a plan value, so you do not re-derive the domain from memory.
---

# Irrigation calculation reference

The plan is the engine's output and nothing else: no AI model computes or adjusts an irrigation number. The engine is `services/planner-service/engine.py` (pure functions) and the crop numbers are in `crops.py`. The sources are in `services/planner-service/docs/research/fao56.md` (FAO-56, with chapter, table and equation numbers). Read that file before changing a number here. It also lists what could not be read, so check those against the printed book.

## Units

- Water is a depth in mm. 1 mm over 1 m² is 1 litre, so `litres = need_mm × area_m2`.
- ET0, rain, ETc, the bucket and the irrigation depth are all mm per day or mm, over the whole plot.
- Dates are `YYYY-MM-DD`. "Today" is the first date of the weather forecast, which is local to the plot.

## Formulas, in the order the engine uses them, for each forecast day

1. **Season day.** `day_number = (date - planting_date) + 1`. Planting day is day 1.
2. **Kc** (single crop coefficient, FAO-56 ch. 6, Eq. 66). Constant `kc_ini` up to `l_ini`. Then a straight line to `kc_mid` over `l_dev` days. Constant `kc_mid` over `l_mid` days. Then a straight line to `kc_end` over `l_late` days. After the season, hold `kc_end`.
   `kc = kc_prev + (day_number - days_before_stage) / stage_length × (kc_next - kc_prev)`
3. **Crop use.** `etc_mm = kc × et0_mm` (Eq. 56).
4. **Bucket size.** `capacity_mm = available_water_mm_per_m × root_depth_m` (Eq. 82). The root depth is in `crops.py` because the registry does not store it.
5. **Water bucket, one day** (`water_day`). Rain and irrigation come early in the morning, then the crop uses `etc_mm`.
   - `level = min(capacity, level_start + rain_mm)`. Rain above the top is lost.
   - If `level - etc_mm < 0.5 × capacity`, irrigate: `need_mm = capacity - level` and the bucket is refilled to the top (the book's `Ii = Dr`).
   - `bucket_end_mm = level - etc_mm`.
   - Exactly half is not below half, so no irrigation.
6. **Drip run time.** One emitter serves `row_spacing_m × emitter_spacing_m` m², so
   `run_minutes = need_mm × row_spacing_m × emitter_spacing_m / flow_lph × 60`. The plot area cancels out.

## Choices the book leaves open (change them in `crops.py` / `engine.py`, and in this file)

- The bucket is **full at the start of today**. The registry has no soil moisture.
- **Irrigate below half** of the bucket. FAO-56 says to use p per crop (tomato 0.40, pepper 0.30, Table 22). `p = 0.5` is only "commonly used". The task asked for half.
- Root depth is the small end of Table 22: tomato 0.7 m, pepper 0.5 m.
- Tomato `kc_end` 0.80, the middle of the printed range 0.70–0.90.
- Pepper `l_ini` 30 days (Table 11 prints "25/30"; 30 matches the printed total 125).
- After the end of the season the Kc stays at `kc_end`. The seed plots were planted months ago, so they are in this case.
- All rain counts. The book ignores rain under about 0.2 × ET0 and has no "effective rain" term.
- No Ks (stress) factor, no drip efficiency loss, no wetted-fraction correction of Kc.

## Three cases calculated by hand (they are tests in `tests/test_engine.py`)

**Case 1, Kc along the tomato season** (30 / 40 / 45 / 30 days, Kc 0.6 / 1.15 / 0.80). Day 50: `0.6 + (50-30)/40 × (1.15-0.6) = 0.875`. Day 100: `1.15`. Day 130: `1.15 + (130-115)/30 × (0.80-1.15) = 0.975`. Day 200: `0.80`.

**Case 2, pepper on sand, mid-season, irrigation on days 4 and 7.** Sand 83 mm/m × 0.5 m = 41.5 mm, half = 20.75. Mid Kc 1.05, ET0 6, so ETc 6.3. Days end at 35.2, 28.9, 22.6. Day 4 would end at 16.3, below 20.75, so the morning level 22.6 is refilled with 41.5 - 22.6 = **18.9 mm**. For 400 m², rows 1.2 m, emitters 0.3 m apart, 2 L/h: 18.9 × 400 = **7560 L** and `18.9 × 1.2 × 0.3 / 2 × 60 = 204.12 min`. Check: 400 / 0.36 = 1111.1 emitters × 2 L/h = 2222.2 L/h, and 7560 / 2222.2 × 60 = 204.12.

**Case 3, tomato in development on loam, 20 mm rain on day 3.** Loam 175 × 0.7 = 122.5 mm. Day 50 on day 1, ET0 4: Kc `0.6 + (day-30) × 0.01375` = 0.875 … 0.9575, ETc = 3.5, 3.555, 3.61, 3.665, 3.72, 3.775, 3.83 (sum 25.655). End of day 2: 122.5 - 3.5 - 3.555 = 115.445. Day 3: rain fills the bucket to 122.5 (the extra is lost), ends at 122.5 - 3.61 = 118.89. Day 7: 118.89 - 3.665 - 3.72 - 3.775 - 3.83 = **103.9 mm**. No irrigation.

Also the task's own example: a 70 mm bucket losing 7 mm a day ends days 1–5 at 63, 56, 49, 42, 35. Day 6 would end at 28, so it irrigates 35 mm.

## Tolerance

Calculated values must match these hand values within 0.5% (NFR-2.5). The API rounds to 1–3 decimals for display only.
