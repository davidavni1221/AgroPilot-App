# FAO-56 research notes for a daily drip-irrigation planner

Source: FAO Irrigation and Drainage Paper 56 (Allen, Pereira, Raes, Smith, 1998), HTML edition at https://www.fao.org/3/x0490e/. Fetched 2026-11-16. Every number below was read from the fetched pages. Numbers in quotation marks are as printed.

Scope notes (read first):

- File map from the contents page: ch. 5 = `x0490e0a.htm`, ch. 6 = `x0490e0b.htm`, ch. 7 = `x0490e0c.htm`, ch. 8 = `x0490e0e.htm`, Annex 1 = `x0490e0i.htm`, Annex 8 = `x0490e0p.htm`.
- Annex 8 is titled "Calculation example for applying the dual Kc procedure in irrigation scheduling". It is NOT a single-Kc example. It is a dual-Kc (Kcb + Ke) spreadsheet for dry edible beans, not tomato or pepper.
- Several equations are embedded as GIF images and the image files could not be fetched (the server returns an HTML error page for them). Those are marked "NOT READ (image)". Where a worked example in the book prints the numbers, this is said explicitly.
- Table 20 (fw values) and Eq. 75 are in chapter 7, not in the requested chapters. They are included because chapters 6 and 8 and Annex 8 refer to them.

---

## 1. From ET0 and Kc to crop water need (ETc), and how rain enters

| Item | What the book says | Cite |
|---|---|---|
| Single Kc equation | "ETc = Kc ETo (56)", ETc, ETo in mm d-1, Kc dimensionless. Repeated as "ETc = Kc ETo (58)" | Ch. 5, "Crop coefficient approach", Eq. 56; Ch. 6 intro, Eq. 58 |
| Meaning | Kc integrates crop height, albedo, canopy resistance and soil evaporation. It gives ETc under "standard conditions" (no water, salinity, disease or density limits). Non-standard conditions are corrected to ETc adj (Part C) | Ch. 5 |
| Single vs dual | Single Kc is a time-averaged coefficient. It "expresses only the time-averaged (multi-day) effects of crop evapotranspiration" | Ch. 5, "Single crop coefficient approach" |
| Which approach for drip | Table 10 lists "irrigation scheduling for high frequency water application (microirrigation and automated sprinkler irrigation)" under the DUAL coefficient (Kcb + Ke) column. The single Kc column lists "irrigation planning and design", "irrigation management", "basic irrigation schedules" and non-frequent surface or sprinkler application. Ch. 5 also says the dual procedure "is the case for high frequency irrigation with microirrigation systems" | Ch. 5, Table 10 and "Dual crop coefficient approach" |
| Dual equation | "Kc = Kcb + Ke (57)". Dual stress form: "ETc adj = (Ks Kcb + Ke) ETo (80)" | Ch. 5 Eq. 57; Ch. 8 Eq. 80 |
| Stress with single Kc | "ETc adj = Ks Kc ETo (81)". The book says Eq. 80 is "generally more valid" because Ks only affects transpiration, but Eq. 81 gives "reasonable results" when soil evaporation is not a large part of ETc | Ch. 8 intro, Eq. 81 |
| Calculation procedure (single Kc) | (1) identify stages, lengths and Kc; (2) adjust Kc for wetting frequency and climate; (3) construct the Kc curve; (4) ETc = Kc x ETo | Ch. 6 intro |

### Rain and effective rainfall

- The term "effective rainfall" is NOT FOUND in chapters 5, 6, 7, 8 or Annex 8. The book does not use a coefficient-style "effective rain". It handles rain physically in the soil water balance, as P minus runoff, with excess above field capacity lost as deep percolation (Eq. 85, 88; section 4 below).
- Rain in the balance: "Pi is equivalent to daily precipitation. Daily precipitation in amounts less than about 0.2 ETo is normally entirely evaporated and can usually be ignored in the water balance calculations especially when the single crop coefficient approach is being used." (Ch. 8, "Precipitation (P), runoff (RO) and irrigation (I)")
- "Runoff from the surface during precipitation can be predicted using standard procedures from hydrological texts." No runoff formula is given in ch. 8. Annex 8 assumes "runoff from precipitation is zero". (Ch. 8; Annex 8 intro)
- Rain also changes Kc through surface wetting (Ch. 5, "Soil evaporation" and "Initial stage", Table 9; Ch. 6, "Crop coefficient for the initial stage"). With the single Kc this is only an average. With the dual approach it is computed daily (Ke, chapter 7).
- Ch. 6 says "For frequent irrigation of crops (more frequently than every 3 days) and where the Kc mid of Table 12 is less than 1.0, the value can be replaced by approximately 1.1-1.3 ... especially where the irrigation system moistens an important fraction of the soil surface (fw > 0.3)." (Ch. 6, "Adjustment for frequency of wetting")

---

## 2. Kc values and stage lengths: tomato and bell pepper

### Growth stages (Ch. 5, "Crop growth stages", Fig. 23, Fig. 24, Fig. 25)

| Stage | Definition as printed |
|---|---|
| Initial | "runs from planting date to approximately 10% ground cover" |
| Crop development | "runs from 10% ground cover to effective full cover" (about fc 0.7-0.8 for crops taller than 0.5 m) |
| Mid-season | "runs from effective full cover to the start of maturity" |
| Late season | "runs from the start of maturity to harvest or full senescence" |

### Table 11 (Ch. 6): lengths of crop development stages, days

Rows as printed. "Total" is the book's column.

| Crop | Lini | Ldev | Lmid | Llate | Total | Plant date | Region |
|---|---|---|---|---|---|---|---|
| Sweet peppers (bell) | 25/30 | 35 | 40 | 20 | 125 | April/June | Europe and Medit. |
| Sweet peppers (bell) | 30 | 40 | 110 | 30 | 210 | October | Arid Region |
| Tomato | 30 | 40 | 40 | 25 | 135 | January | Arid Region |
| Tomato | 35 | 40 | 50 | 30 | 155 | Apr/May | Calif., USA |
| Tomato | 25 | 40 | 60 | 30 | 155 | Jan | Calif. Desert, USA |
| Tomato | 35 | 45 | 70 | 30 | 180 | Oct/Nov | Arid Region |
| Tomato | 30 | 40 | 45 | 30 | 145 | April/May | Mediterranean |

Notes on Table 11:

- The first pepper row prints Lini as "25/30". The book does not explain the slash. The total 125 = 25+35+40+20, so 25 is the value that matches the total.
- Table footnote: "Lengths of crop development stages provided in this table are indicative of general conditions, but may vary substantially from region to region, with climate and cropping conditions, and with crop variety. The user is strongly encouraged to obtain appropriate local information."
- Text: "The values in Table 11 are useful only as a general guide and for comparison purposes ... Local observations of the specific plant stage development should be used, wherever possible." Primary source is given as FAO-24 (Doorenbos and Pruitt, 1977), Table 22.

### Table 12 (Ch. 6): Kc and maximum height

Subhumid climate (RHmin about 45%, u2 about 2 m/s). Table 12 has a group row "b. Vegetables - Solanum Family (Solanaceae)" with "0.6 | 1.15 | 0.80" and individual rows with an empty first cell. In the HTML the column header cell for Kc ini is blank, and the individual rows leave Kc ini blank. I read the group row as Kc ini = 0.6, Kc mid = 1.15, Kc end = 0.80 for the whole Solanum family (the same pattern as other groups, for example small vegetables 0.7 / 1.05 / 0.95). The book gives one Kc ini for the group: ch. 6 says "For several group types only one value for Kc ini is listed and it is considered to be representative of the whole group". Verify against the printed book.

| Crop | Kc ini | Kc mid | Kc end | Max height h (m) |
|---|---|---|---|---|
| Sweet Peppers (bell) | 0.6 (group value) | "1.05" (footnote 2) | 0.90 | 0.7 |
| Tomato | 0.6 (group value) | "1.15" (footnote 2) | "0.70-0.90" | 0.6 |

- Footnote 1 to Table 12 on Kc ini: "These are general values for Kc ini under typical irrigation management and soil wetting. For frequent wettings such as with high frequency sprinkle irrigation or daily rainfall, these values may increase substantially and may approach 1.0 to 1.2. Kc ini is a function of wetting interval and potential evaporation rate ... and is more accurately estimated using Figures 29 and 30, or Equation 7-3 in Annex 7, or using the dual Kcb ini + Ke."
- Footnote 2: "Beans, Peas, Legumes, Tomatoes, Peppers and Cucumbers are sometimes grown on stalks reaching 1.5 to 2 meters in height. In such cases, increased Kc values need to be taken. For green beans, peppers and cucumbers, 1.15 can be taken, and for tomatoes, dry beans and peas, 1.20. Under these conditions h should be increased also."
- Tomato Kc end is a range "0.70-0.90". The book does not say which end of the range applies. The engine author must choose.
- Table 12 text: Kc mid and Kc end are for "a sub-humid climate with an average daytime minimum relative humidity (RHmin) of about 45% and with calm to moderate wind speeds averaging 2 m/s", and should be modified using Eq. 62 and Eq. 65 otherwise (Ch. 6, "Crop coefficient for the mid-season stage", "... end of the late season stage").
- Eq. 62 (Kc mid climate adjustment) and Eq. 65 (Kc end adjustment): NOT READ (images x0490e2d.gif, x0490e2i.gif). Printed constraints: Eq. 62 inputs u2 (1 to 6 m/s), RHmin (20 to 80%), h (0.1 to 10 m). Eq. 65 applies only when tabulated Kc end >= 0.45, and "No adjustment is made when Kc end (Table) < 0.45". The same adjustment is visible in Annex 8, Box 8.1, cell J5 (this is Eq. 70 for Kcb in ch. 7, same form): `I5+(0.04*($K$8 - 2)-0.004*($K$9 - 45))*($M$5/3)^0.3`. That is the Kcb version, not the Kc version, so do not copy it into a single-Kc engine without checking the Eq. 62 image.

### Kc ini correction for partial wetting (Ch. 6, Eq. 60 and 61)

See section 5.

### Daily interpolation of Kc (Ch. 6, "Construction of the Kc curve" and "Numerical determination of Kc", Fig. 25, Fig. 34, Eq. 66)

- Curve construction (Ch. 6, "Annual crops"): "Horizontal lines are drawn through Kc ini in the initial stage and through Kc mid in the mid-season stage. Diagonal lines are drawn from Kc ini to Kc mid within the course of the crop development stage and from Kc mid to Kc end within the course of the late season stage." Fig. 25 (ch. 5) shows the generalized curve and Fig. 34 (ch. 6) the constructed curve.
- Numerical rule (Ch. 6): "during the initial and mid-season stages Kc is constant and equal to the Kc value of the growth stage under consideration. During the crop development and late season stage, Kc varies linearly between the Kc at the end of the previous stage (Kc prev) and the Kc at the beginning of the next stage (Kc next), which is Kc end in the case of the late season stage."
- Eq. 66 itself is an image: NOT READ. Its variables are printed: i = day number within the growing season [1 .. length of the growing season]; Kc i; Lstage = length of the stage; Sum(Lprev) = sum of lengths of all previous stages. "Equation 66 applies to all four stages."
- The form can be taken from the book's own worked arithmetic in Example 28 (not from the image):
  - Development, day 40, Sum(Lprev) = 25, Lstage = 25: "Kc = 0.15 + [(40 - 25)/25](1.19 - 0.15) = 0.77"
  - Late, day 95, Sum(Lprev) = 80, Lstage = 20: "Kc = 1.19 + [(95-80)/20](0.35-1.19) = 0.56"
  - Initial day 20: 0.15. Mid day 70: 1.19. (Example 28 uses stage lengths 25 / 25 / 30 / 20 and Kc 0.15 / 1.19 / 0.35, dry beans.)
  - In general: Kc_i = Kc_prev + [(i - Sum(Lprev)) / Lstage] x (Kc_next - Kc_prev). Day numbering starts at 1 at planting (variable range printed as [1..length]).
- The same linear interpolation appears in Annex 8, Box 8.1, cell O14 (for Kcb, Eq. 66): `IF(D14<$Q$4,$J$4, IF(D14<$Q$5,$J$4+(D14-$Q$4)/$F$5*($J$5-$J$4), IF(D14<$Q$6,$J$5, IF(D14<$Q$7,$J$5+(D14-$Q$6)/$F$7*($J$6-$J$5),$J$4))))`. Here D = day of year, Q4 = start of development, Q5 = start of mid, Q6 = start of late, Q7 = harvest. Note that on the day after harvest it returns Kcb ini. Note also that this uses `D - start` without +1 or -1 offsets.

---

## 3. Soil bucket: TAW, root depth, p, RAW, Dr, stress threshold

| Quantity | Equation / statement | Cite |
|---|---|---|
| TAW | "TAW = 1000(theta_FC - theta_WP) Zr (82)", TAW in mm, theta in m3 m-3, Zr in m | Ch. 8, "Total available water (TAW)", Eq. 82 |
| Root depth | Zr = rooting depth [m]. Range of maximum effective root depth per crop in Table 22 | Ch. 8, Eq. 82, Table 22 |
| RAW | "RAW = p TAW (83)". p is the "average fraction of Total Available Soil Water (TAW) that can be depleted from the root zone before moisture stress (reduction in ET) occurs [0-1]" | Ch. 8, "Readily available water (RAW)", Eq. 83 |
| p range | "normally varies from 0.30 for shallow rooted plants at high rates of ETc (> 8 mm d-1) to 0.70 for deep rooted plants at low rates of ETc (< 3 mm d-1). A value of 0.50 for p is commonly used for many crops." | Ch. 8, RAW section |
| p vs ETc | Table 22 p applies for ETc about 5 mm/day. "A numerical approximation for adjusting p for ETc rate is p = pTable 22 + 0.04 (5 - ETc) where the adjusted p is limited to 0.1 <= p <= 0.8 and ETc is in mm/day." Same formula in Table 22 footnote 2. See Fig. 41 | Ch. 8, RAW section; Table 22 fn. 2; Fig. 41 |
| p vs soil | "for fine textured soils (clay) the p values listed in Table 22 can be reduced by 5-10%, while for more coarse textured soils (sand), they can be increased by 5-10%" | Ch. 8, text after Example 36 |
| Depletion Dr | "root zone depletion, Dr, i.e., water shortage relative to field capacity. At field capacity, the root zone depletion is zero (Dr = 0)". Limits: "0 <= Dr, i <= TAW (86)" | Ch. 8, "Water stress coefficient (Ks)"; "Limits on Dr, i", Eq. 86 |
| Stress threshold | "stress will be induced when Dr becomes equal to RAW. After the root zone depletion exceeds RAW (the water content drops below the threshold theta_t) ... the crop evapotranspiration begins to decrease in proportion to the amount of water remaining in the root zone (Figure 42)" | Ch. 8, Ks section, Fig. 42 |
| Ks | "When the root zone depletion is smaller than RAW, Ks = 1." For Dr > RAW, Ks from Eq. 84. Eq. 84 is an image: NOT READ. Variables printed: Ks, Dr, TAW, p | Ch. 8, Eq. 84 |
| Ks check | Annex 8 Box 8.1 cell AJ14 prints it: `IF(AG14>AF14,(AE14*AF$5-AG14)/(AE14*AF$5-AF14),1)`, i.e. Ks = (TAW - Dr) / (TAW - RAW) when Dr > RAW, else 1. Example 37 (ch. 8) numbers agree: Dr = 67, TAW = 160, RAW = 64 gives Ks "0.97" | Annex 8 Box 8.1, AJ14; Ch. 8 Ex. 37 |
| Initial depletion | "Dr, i-1 = 1000(theta_FC - theta_i-1) Zr (87)". "Following heavy rain or irrigation, the user can assume that the root zone is near field capacity, i.e., Dr, i-1 = 0." | Ch. 8, "Initial depletion", Eq. 87 |

### Table 22 (Ch. 8): root depth and p for tomato and bell pepper

| Crop | Maximum root depth (m) | Depletion fraction p (for ET about 5 mm/day) |
|---|---|---|
| Sweet Peppers (bell) | "0.5-1.0" | "0.30" |
| Tomato | "0.7-1.5" | "0.40" |

Table 22 footnote 1: "The larger values for Zr are for soils having no significant layering or other characteristics that can restrict rooting depth. The smaller values for Zr may be used for irrigation scheduling and the larger values for modeling soil water stress or for rainfed conditions."

Example 37 (ch. 8) uses a full-grown tomato with "Zr = 0.8 m and p = 0.40" on a silty soil (theta_FC 0.32, theta_WP 0.12): TAW = 160 mm, RAW = 64 mm. These soil values are for that example only. Typical theta_FC and theta_WP by texture are in Table 19 (ch. 8), not extracted here.

### Management allowed depletion (MAD) versus p versus "half"

- Book text (Ch. 8, after Example 36): "RAW is similar to the term Management Allowed Depletion (MAD) introduced by Merriam However, values for MAD are influenced by management and economic factors in addition to the physical factors influencing p. Generally, MAD < RAW where there is risk aversion or uncertainty, and MAD > RAW where plant moisture stress is an intentional part of soil water management."
- Irrigation rule (Ch. 8, "Forecasting or allocating irrigations"): "To avoid crop water stress, irrigations should be applied before or at the moment when the readily available soil water is depleted (Dr, i <= RAW)." As printed this reads "Dr,i <= RAW" (that is, applied before Dr exceeds RAW). Stated as a trigger: irrigate when depletion reaches RAW = p x TAW.
- Relation to "irrigate when the bucket falls below half": the book never states a "half" rule as such. It only says "A value of 0.50 for p is commonly used for many crops" (Ch. 8, Eq. 83 text). So "irrigate at half" equals the book's rule only when p = 0.5, because then RAW = 0.5 TAW, meaning 50% of TAW has been used up and 50% remains.
- With the Table 22 values at ET about 5 mm/day:
  - tomato p = 0.40: irrigate when Dr reaches 0.40 TAW (60% of TAW still in the bucket). This is wetter than "half".
  - bell pepper p = 0.30: irrigate when Dr reaches 0.30 TAW (70% of TAW still in the bucket). This is wetter than "half".
  - So a "half" rule lets these two crops dry beyond RAW into the stress zone (Ks < 1 per Eq. 84) before irrigating. (This is my reading of the numbers above, not a book statement.)
- In Annex 8, MAD is an input in percent: "MAD during Initial Stage" = 70 (%) and "MAD after Initial Stage" = 45 (%) (Box 8.1, cells AK3, AK4), with the statement "In this example, it is assumed that p = MAD." and "The allowable depletion is the same as the readily available water (RAW) when it is assumed that MAD = p". (Annex 8 text after Table 8.1; footnote 11.) In the formula for allowable depletion (AF14) MAD/100 is multiplied by available water and root depth, so MAD is a depletion fraction of TAW, the same meaning as p.

---

## 4. Daily scheduling (Ch. 8 water balance and Annex 8 spreadsheet)

### Daily balance (Ch. 8, "Soil water balance", Fig. 43)

"Dr, i = Dr, i-1 - (P - RO)i - Ii - CRi + ETc, i + DPi (85)"

Terms (all mm, for day i): Dr,i depletion at end of day i; Dr,i-1 depletion at end of previous day; P precipitation; RO runoff; I "net irrigation depth on day i that infiltrates the soil"; CR capillary rise; ETc,i crop evapotranspiration; DP deep percolation out of the root zone.

| Eq. | Statement | Cite |
|---|---|---|
| 85 | Daily balance above | Ch. 8 |
| 86 | "0 <= Dr, i <= TAW" | Ch. 8, "Limits on Dr, i" |
| 87 | "Dr, i-1 = 1000(theta_FC - theta_i-1) Zr" | Ch. 8, "Initial depletion" |
| 88 | "DPi = (Pi - ROi) + Ii - ETc, i - Dr, i-1 >= 0". Soil is assumed back at field capacity the same day: "the total amount of water above field capacity is assumed to be lost the same day by deep percolation, following any ET for that day" and "As long as the soil water content in the root zone is below field capacity (i.e., Dr, i > 0), the soil will not drain and DPi = 0" | Ch. 8, "Deep percolation (DP)" |
| 80 / 81 | ETc adj with Ks (section 1). "Where the soil water depletion is smaller than RAW, the crop evapotranspiration equals ETc = Kc ETo. As soon as Dr, i exceeds RAW, the crop evapotranspiration is reduced" | Ch. 8, "Evapotranspiration (ETc)" |
| CR | "CR can normally be assumed to be zero when the water table is more than about 1 m below the bottom of the root zone" | Ch. 8, "Capillary rise (CR)" |

### Trigger and amount (Ch. 8, "Forecasting or allocating irrigations")

- Timing: "irrigations should be applied before or at the moment when the readily available soil water is depleted (Dr, i <= RAW)".
- Amount: "To avoid deep percolation losses that may leach relevant nutrients out of the root zone, the net irrigation depth should be smaller than or equal to the root zone depletion (Ii <= Dr, i)."
- Example 38 (Ch. 8) plans irrigation "when RAW is depleted", p = 0.6, with "all irrigations and precipitations occur early in the day", Zr 0.3 m on day 1 rising to 0.35 m by day 10, and initial depletion Dr = RAW. The book's table for Example 38 was not transcribed here.

### How the Annex 8 spreadsheet does it (Annex 8 text, Box 8.1, Fig. 8.1)

Stated assumptions (Annex 8 intro):

- "all irrigation and precipitation events occur early in the morning."
- "The scheduling and magnitudes of irrigations are based on the soil water depletion at the end of the previous day."
- "all drainage from the root zone due to excess precipitation occurs on the day of the precipitation event."
- "runoff from precipitation is zero".
- "the net depth of irrigation that is retained in the crop root zone is exactly equal to the depletion depth of the previous day. This assumption presumes perfect knowledge of soil water depletion by the irrigator or that all irrigations are adequate or excessive."

Column logic from Box 8.1 (row 14, Excel, with the book's equation tags). Column letters are the book's; names are inferred from the formulas and footnotes, because the figure header row was not readable in the HTML:

| Step | Formula as printed (row 14) | Book tag |
|---|---|---|
| Daily Kcb | piecewise linear, see section 2 | Eq. 66 |
| First estimate of end-of-day depletion, no drainage, no stress | AG14: `= $X$6 - L14 + AC14` (initial depletion - precipitation + non-stressed ETc), where AC14 = AB14*H14 (Kc x ETo) | Eq. 85 (9) |
| RAW (allowable depletion) | AF14: `MAX(IF(D14<Q$4, AK$3, AK$4)/100*AE14*$AF$5, AF13)`, i.e. MAD fraction x root depth x available water (160 mm/m), never decreasing | Eq. 82 (with 83) |
| Irrigation decision | AH14: `IF(D14>=Q$3, IF(D14<(Q$6+Q$7)/2, IF(AG14>AF14, AG14, 0), 0), 0)`. Irrigate only if the day is in the irrigation window (planting to the middle of the late season) and the first-estimate depletion exceeds RAW. The amount is the whole depletion AG14 | Footnote (10) |
| Drainage | AI14: `MAX(+L14 - AC14 - $X$6, 0)` (precipitation - ETc - previous depletion, floored at 0) | Eq. 88 |
| Ks | AJ14: see section 3 | Eq. 84 (11) |
| Stressed ETc | AK14: `X14 + O14*AJ14` (Ke + Kcb x Ks) | Eq. 80 |
| End-of-day depletion | the final Dr column: `= +$X$6 - L14 + AK14*H14 + AI14` (previous depletion - rain + ETc adj + drainage) | Eq. 85 (9)(12) |

Footnote (10), printed: "The net depth of irrigation needed is based on the value of soil water depletion at the end of the day. It is assumed that irrigation will be applied at the beginning of the following day. The formula in column AH checks to insure that the specific day is within the growing period. The formula assumes that no irrigation will be desired during the last one-half of the late-season period."

Footnote (4): "The value for irrigation depth (divided by fw to express the depth over the wetted fraction of the soil, only) is presumed to occur early in the day. This value is based on a decision made at the end of the previous day (column AH), based on whether or not the ending soil water depletion on the previous day has exceeded the readily available water (RAW). The irrigation depth on the first day is presumed to be zero."

Annex 8 text on the trigger: "irrigations are not applied in the spreadsheet until the the soil water depletion at the end of the previous day is greater than or equal to RAW occasionally causes a small amount of stress on the day prior to irrigation".

Other printed Annex 8 details:

- Root depth grows with Kcb: Eq. 8-1 and 8-3 are images (NOT READ). Eq. 8-2 is printed: "Zr i = Zr max for J >= Jmid". Text: "Equations 8-1 and 8-2 presume that the development of the root zone increases in proportion to the increase in Kcb." Rootmin 0.2 m and Rootmax 0.8 m are inputs for beans (Box 8.1 AF3, AF4). "Zr min for annual crops should represent the depth of seed placement plus an additional depth of soil ... For many annual crops, Zr min can be estimated as 0.15 to 0.20 m." Root depth is never allowed to decrease (footnote 8).
- MAD during initial stage is larger than later: "to account for the ability of roots for some crops to extract water at relatively dry water contents during germination and during the initial period with little impact by stress."
- Note the Excel test in AH14 is `AG14 > AF14` (strictly greater), while the text says "greater than or equal to RAW". Minor, but decide which for the engine.
- Formulas for rows after row 14 are described only as "similar" (Box 8.1 "All rows below row 15 are similar"). The R column (irrigation applied on day i, from AH of day i-1) is not printed as a formula in the HTML for row 15. The summary above is therefore from the footnotes. Verify against Fig. 8.1.
- The Annex 8 crop is dry beans. The Annex 8 Figure 8.1 numeric table was not extracted. Nothing in the annex is tomato or pepper data.

---

## 5. Drip conversions, wetted fraction (fw) and fraction covered (fc)

### Unit conversion

- "1 mm over 1 m2 = 1 litre": NOT FOUND stated in chapters 5, 6, 8 or Annex 8. Searched those pages for "litre"/"liter" with no hit.
- Annex 1 (Units and symbols, `x0490e0i.htm`, "Evapotranspiration"): "1 m3 ha-1 day-1 = 0.1 mm day-1" and "1 l s-1 ha-1 = 8.640 mm day-1". From the first, 1 mm = 10 m3/ha = 10 000 L/ha = 1 L/m2. That is arithmetic from the book's own conversion, not a book statement.

### Partial wetting by drip (Ch. 6, "Adjustment for partial wetting by irrigation", Eq. 60, 61, Ex. 26, Fig. 31)

- "Many types of irrigation systems wet only a fraction of the soil surface. For example, for a trickle irrigation system, the fraction of the surface wetted, fw, may be only 0.4. For furrow irrigation systems, the fraction of the surface wetted may range from 0.3 to 0.8. Common values ... are given in Table 20."
- "Kc ini = fw Kc ini (Tab, Fig) (60)", fw "the fraction of surfaced wetted by irrigation or rain [0 - 1]". This applies to Kc ini only (initial stage), not to Kc mid or Kc end.
- Eq. 61 (image, NOT READ) defines Iw, "irrigation depth for the part of the surface that is wetted [mm]", from fw and I, "the irrigation depth for the field". Example 26 prints the arithmetic: "lw = I/fw = 12 mm/0.4 = 30 mm". Text: "the average infiltrated depth, expressed in millimetres over the entire field surface, should be divided by fw to represent the true infiltrated depth of water for the part of the surface that is wetted".
- Example 26: trickle every two days, 12 mm per application "expressed as an equivalent depth over the field area", fw 0.4, ETo 4 mm/day, Kc ini from Fig. 29 = 0.85 and from Fig. 30.b = 1.15, Eq. 59 gives "1.05", Eq. 60 gives "0.4 (1.05) = 0.42" and "ETc = Kc ini ETo = 0.42(4) = 1.7 mm/day". The 0.42 "represents the Kc ini as applied over the entire field area".
- Mixed wetting: "When irrigation of part of the soil surface and precipitation over the entire soil surface both occur during the initial period, fw should represent the average of fw for each type of wetting, weighted according to the total infiltration depth received by each type."
- Fig. 29 may be used "when irrigation is by high frequency systems such as microirrigation ... and light applications of about 10 mm or less per wetting event are applied" (Ch. 6).
- Chapters 5 and 8: no statement about fw or drip. Ch. 5 only mentions the fraction of ground covered by vegetation as a Kc driver and in stage definitions. Ch. 8 mentions neither fw nor drip (searched for "trickle", "drip", "micro", "fw", "wetted").

### Table 20 (Ch. 7, "fw") fraction of soil surface wetted

| Wetting event | fw |
|---|---|
| Precipitation | 1.0 |
| Sprinkler, basin, border irrigation | 1.0 |
| Furrow (every furrow), narrow bed | 0.6...1.0 |
| Furrow (every furrow), wide bed | 0.4...0.6 |
| Furrow (alternated furrows) | 0.3...0.5 |
| Trickle irrigation | 0.3...0.4 |

Daily rules for fw (Ch. 7, after Table 20): "Surface is wetted by irrigation and rain: fw is the fw for the irrigation system; Surface is wetted by irrigation: fw is the fw for the irrigation system; Surface is wetted by significant rain (i.e., > 3 to 4 mm) with no irrigation: fw = 1; Where there is neither irrigation nor significant precipitation: fw is the fw of the previous day."

### Ground cover fc (Ch. 5, Ch. 7)

- Ch. 5: initial stage ends at "approximately 10% ground cover". For tall crops effective full cover occurs at fc "about 0.7-0.8". "Typically, if the soil surface is dry, Kc = 0.5 corresponds to about 25-40% of the ground surface covered by vegetation ... A Kc = 0.7 often corresponds to about 40-60% ground cover."
- Ch. 7, Table 21 (fc): initial 0.0-0.1; development 0.1-0.8; mid-season 0.8-1.0; late season 0.8-0.2.
- Ch. 7, Eq. 75: "few = min(1 - fc, fw) (75)" (exposed and wetted fraction for evaporation).
- Ch. 7 drip: "In the case of drip irrigation, where the majority of soil wetted by irrigation may be beneath the canopy and may therefore be shaded ... the value for fw may need to be reduced to about one-half to one-third of that given in Table 20 ... A general approach could be to multiply fw by [1-(2/3)fc] for drip irrigation." Example 34 gives few = min[(1 - fc),(1 - 0.67 fc) fw)] = "0.19" for fc = 0.53 and fw = 0.3.
- Also (Ch. 7, Ke section): "Ii is generally expressed as a depth of water that is equivalent to the mean infiltrated irrigation depth distributed over the entire field. Therefore, the value Ii/fw is used to describe the actual concentration of the irrigation volume over the fraction of the soil that is wetted (Figure 31)."
- The book does NOT apply an fc or fw factor to the transpiration part of ETc (Kc mid) for drip. That is a field-level coefficient (ET over the whole field area). Ch. 8 water balance is in mm over the whole field area ("Ii is equivalent to the mean infiltrated irrigation depth expressed for the entire field surface"). So for volume per plant or per emitter line, the engine must convert the field-equivalent mm itself. The book gives no drip-specific volume formula in the requested chapters.

---

## 6. Open questions and caveats for the engine author

1. Single or dual Kc. Table 10 recommends the dual (Kcb + Ke) for "high frequency water application (microirrigation ...)". A single Kc planner is the simpler "basic irrigation schedule" case and the book warns the single Kc is time-averaged. If single Kc is used, Kc ini should be corrected with fw (Eq. 60), and Kc mid may be raised to 1.1-1.3 for frequent wetting with fw > 0.3 only where Table 12 Kc mid < 1.0 (not the case for tomato 1.15 or pepper 1.05 beyond that rule; check the rule's wording).
2. Kc ini for tomato and pepper. Table 12 gives one group value of 0.6 (my reading of a blank cell). Verify in the printed book. The book says to refine it with Fig. 29 or 30, or Annex 7.
3. Stage lengths. Table 11 gives several rows per crop with different climates and plant dates and says to use local data. The engine needs the local row, or a user-supplied set of four lengths. The pepper row "25/30" is ambiguous. Tomato Kc end "0.70-0.90" and the 1.15 / 1.20 tall-crop options (Table 12 fn. 2) need a decision.
4. Eq. 62, 65, 61, 84, 8-1, 8-3 are images that could not be read. Eq. 66 form was confirmed from Example 28 arithmetic and Annex 8 cell O14. Eq. 84 form was confirmed from Annex 8 cell AJ14 and Example 37 numbers. Eq. 62 and 65 are only partly confirmed through the Kcb analogue (Eq. 70) in Annex 8. Check the PDF if the climate adjustment is implemented.
5. Start-of-day assumption. The book's balance (Eq. 85) is end-of-day. Annex 8 assumes irrigation and rain happen "early in the morning", and the decision to irrigate is made from the previous day's end-of-day depletion, applied at the start of the next day. The engine should follow this and define clearly whether the stored value is start-of-day (after irrigation) or end-of-day.
6. Trigger: `>=` (text) or `>` (Excel formula). Whether to trigger at Dr = RAW exactly. Ch. 8 says "before or at the moment" Dr <= RAW; Annex 8 text says "greater than or equal to RAW".
7. "Half" simplification vs p. p = 0.5 is only "commonly used". Table 22 gives tomato 0.40 and pepper 0.30 (at ETc about 5 mm/day). The book adjusts p with `p = p_table22 + 0.04 (5 - ETc)`, limited to 0.1-0.8, and by soil texture (plus or minus 5-10%). MAD may be set above or below RAW by management (Ch. 8). Decide whether the planner uses p, MAD, or a user-set fraction.
8. Irrigation amount. The book's rule is Ii <= Dr (apply up to the depletion, not above). Annex 8 applies exactly Dr. The amount in litres still needs the field/plot area and the fw conversion (mm x m2 = L). Real drip systems have efficiency and uniformity losses that the book does not cover in these chapters.
9. Root depth. Table 22 gives ranges (tomato 0.7-1.5 m, pepper 0.5-1.0 m) with the note that smaller values suit irrigation scheduling. Annex 8 grows Zr from 0.15-0.20 m at planting in proportion to Kcb. Drip systems often limit the effective root zone, so decide the value used.
10. Rain. The book has no "effective rainfall" term. It uses P - RO, ignores small rain (< about 0.2 ETo, Ch. 8) and treats the excess above field capacity as deep percolation (Eq. 88). Annex 8 sets RO = 0. A planner that uses forecast or measured rain must decide its own runoff and minimum-rain rules.
11. Drip wetting. fw for trickle is 0.3-0.4 (Table 20), but ch. 7 says shaded drip wetting may need fw reduced to one-half to one-third or multiplied by [1 - (2/3) fc]. That correction is part of the evaporation component (Ke). It does not change the soil bucket in Eq. 85, which is in field-average mm.
12. Unit conversion is not stated as "1 mm = 1 L/m2" in the requested chapters. It follows from Annex 1 (1 m3/ha/day = 0.1 mm/day).
13. Table 12 header, Table 12 Kc ini column and Annex 8 Fig. 8.1 header rows were read from OCR-style HTML where some cells are empty or merged. Check any number the engine hard-codes against the printed book.

---

## Sources (pages actually fetched, 2026-11-16)

- https://www.fao.org/3/x0490E/x0490e00.htm (contents page and file map)
- https://www.fao.org/3/x0490e/x0490e0a.htm (Ch. 5)
- https://www.fao.org/3/x0490e/x0490e0b.htm (Ch. 6)
- https://www.fao.org/3/x0490e/x0490e0c.htm (Ch. 7, for Table 20, Table 21, Eq. 75, drip fw text)
- https://www.fao.org/3/x0490e/x0490e0e.htm (Ch. 8)
- https://www.fao.org/3/x0490e/x0490e0i.htm (Annex 1, units)
- https://www.fao.org/3/x0490e/x0490e0p.htm (Annex 8)
- Equation images x0490e2d.gif, x0490e2i.gif, x0490e2k.gif under https://www.fao.org/3/x0490e/ were requested but returned an HTML error page, not an image (could not be read).
