"""Crop parameters for the irrigation engine. Every number is from docs/research/fao56.md (FAO-56).

The registry knows a plot's crop only by id, so the Kc values, stage lengths and root depth live here.
Choices the book leaves open are marked CHOICE.
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


CROPS: dict[str, CropParams] = {
    # Kc: Table 12 (Solanum family, kc_ini is the group value). Lengths: Table 11, Mediterranean, April/May.
    # CHOICE: kc_end 0.80 is the middle of the printed range 0.70-0.90.
    # CHOICE: root depth 0.7 m is the small end of Table 22's 0.7-1.5 m, which the book advises for irrigation scheduling.
    "tomato": CropParams(kc_ini=0.6, kc_mid=1.15, kc_end=0.80, l_ini=30, l_dev=40, l_mid=45, l_late=30, root_depth_m=0.7),
    # Kc: Table 12. Lengths: Table 11, Europe and Mediterranean, April/June, total 125.
    # CHOICE: Table 11 prints l_ini as "25/30". 30 is the value that adds up to the printed total 30+35+40+20 = 125.
    # CHOICE: root depth 0.5 m is the small end of Table 22's 0.5-1.0 m.
    "bell-pepper": CropParams(kc_ini=0.6, kc_mid=1.05, kc_end=0.90, l_ini=30, l_dev=35, l_mid=40, l_late=20, root_depth_m=0.5),
}

# Irrigate when the bucket would fall below this share of its capacity. The task's rule; FAO-56 calls p = 0.5 "commonly used".
IRRIGATE_BELOW = 0.5

# CHOICE: the bucket holds this share of its capacity at the start of today. The registry has no soil moisture, so this is
# an assumption. Starting at the irrigation line means today already gets what the crop uses.
START_LEVEL = 0.5
