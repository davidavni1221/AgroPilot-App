"""What the irrigation engine needs to know about a crop, and the two irrigation rules it applies.

The crop numbers (Kc, stage lengths, root depth) come from the registry. The tomato and bell pepper values
it starts with are from docs/research/fao56.md (FAO-56). Choices the book leaves open are marked CHOICE.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class CropParams:
    kc_ini: float
    kc_mid: float
    kc_end: float
    l_ini: int  # days
    l_dev: int
    l_mid: int
    l_late: int
    root_depth_m: float


# Irrigate when the bucket would fall below this share of its capacity. The task's rule; FAO-56 calls p = 0.5 "commonly used".
IRRIGATE_BELOW = 0.5

# CHOICE: the bucket holds this share of its capacity at the start of today. The registry has no soil moisture, so this is
# an assumption. Starting at the irrigation line means today already gets what the crop uses.
START_LEVEL = 0.5
