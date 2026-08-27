import random
from typing import List, Optional

from .players_data import PLAYERS
from .model.features import build_features, batter_skill, bowler_skill, clip
from .model.ball_model import sample_outcome


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


def build_ai_opponent(exclude_ids: List[int], target_elo: float = 1200.0, pool: Optional[List[dict]] = None) -> List[dict]:
    """Builds a random XI whose average player rating is centered on
    whatever team strength `target_elo` implies - used when there's no
    real opponent to matchmake against, so the fallback still scales with
    the challenger's own rank instead of always fielding a stacked XI."""
    target_avg = 68.0 + (target_elo - 1200.0) / 25.0

    source = pool if pool is not None else PLAYERS
    candidates_pool = [p for p in source if p["id"] not in exclude_ids]
    squad: List[dict] = []
    used = set()

    def take(role: str, count: int):
        candidates = [p for p in candidates_pool if p["role"] == role and p["id"] not in used]
        if not candidates:
            return
        candidates.sort(key=lambda p: abs(p["rating"] - target_avg))
        window = candidates[: max(count * 3, 6)]
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
        leftovers = [p for p in candidates_pool if p["id"] not in used]
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


def simulate_innings(batting_order: List[dict], bowling_team: List[dict], total_overs: int, target=None):
    max_overs_per_bowler = max(1, total_overs // 5)
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
            if overs_bowled[candidate["id"]] < max_overs_per_bowler:
                return candidate
        return min(bowlers, key=lambda p: overs_bowled[p["id"]])

    for over in range(total_overs):
        if wickets_down >= 10 or chase_won:
            break
        bowler = pick_bowler()
        overs_bowled[bowler["id"]] += 1
        over_balls: List[str] = []
        for ball in range(6):
            if wickets_down >= 10:
                break
            striker = batting_order[striker_idx]
            balls_remaining = (total_overs - over) * 6 - ball
            if target is not None:
                required = target - score
                required_rate = (required / max(1, balls_remaining)) * 6
                pressure = clip((required_rate - 6) / 10.0, -0.5, 1.0)
            else:
                pressure = 0.0

            x = build_features(striker, bowler, fielding_avg, wickets_down, over, total_overs, pressure)
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


def _merge_points(batting_innings_list, bowling_innings_list):
    """Combine a side's batting (across all innings it batted) with its
    bowling (across all innings it bowled) into per-player fantasy points -
    relevant for all-rounders, and for Test where a player bats/bowls twice."""
    merged = {}
    for innings in batting_innings_list:
        for s in innings["batting"]:
            merged[s["id"]] = merged.get(s["id"], 0.0) + fantasy_points_batting(s["runs"], s["balls"])
    for innings in bowling_innings_list:
        for b in innings["bowling"]:
            merged[b["id"]] = merged.get(b["id"], 0.0) + fantasy_points_bowling(b["wickets"], b["balls"] / 6.0, b["runs_conceded"])
    return merged


def _aggregate_scorecard(batting_innings_list, bowling_innings_list, points_map, captain_id, other_captain_id):
    rows_by_id = {}
    order = []
    for innings in batting_innings_list:
        for s in innings["batting"]:
            if s["id"] not in rows_by_id:
                rows_by_id[s["id"]] = {
                    "id": s["id"], "name": s["name"], "role": s["role"],
                    "runs": 0, "balls": 0, "wickets": 0, "how_out": "not out",
                    "captain": s["id"] == captain_id or s["id"] == other_captain_id,
                }
                order.append(s["id"])
            row = rows_by_id[s["id"]]
            row["runs"] += s["runs"]
            row["balls"] += s["balls"]
            row["how_out"] = s["how_out"] if s["out"] else row["how_out"]
    bowl_totals = {}
    for innings in bowling_innings_list:
        for b in innings["bowling"]:
            t = bowl_totals.setdefault(b["id"], {"wickets": 0, "balls": 0, "runs_conceded": 0})
            t["wickets"] += b["wickets"]
            t["balls"] += b["balls"]
            t["runs_conceded"] += b["runs_conceded"]
    for pid, t in bowl_totals.items():
        if pid not in rows_by_id:
            # a bowler who didn't bat this side of the ledger yet (rare) - still show their figures
            continue
        rows_by_id[pid]["wickets"] = t["wickets"]
        rows_by_id[pid]["overs"] = round(t["balls"] / 6.0, 1)
        rows_by_id[pid]["runs_conceded"] = t["runs_conceded"]
    for pid in rows_by_id:
        rows_by_id[pid]["points"] = round(points_map.get(pid, 0.0), 1)
    return [rows_by_id[pid] for pid in order]


def simulate_match(
    user_batting_order: List[dict],
    captain_id: int,
    opponent_order: List[dict],
    opponent_name: str,
    opponent_rating: float,
    opponent_captain_id: Optional[int] = None,
    overs: int = 20,
    innings_per_side: int = 1,
):
    ai_captain = opponent_captain_id or max(opponent_order, key=lambda p: p["rating"])["id"]
    innings_public: List[dict] = []

    def public(innings, side, seq):
        return {
            "side": side, "seq": seq, "score": innings["score"], "wickets": innings["wickets"],
            "overs": innings["overs"], "timeline": innings["timeline"],
        }

    if innings_per_side == 1:
        first = simulate_innings(user_batting_order, opponent_order, overs, target=None)
        second = simulate_innings(opponent_order, user_batting_order, overs, target=first["score"] + 1)
        innings_public = [public(first, "team", 1), public(second, "opponent", 2)]

        team_batting, team_bowling = [first], [second]
        opp_batting, opp_bowling = [second], [first]

        team_total, opp_total = first["score"], second["score"]
        if team_total != opp_total:
            result = "W" if team_total > opp_total else "L"
        else:
            result = "W" if first["wickets"] <= second["wickets"] else "L"

    else:  # Test: two innings a side
        a1 = simulate_innings(user_batting_order, opponent_order, overs, target=None)
        b1 = simulate_innings(opponent_order, user_batting_order, overs, target=None)
        a2 = simulate_innings(user_batting_order, opponent_order, overs, target=None)
        target = a1["score"] + a2["score"] - b1["score"] + 1
        b2 = simulate_innings(opponent_order, user_batting_order, overs, target=target)
        innings_public = [
            public(a1, "team", 1), public(b1, "opponent", 2),
            public(a2, "team", 3), public(b2, "opponent", 4),
        ]

        team_batting, team_bowling = [a1, a2], [b1, b2]
        opp_batting, opp_bowling = [b1, b2], [a1, a2]

        team_total = a1["score"] + a2["score"]
        opp_total = b1["score"] + b2["score"]
        if b2["score"] >= target:
            result = "L"
        elif b2["wickets"] >= 10:
            result = "W"
        else:
            result = "D"  # overs ran out with the chase unresolved

    team_points = _merge_points(team_batting, team_bowling)
    opp_points = _merge_points(opp_batting, opp_bowling)
    if captain_id in team_points:
        team_points[captain_id] *= 2
    if ai_captain in opp_points:
        opp_points[ai_captain] *= 2

    return {
        "opponent_name": opponent_name,
        "opponent_rating": opponent_rating,
        "result": result,
        "team_total": team_total,
        "opponent_total": opp_total,
        "innings": innings_public,
        "scorecard": {
            "team": _aggregate_scorecard(team_batting, team_bowling, team_points, captain_id, ai_captain),
            "opponent": _aggregate_scorecard(opp_batting, opp_bowling, opp_points, captain_id, ai_captain),
        },
        "fantasy_points": round(sum(team_points.values()), 1),
    }
