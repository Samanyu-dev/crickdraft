"""
Shared feature extraction for the ball-outcome model. Both the offline
trainer and the runtime engine build feature vectors the same way so what
gets learned is what gets used.

Feature vector (bias included):
  [1, batter_skill, bowler_skill, skill_diff, fielding_pressure,
   effective_morale, phase_powerplay, phase_death, pressure_factor]
"""
from typing import Optional

FEATURE_NAMES = [
    "bias", "batter_skill", "bowler_skill", "skill_diff", "fielding_pressure",
    "effective_morale", "phase_powerplay", "phase_death", "pressure_factor",
]
OUTCOMES = ["0", "1", "2", "3", "4", "6", "W"]


def clip(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def batter_skill(batting: Optional[dict]) -> float:
    if not batting:
        return 0.15  # tail-ender facing a ball, still capable of blocking/nudging
    return clip((batting["avg"] / 65.0) * 0.65 + (batting["sr"] / 120.0) * 0.35)


def bowler_skill(bowling: Optional[dict]) -> float:
    if not bowling:
        return 0.25  # part-timer pressed into an over
    return clip((1 - bowling["avg"] / 40.0) * 0.5 + (1 - bowling["econ"] / 8.0) * 0.3 + (1 - bowling["sr"] / 70.0) * 0.2)


def effective_morale(morale: float, wickets_down: int) -> float:
    base = morale / 100.0
    pressure = wickets_down / 10.0
    return clip(base - 0.15 * pressure * (1 - base))


def build_features(
    batter: dict,
    bowler: dict,
    bowling_side_fielding_avg: float,
    wickets_down: int,
    over_index: int,
    total_overs: int,
    pressure_factor: float,
) -> list:
    b_skill = batter_skill(batter.get("batting"))
    bl_skill = bowler_skill(bowler.get("bowling"))
    powerplay_overs = max(1, round(total_overs * 0.3))
    death_start = total_overs - max(1, round(total_overs * 0.2))
    return [
        1.0,
        b_skill,
        bl_skill,
        b_skill - bl_skill,
        clip(bowling_side_fielding_avg / 100.0),
        effective_morale(batter.get("morale", 60), wickets_down),
        1.0 if over_index < powerplay_overs else 0.0,
        1.0 if over_index >= death_start else 0.0,
        clip(pressure_factor, -0.5, 1.0),
    ]
