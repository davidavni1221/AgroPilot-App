---
name: drip-irrigation
description: How drip irrigation is described in AgroPilot data (soils, emitters, spacing, plot area) and how to calculate with it. Use when working with plots, soils, emitters, or irrigation calculations.
---

# Drip irrigation in AgroPilot

## Fields and units

| Field | Unit | Meaning |
|---|---|---|
| `area_m2` | m² | Plot area |
| `row_spacing_m` | m | Distance between plant rows |
| `emitter_spacing_m` | m | Distance between emitters along a row |
| `flow_lph` (emitter) | L/h | Water an emitter delivers in one hour |
| `available_water_mm_per_m` (soil) | mm per m of depth | Water the soil can hold for plants, as a depth of water |

## Formulas (simplified model)

Assumptions: one emitter for each `row_spacing_m × emitter_spacing_m` cell, and no losses (100% efficiency).

- Volume: 1 mm of water over 1 m² is 1 liter, so `volume_L = area_m2 × depth_mm`.
- Cell area: `cell_m2 = row_spacing_m × emitter_spacing_m`.
- Emitter count: `emitters = area_m2 / cell_m2`.
- Application rate: `rate_mm_per_h = flow_lph / cell_m2`.
- Run time: `hours = depth_mm / rate_mm_per_h`.
- Water held in the root zone: `available_water_mm_per_m × root_depth_m`. The root depth is not stored in the registry, so it must be given as an input.

## Worked example (seed plot "North block")

Data: `area_m2` 1000, `row_spacing_m` 1.5, `emitter_spacing_m` 0.4, emitter `dripnet-pc-1.0` (`flow_lph` 1.0).

```text
cell_m2        = 1.5 * 0.4          = 0.6 m²
emitters       = 1000 / 0.6         = 1666.7
rate_mm_per_h  = 1.0 / 0.6          = 1.667 mm/h
depth 5 mm     -> volume_L          = 1000 * 5       = 5000 L
               -> hours             = 5 / 1.667      = 3.0 h
check          = 1666.7 emitters * 1.0 L/h * 3 h     = 5000 L
```

## Open points

- Rounding rules and efficiency factors are not defined yet. Ask before assuming them.
- These formulas are a simplified teaching model, not agronomic advice.
