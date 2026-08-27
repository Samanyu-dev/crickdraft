import json
import os
from typing import Dict, List

_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "players.json")

with open(_DATA_PATH) as f:
    PLAYERS: List[dict] = json.load(f)

PLAYERS_BY_ID: Dict[int, dict] = {p["id"]: p for p in PLAYERS}


def _squad_key(country: str, era: int) -> str:
    return f"{country}|{era}"


SQUADS: Dict[str, dict] = {}
for _p in PLAYERS:
    _key = _squad_key(_p["country"], _p["era"])
    if _key not in SQUADS:
        SQUADS[_key] = {
            "key": _key,
            "country": _p["country"],
            "era": _p["era"],
            "squad_name": _p["squad_name"],
            "players": [],
        }
    SQUADS[_key]["players"].append(_p)

ROLE_RULES = {
    # role: (min, max)
    "WK": (1, 2),
    "BAT": (3, 6),
    "BOWL": (3, 6),
    "AR": (0, 4),
}
SQUAD_SIZE = 11
CREDIT_CAP = 100.0


def validate_squad(player_ids: List[int]):
    if len(player_ids) != SQUAD_SIZE:
        return False, f"Squad must have exactly {SQUAD_SIZE} players (got {len(player_ids)})."
    if len(set(player_ids)) != len(player_ids):
        return False, "Duplicate players are not allowed."

    role_counts = {"WK": 0, "BAT": 0, "BOWL": 0, "AR": 0}
    total_credit = 0.0
    for pid in player_ids:
        player = PLAYERS_BY_ID.get(pid)
        if not player:
            return False, f"Unknown player id {pid}."
        role_counts[player["role"]] += 1
        total_credit += player["credit"]

    for role, (lo, hi) in ROLE_RULES.items():
        if not (lo <= role_counts[role] <= hi):
            return False, f"{role} count must be between {lo} and {hi} (got {role_counts[role]})."

    if total_credit > CREDIT_CAP + 1e-9:
        return False, f"Squad costs {total_credit:.1f} credits, exceeds cap of {CREDIT_CAP:.0f}."

    return True, "ok"
