# FAO-56 research note: crop water need, Kc, soil bucket, Annex 8

Accessed: 2026-11-21. Only source: FAO Irrigation and Drainage Paper 56, "Crop evapotranspiration - Guidelines for computing crop water requirements".
Index: https://www.fao.org/3/x0490E/x0490e00.htm (redirects to http://www.fao.org/4/x0490E/x0490e00.htm).
Pages read: Ch. 5 `x0490e0a.htm`, Ch. 6 `x0490e0b.htm`, Ch. 8 `x0490e0e.htm`, Annex 8 `x0490e0p.htm` (all under http://www.fao.org/4/x0490E/).

Method note: pages were fetched as text and summarised by a tool. Equations rendered as images on the FAO page (Eq. 59, 61, 62, 65, 66, 84, 89 and some in Annex 8) were NOT readable. Where a formula is not given below, it is because it could not be read, not because it does not exist. Nothing here is filled in from memory unless marked "not verified".

Labels: **FAO states** = taken from the pages. **Interpretation** = my reading for the planner, not FAO text.

## Summary

- FAO states ETc = Kc x ET0 (FAO-56, Ch. 5, Eq. 56 in the Ch. 5 page; the same equation appears as Eq. 58 in the Ch. 6 page text).
- Tomato: Kc mid 1.15, Kc end 0.70-0.90, h 0.6 m (Table 12). Bell pepper: Kc mid 1.05, Kc end 0.90, h 0.7 m (Table 12). The Kc ini cells are images and could not be read.
- Stage lengths (Table 11) differ by region and planting date; there is no single value.
- Soil bucket (Ch. 8): TAW = 1000(FC - WP) Zr (Eq. 82); RAW = p TAW (Eq. 83); depletion balance Eq. 85; irrigate when depletion reaches RAW, with net depth no more than the depletion.
- Annex 8 is a DUAL Kc (Kcb + Ke) worked example with dry beans, not a single-Kc tomato/pepper example. Its irrigation rule is useful as a daily-step template.

## 1. From ET0 and Kc to crop water need

- ETc = Kc ETo, with ETc and ETo in mm/d and Kc dimensionless. Kc is the ratio ETc/ETo. (FAO-56, Ch. 5, Eq. 56)
- "The Kc in Equation 56 predicts ETc under standard conditions" (large fields, excellent agronomic and soil water conditions, no stress). (FAO-56, Ch. 5, "Crop coefficient approach")
- Single approach combines evaporation and transpiration in one Kc; suited to time-averaged calculation (weekly or longer) for planning, design and basic scheduling. Dual approach Kc = Kcb + Ke (Eq. 57) suits research, real-time scheduling and high-frequency irrigation, with a daily water balance. (FAO-56, Ch. 5, Table 10, Eq. 57)
- Standard climate: sub-humid, RHmin about 45%, wind about 2 m/s. (FAO-56, Ch. 5, "Climate")
- Non-standard conditions (stress, salinity, etc.): ETc adj = Ks Kc ETo (Eq. 81) or (Ks Kcb + Ke) ETo (Eq. 80). (FAO-56, Ch. 8, Eq. 80, 81)
- Ch. 6 text: ETc is computed by multiplying Kc values by the corresponding ETo values (for the period used). (FAO-56, Ch. 6)
- Net irrigation requirement: the pages I read do NOT define a "net irrigation requirement" quantity by name (Ch. 5 gave nothing). What Ch. 8 gives is the balance: irrigation is needed when rain cannot offset ET, and the net depth should be <= the root zone depletion (FAO-56, Ch. 8, "Forecasting or allocating irrigations", Eq. 85).
  - **Interpretation:** daily net need = ETc - effective rain (when the bucket is at or below field capacity), accumulated as depletion Dr; irrigation is the refill of Dr.

## 2. Tomato and bell pepper (Ch. 6)

URL: http://www.fao.org/4/x0490E/x0490e0b.htm

### Table 11, stage lengths in days (as printed)

| Crop | L ini | L dev | L mid | L late | Total | Plant date | Region |
|---|---|---|---|---|---|---|---|
| Tomato | 30 | 40 | 40 | 25 | 135 | January | Arid Region |
| Tomato | 35 | 40 | 50 | 30 | 155 | Apr/May | Calif., USA |
| Tomato | 25 | 40 | 60 | 30 | 155 | Jan | Calif. Desert, USA |
| Tomato | 35 | 45 | 70 | 30 | 180 | Oct/Nov | Arid Region |
| Tomato | 30 | 40 | 45 | 30 | 145 | April/May | Mediterranean |
| Sweet peppers (bell) | 25/30 | 35 | 40 | 20 | 125 | April/June | Europe and Medit. |
| Sweet peppers (bell) | 30 | 40 | 110 | 30 | 210 | October | Arid Region |

(FAO-56, Ch. 6, Table 11.) Footnote: lengths "are indicative of general conditions, but may vary substantially from region to region."

Stage definitions: initial = planting to about 10% ground cover; development = 10% to effective full cover; mid = full cover to start of maturity; late = start of maturity to harvest/senescence. (FAO-56, Ch. 5, "Crop growth stages")

### Table 12, Kc and height (as printed)

| Crop | Kc ini | Kc mid | Kc end | Max height h (m) |
|---|---|---|---|---|
| Solanaceae group row | 0.6 | 1.15 | 0.80 | blank |
| Sweet Peppers (bell) | image, unreadable | 1.05 (fn 2) | 0.90 | 0.7 |
| Tomato | image, unreadable | 1.15 (fn 2) | 0.70-0.90 | 0.6 |

(FAO-56, Ch. 6, Table 12.) The Kc ini cells of the individual crops were images. The only readable Kc ini value near them is the group row 0.6.
- **Interpretation (not verified):** the individual tomato and pepper Kc ini is probably 0.6 like the group row, but I could not confirm it. Check Table 12 on the page by eye.

### Footnotes and adjustments

- Kc ini footnote: "general values for Kc ini under typical irrigation management and soil wetting"; with frequent wetting (high-frequency sprinkler, rain) Kc ini "may increase substantially" and may approach 1.0 to 1.2. Kc ini ranges 0.1 to 1.15. (FAO-56, Ch. 6, Table 12 footnote 1, text on Kc ini)
- Footnote 2: beans, peas, legumes, tomatoes, peppers, cucumbers are sometimes grown on stalks 1.5-2 m high. Then for green beans, peppers and cucumbers Kc mid 1.15 can be taken, and for tomatoes 1.20; h should be increased too. (FAO-56, Ch. 6, Table 12 footnote 2)
- Kc mid and Kc end are for standard climate. Adjust when RHmin differs from 45% or u2 differs from 2.0 m/s, for h between 0.1 and 10 m (Eq. 62, formula not readable). (FAO-56, Ch. 6, Eq. 62)
- Kc end adjustment (Eq. 65) applies only if the tabulated Kc end exceeds 0.45; both tomato (0.70-0.90) and pepper (0.90) qualify. (FAO-56, Ch. 6, Eq. 65)
- Kc ini from wetting events: Figure 29 (light wetting 3-10 mm), Figure 30 (heavy wetting 40 mm or more; 30a coarse, 30b fine/medium soils); for average infiltration 10-40 mm interpolate (Eq. 59). (FAO-56, Ch. 6, Eq. 59, Fig. 29, 30)
- Drip remark: "Kc ini = fw Kc ini (Tab, Fig)" (Eq. 60) with fw the wetted surface fraction, e.g. "for a trickle irrigation system, the fraction of the surface wetted, fw, may be only 0.4"; wetted-part depth Iw = I/fw (Eq. 61). (FAO-56, Ch. 6, Eq. 60, 61)
  - Footnote 16 about drip under plastic mulch (Kc reduced by 0.10) is for pineapple only, not tomato or pepper. (FAO-56, Ch. 6, Table 12)

### Curve construction (daily planner relevance)

- Horizontal lines at Kc ini (initial stage) and Kc mid (mid stage); Kc varies linearly between Kc at the end of the previous stage and Kc at the start of the next during development and late stages; Eq. 66 "applies to all four stages". (FAO-56, Ch. 6, Eq. 66, Figure 25 as referenced, Figure 34 "Crop coefficient curve", Figure 33 ranges for Kc end)
- Kc is multiplied by the daily ETo of the matching day. (FAO-56, Ch. 6)

### Ambiguities

- Name: Table 12 and 11 say "Sweet Pepper (bell)" / "Sweet peppers (bell)". No separate bell pepper row exists in what I read.
- Dry vs fresh fruit: not distinguished in the tomato/pepper rows I read.
- Two Kc end values for tomato (0.70-0.90): range, no rule given to pick one.
- Table 11 pepper L ini "25/30" is printed as two values; no explanation read.
- Table 11 has 5 tomato and 2 pepper rows by region/date; picking a row is a choice for the user.

## 3. Soil bucket (Ch. 8)

URL: http://www.fao.org/4/x0490E/x0490e0e.htm

FAO states:
- TAW = 1000 (thetaFC - thetaWP) Zr, in mm, theta in m3/m3, Zr in m. (FAO-56, Ch. 8, Eq. 82)
- RAW = p TAW. (FAO-56, Ch. 8, Eq. 83)
- Table 22: Tomato Zr 0.7-1.5 m, p = 0.40; Sweet Peppers (bell) Zr 0.5-1.0 m, p = 0.30. (FAO-56, Ch. 8, Table 22)
- Table 22 footnote 2: p values apply for ETc of about 5 mm/day; adjust p = p(Table 22) + 0.04 (5 - ETc), ETc in mm/d. (FAO-56, Ch. 8, Table 22 fn 2)
- Ks: equals 1 when Dr <= RAW; when Dr > RAW it is a factor between 0 and 1 using TAW, Dr and p (Eq. 84, formula image NOT readable). (FAO-56, Ch. 8, Eq. 84)
  - Annex 8 describes the same Eq. 84 shape as (TAW - Dr) over a term with RAW, but its rendering was garbled; not verified. (FAO-56, Annex 8, Ks)
- Adjusted ET: ETc adj = (Ks Kcb + Ke) ETo (Eq. 80); ETc adj = Ks Kc ETo (Eq. 81). (FAO-56, Ch. 8)
- Daily balance at end of day: Dr,i = Dr,i-1 - (P - RO)i - Ii - CRi + ETc,i + DPi (Eq. 85); limits 0 <= Dr,i <= TAW (Eq. 86). (FAO-56, Ch. 8)
- Initial depletion: Dr,i-1 = 1000 (thetaFC - theta i-1) Zr (Eq. 87); the user may assume near field capacity after heavy rain or irrigation. (FAO-56, Ch. 8, Eq. 87)
- Deep percolation: DPi = (Pi - ROi) + Ii - ETc,i - Dr,i-1, >= 0, occurring while the root zone is above field capacity (Eq. 88). (FAO-56, Ch. 8, Eq. 88)
- Rain: daily precipitation below about 0.2 ETo is normally evaporated and can usually be ignored; runoff by standard hydrology methods. (FAO-56, Ch. 8, "Effective rain")
- Irrigation I is the mean infiltrated depth over the entire field surface. CR can usually be taken as 0 when the water table is more than about 1 m below the root zone. (FAO-56, Ch. 8)
- Scheduling: irrigate before or when readily available water is depleted (Dr <= RAW kept); net depth should be <= root zone depletion (Ii <= Dr,i) to limit deep percolation. (FAO-56, Ch. 8, "Forecasting or allocating irrigations", Example 38)
- Partial wetting / localized irrigation: not covered in the Ch. 8 text I read. Only note: high-frequency surface irrigation raises soil evaporation. (FAO-56, Ch. 8)

Not retrieved: Table 19 (theta FC/WP by soil type) and the exact Eq. 84 and 89.

**Interpretation:** the planner's "irrigate at half" rule, if used, corresponds to p = 0.5 and is not a FAO value for tomato (0.40) or pepper (0.30). Note also that ETc in Eq. 85 is the unstressed ETc when depletion is below RAW, and ETc adj afterwards.

## 4. How Annex 8 schedules day by day

URL: http://www.fao.org/4/x0490E/x0490e0p.htm

FAO states (FAO-56, Annex 8):
- It is a spreadsheet example of the DUAL Kc procedure (Ch. 7) plus the Ch. 8 water balance, for DRY EDIBLE BEANS (not tomato or pepper). Planted 22 May, stages 25/25/30/20 days, Kcb ini 0.15, Kcb mid 1.1, Kcb end 0.25, h max 0.4 m, TEW 22 mm, REW 8 mm, available water 160 mm/m, root 0.2 to 0.8 m, MAD 70% in initial stage and 45% afterwards, fw irrigation 0.5.
- Annex assumes p = MAD. Irrigation efficiency is not modelled; the irrigator is assumed to know the depletion perfectly. Drip is not mentioned; fw = 0.5 is the only method parameter.
- Authors warn the cell formulas contain inconsistent references and a hard-coded value (16 in J6), so check before reuse.

Order of daily calculations (from the footnotes, FAO-56, Annex 8, Box 8.1):
1. Kcb from growth stage, linear interpolation in development and late stages (Eq. 70 adjusted for u2, RHmin).
2. Crop height from Kcb, never decreasing.
3. Irrigation (and rain) are assumed to arrive early morning, based on the previous day's end depletion.
4. fw set from the last rain or irrigation event; few = smaller of (1 - fc) and fw (Eq. 75).
5. Evaporation-layer depletion De at start of day = previous end value minus water input, >= 0.
6. Kr (Eq. 71), Ke (limited by few x Kc max), soil evaporation, De at end of day (Eq. 77).
7. Kc = Kcb + Ke (Eq. 69); ETc = Kc x ETo.
8. Root depth Zr grows with Kcb, never decreasing; reaches max at start of mid-season; RAW computed from it.
9. First estimate of end-of-day Dr with zero drainage and unstressed ETc, then recomputed after drainage and Ks.
10. Net irrigation for the next day set from end-of-day depletion.
11. Ks from depletion (Ks = 1 when Dr does not exceed RAW).

Trigger and amount:
- Trigger: the previous day's ending depletion exceeded RAW. Irrigation applied at the start of the next day. (FAO-56, Annex 8, footnote 10)
- Net amount: exactly equal to that depletion (refills to field capacity). The depth applied to the wetted part is divided by fw (Eq. 76). (FAO-56, Annex 8)
- No irrigation in the last half of the late season (last irrigation day 225). (FAO-56, Annex 8, footnote 10)
- Rain: runoff assumed zero; excess drains the same day (deep percolation computed afterward). (FAO-56, Annex 8)
- Tolerances: authors say small differences arise from irrigation-timing assumptions.

**Interpretation:** for a single-Kc planner, steps 4-6 (Ke, few, De) can be dropped and Kc taken from Table 12 curve; steps 8-11 and the trigger/amount rule are directly reusable. Apply order: carry yesterday's Dr, decide irrigation for today, add today's rain, subtract ETc adj, clip to 0..TAW, record DP.

## 5. Where drip / partial wetting changes things

- Kc ini scaled by fw (Eq. 60) and wetting depth Iw = I/fw (Eq. 61). (FAO-56, Ch. 6)
- Annex 8 divides applied depth by fw (Eq. 76) and limits exposed wet soil few. (FAO-56, Annex 8)
- Ch. 8 text read gives no drip-specific bucket rule; that is a gap. (FAO-56, Ch. 8)
- **Interpretation:** whether TAW should use the wetted volume only is a design choice not decided by the pages read.

## 6. Open questions / ambiguities

1. Kc ini for tomato and bell pepper in Table 12: image cells, unread (group row 0.6 only).
2. Exact formulas for Eq. 59, 61, 62, 65, 66, 84, 89 not readable from text.
3. Which Table 11 row (region/date) applies to the user's farms; Table 11 pepper L ini "25/30".
4. Tomato Kc end 0.70-0.90: which value.
5. Eq. numbering: Ch. 5 page labels ETc = Kc ETo as Eq. 56, the Ch. 6 page as Eq. 58; I did not resolve which is canonical.
6. Annex 8 uses dry beans and dual Kc, so numbers there do not transfer to tomato or pepper.
7. Table 19 (soil water values) and any drip guidance in Ch. 8 were not retrieved.
8. Ch. 5 and 6 text for Table 10, Figure 25 caption, Figure 34 were referenced but not fully read.
