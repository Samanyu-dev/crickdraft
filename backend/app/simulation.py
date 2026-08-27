import random
from typing import List

from .players_data import PLAYERS
from .model.features import build_features, batter_skill, bowler_skill, clip
from .model.ball_model import sample_outcome

TOTAL_OVERS = 20
MAX_OVERS_PER_BOWLER = max(1, TOTAL_OVERS // 5)


def assign_batting_order(players: List[dict]) -> List[dict]:
    """Assign 11 players into positions 1-11 respecting each player's
    (position_min, position_max), via bipartite matching (Kuhn's algorithm)
    so a valid arrangement is found whenever one exists - a greedy
    most-constrained-first heuristic can fail even when a perfect
    assignment is possible. Used for the randomly built AI opponent; the
    human user's own order is submitted explicitly and validated exactly."""
    n = len(players)
    slot_to_player: List[int] = [-1] * n

    def try_assign(player_idx: int, visited: set) -> bool:
        p = players[player_idx]
        for slot in range(p["position_min"] - 1, min(p["position_max"], n)):
            if slot in visited:
                continue
            visited.add(slot)
            if slot_to_player[slot] == -1 or try_assign(slot_to_player[slot], visited):
                slot_to_player[slot] = player_idx
                return True
        return False

    unmatched_idx = []
    for i in range(n):
        if not try_assign(i, set()):
            unmatched_idx.append(i)

    order: List[dict] = [None] * n
    for slot, player_idx in enumerate(slot_to_player):
        if player_idx != -1:
            order[slot] = players[player_idx]
    # fallback (only reached if no perfect matching exists at all): drop
    # remaining players into whatever slots are left over.
    empty_slots = [i for i, p in enumerate(order) if p is None]
    for slot, player_idx in zip(empty_slots, unmatched_idx):
        order[slot] = players[player_idx]
    return order


def build_ai_opponent(exclude_ids: List[int]) -> List[dict]:
    from .players_data import ROLE_RULES

    pool = [p for p in PLAYERS if p["id"] not in exclude_ids]
    squad: List[dict] = []
    used = set()

    def take(role: str, count: int):
        candidates = [p for p in pool if p["role"] == role and p["id"] not in used]
        if not candidates:
            return
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


def team_elo_rating(squad: List[dict]) -> float:
    """Maps a squad's average player rating onto an Elo-like scale centered
    on the default starting rating, so a random opponent's strength
    actually moves the ladder math (beating a stacked legends XI is worth
    more than beating a weak one)."""
    avg_rating = sum(p["rating"] for p in squad) / len(squad)
    return round(1200 + (avg_rating - 68.0) * 25, 1)


def _team_fielding_avg(team: List[dict]) -> float:
    return sum(p.get("fielding", 55) for p in team) / len(team)


def _bowler_pool(team: List[dict]) -> List[dict]:
    bowlers = [p for p in team if p.get("bowling")]
    bowlers.sort(key=lambda p: -bowler_skill(p["bowling"]))
    return bowlers if bowlers else list(team)


def fantasy_points_batting(runs: int, balls: int) -> float:
    pts = float(runs)
    if runs >= 100:
        pts += 16
    elif runs >= 50:
        pts += 8
    if balls >= 10:
        sr = runs / balls * 100
        if sr >= 140:
            pts += 6
        elif sr < 60:
            pts -= 4
    return pts


def fantasy_points_bowling(wickets: int, overs: float, runs_conceded: int) -> float:
    pts = wickets * 25.0
    if wickets >= 5:
        pts += 16
    elif wickets >= 3:
        pts += 8
    if overs > 0:
        econ = runs_conceded / overs
        if econ < 5:
            pts += 6
        elif econ > 9:
            pts -= 4
    return pts


def simulate_innings(batting_order: List[dict], bowling_team: List[dict], target=None):
    stats = {
        p["id"]: {"id": p["id"], "name": p["name"], "role": p["role"], "runs": 0, "balls": 0,
                   "fours": 0, "sixes": 0, "out": False, "how_out": "not out"}
        for p in batting_order
    }
    bowl_stats = {
        p["id"]: {"id": p["id"], "name": p["name"], "balls": 0, "runs_conceded": 0, "wickets": 0}
        for p in bowling_team
    }

    fielding_avg = _team_fielding_avg(bowling_team)
    bowlers = _bowler_pool(bowling_team)
    overs_bowled = {p["id"]: 0 for p in bowlers}
    rotation_idx = 0

    striker_idx, non_striker_idx, next_in = 0, 1, 2
    score = 0
    wickets_down = 0
    balls_bowled_total = 0
    chase_won = False
    timeline: List[dict] = []

    def pick_bowler():
        nonlocal rotation_idx
        n = len(bowlers)
        for _ in range(n):
            candidate = bowlers[rotation_idx % n]
            rotation_idx += 1
            if overs_bowled[candidate["id"]] < MAX_OVERS_PER_BOWLER:
                return candidate
        return min(bowlers, key=lambda p: overs_bowled[p["id"]])

    for over in range(TOTAL_OVERS):
        if wickets_down >= 10 or chase_won:
            break
        bowler = pick_bowler()
        overs_bowled[bowler["id"]] += 1
        over_balls: List[str] = []
        for ball in range(6):
            if wickets_down >= 10:
                break
            striker = batting_order[striker_idx]
            balls_remaining = (TOTAL_OVERS - over) * 6 - ball
            if target is not None:
                required = target - score
                required_rate = (required / max(1, balls_remaining)) * 6
                pressure = clip((required_rate - 6) / 10.0, -0.5, 1.0)
            else:
                pressure = 0.0

            x = build_features(striker, bowler, fielding_avg, wickets_down, over, TOTAL_OVERS, pressure)
            outcome = sample_outcome(x)

            s = stats[striker["id"]]
            bs = bowl_stats[bowler["id"]]
            s["balls"] += 1
            bs["balls"] += 1
            balls_bowled_total += 1

            if outcome == "W":
                s["out"] = True
                s["how_out"] = f"b {bowler['name']}"
                bs["wickets"] += 1
                wickets_down += 1
                over_balls.append("W")
                if wickets_down < 10 and next_in < 11:
                    striker_idx = next_in
                    next_in += 1
                # non_striker_idx unchanged
            else:
                runs = int(outcome)
                s["runs"] += runs
                score += runs
                bs["runs_conceded"] += runs
                over_balls.append(str(runs))
                if runs == 4:
                    s["fours"] += 1
                elif runs == 6:
                    s["sixes"] += 1
                if runs % 2 == 1:
                    striker_idx, non_striker_idx = non_striker_idx, striker_idx

            if target is not None and score > target - 1:
                chase_won = True
                break
        timeline.append({
            "over": over + 1,
            "bowler": bowler["name"],
            "balls": over_balls,
            "score": score,
            "wickets": wickets_down,
        })
        if wickets_down >= 10 or chase_won:
            break
        # strike rotates at the end of a completed over
        striker_idx, non_striker_idx = non_striker_idx, striker_idx

    overs_used = balls_bowled_total // 6 + (balls_bowled_total % 6) / 10.0

    return {
        "score": score,
        "wickets": wickets_down,
        "overs": round(overs_used, 1),
        "batting": list(stats.values()),
        "bowling": [b for b in bowl_stats.values() if b["balls"] > 0],
        "timeline": timeline,
    }


def _merge_points(batting_innings, bowling_innings):
    """Combine a side's batting (from the innings it batted) with its bowling
    (from the innings it bowled) into per-player fantasy points - relevant
    for all-rounders who show up in both."""
    merged = {}
    for s in batting_innings["batting"]:
        merged[s["id"]] = merged.get(s["id"], 0.0) + fantasy_points_batting(s["runs"], s["balls"])
    for b in bowling_innings["bowling"]:
        merged[b["id"]] = merged.get(b["id"], 0.0) + fantasy_points_bowling(b["wickets"], b["balls"] / 6.0, b["runs_conceded"])
    return merged


def simulate_match(user_batting_order: List[dict], captain_id: int):
    opponent_pool = build_ai_opponent([p["id"] for p in user_batting_order])
    opponent_order = assign_batting_order(opponent_pool)
    opponent_name = name_opponent(opponent_pool)

    first = simulate_innings(user_batting_order, opponent_order, target=None)
    second = simulate_innings(opponent_order, user_batting_order, target=first["score"] + 1)

    # team bats in `first` and bowls in `second`; opponent is the mirror
    team_points = _merge_points(first, second)
    opp_points = _merge_points(second, first)

    if captain_id in team_points:
        team_points[captain_id] *= 2
    ai_captain = max(opponent_order, key=lambda p: p["rating"])["id"]
    if ai_captain in opp_points:
        opp_points[ai_captain] *= 2

    team_score, opp_score = first["score"], second["score"]
    if team_score != opp_score:
        result = "W" if team_score > opp_score else "L"
    else:
        # scores level: fewer wickets lost carries the tiebreak, like a Super Over proxy
        result = "W" if first["wickets"] <= second["wickets"] else "L"

    def scorecard_rows(batting_innings, bowling_innings, points_map):
        rows = []
        for s in batting_innings["batting"]:
            rows.append({
                "id": s["id"], "name": s["name"], "role": s["role"],
                "runs": s["runs"], "wickets": 0,
                "balls": s["balls"], "how_out": s["how_out"],
                "points": round(points_map.get(s["id"], 0.0), 1),
                "captain": s["id"] == captain_id or s["id"] == ai_captain,
            })
        bowl_by_id = {b["id"]: b for b in bowling_innings["bowling"]}
        for row in rows:
            b = bowl_by_id.get(row["id"])
            if b:
                row["wickets"] = b["wickets"]
                row["overs"] = round(b["balls"] / 6.0, 1)
                row["runs_conceded"] = b["runs_conceded"]
        return rows

    return {
        "opponent_name": opponent_name,
        "opponent_rating": team_elo_rating(opponent_order),
        "team_score": float(team_score),
        "opponent_score": float(opp_score),
        "team_wickets": first["wickets"],
        "opponent_wickets": second["wickets"],
        "team_overs": first["overs"],
        "opponent_overs": second["overs"],
        "team_timeline": first["timeline"],
        "opponent_timeline": second["timeline"],
        "result": result,
        "scorecard": {
            "team": scorecard_rows(first, second, team_points),
            "opponent": scorecard_rows(second, first, opp_points),
        },
        "fantasy_points": round(sum(team_points.values()), 1),
    }
