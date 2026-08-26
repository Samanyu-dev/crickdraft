import random
from typing import List, Dict

from .players_data import PLAYERS, PLAYERS_BY_ID, ROLE_RULES


def _poisson(lam: float) -> int:
    # Knuth's algorithm; avoids a numpy dependency.
    l = pow(2.718281828, -lam)
    k = 0
    p = 1.0
    while True:
        k += 1
        p *= random.random()
        if p <= l:
            return k - 1


def _simulate_batting(player: dict) -> Dict:
    bat = player.get("batting")
    if not bat:
        return {"runs": 0, "points": 0.0}
    consistency = player.get("consistency", 0.6)
    scale = 0.6 if player["role"] == "AR" else 1.0
    mu = bat["avg"] * 0.7 * scale
    sigma = max(4.0, bat["avg"] * 0.55 * (1.15 - consistency) * scale)
    runs = max(0, round(random.gauss(mu, sigma)))
    points = float(runs)
    if runs >= 100:
        points += 16
    elif runs >= 50:
        points += 8
    # strike-rate bonus/penalty
    sr = bat.get("sr") or 80
    if sr >= 140:
        points += 6
    elif sr < 60:
        points -= 4
    return {"runs": runs, "points": round(points, 1)}


def _simulate_bowling(player: dict) -> Dict:
    bowl = player.get("bowling")
    if not bowl:
        return {"wickets": 0, "points": 0.0}
    scale = 0.6 if player["role"] == "AR" else 1.0
    expected_wkts = max(0.2, (4.6 - bowl["avg"] / 11.5)) * scale
    wickets = min(6, _poisson(expected_wkts))
    points = wickets * 25.0
    if wickets >= 5:
        points += 16
    elif wickets >= 3:
        points += 8
    econ = bowl.get("econ") or 7.0
    if econ < 5.0:
        points += 6
    elif econ > 9.0:
        points -= 4
    return {"wickets": wickets, "points": round(points, 1)}


def simulate_player_performance(player: dict, is_captain: bool) -> Dict:
    bat = _simulate_batting(player)
    bowl = _simulate_bowling(player)
    total = bat["points"] + bowl["points"]
    if is_captain:
        total *= 2
    return {
        "id": player["id"],
        "name": player["name"],
        "role": player["role"],
        "runs": bat["runs"],
        "wickets": bowl["wickets"],
        "points": round(total, 1),
        "captain": is_captain,
    }


def build_ai_opponent(exclude_ids: List[int]) -> List[dict]:
    pool = [p for p in PLAYERS if p["id"] not in exclude_ids]
    squad: List[dict] = []
    used = set()

    def take(role: str, count: int):
        candidates = [p for p in pool if p["role"] == role and p["id"] not in used]
        if not candidates:
            return
        # draw from the upper-middle of the pool rather than always the single best,
        # so AI opponents vary in strength instead of always fielding an all-legends XI
        candidates.sort(key=lambda p: p["rating"], reverse=True)
        window = candidates[: max(count * 3, len(candidates) // 2)]
        random.shuffle(window)
        for p in window[:count]:
            squad.append(p)
            used.add(p["id"])

    take("WK", 1)
    take("BAT", random.choice([4, 5]))
    take("BOWL", random.choice([4, 5]))
    remaining = 11 - len(squad)
    take("AR", remaining)

    # top up if short (small pools / role scarcity)
    if len(squad) < 11:
        leftovers = [p for p in pool if p["id"] not in used]
        random.shuffle(leftovers)
        for p in leftovers:
            if len(squad) >= 11:
                break
            squad.append(p)
            used.add(p["id"])

    return squad[:11]


def name_opponent(squad: List[dict]) -> str:
    countries = [p["country"] for p in squad]
    top = max(set(countries), key=countries.count)
    share = countries.count(top) / len(countries)
    if share >= 0.6:
        return f"{top} Legends XI"
    return "World Select XI"


def simulate_match(user_squad: List[dict], captain_id: int):
    opponent_squad = build_ai_opponent([p["id"] for p in user_squad])
    opponent_name = name_opponent(opponent_squad)

    team_scorecard = [simulate_player_performance(p, p["id"] == captain_id) for p in user_squad]
    # give the AI team a captain too (its highest-rated player)
    ai_captain = max(opponent_squad, key=lambda p: p["rating"])["id"]
    opp_scorecard = [simulate_player_performance(p, p["id"] == ai_captain) for p in opponent_squad]

    team_score = round(sum(p["points"] for p in team_scorecard), 1)
    opp_score = round(sum(p["points"] for p in opp_scorecard), 1)
    result = "W" if team_score >= opp_score else "L"

    return {
        "opponent_name": opponent_name,
        "team_score": team_score,
        "opponent_score": opp_score,
        "result": result,
        "scorecard": {
            "team": team_scorecard,
            "opponent": opp_scorecard,
        },
    }
