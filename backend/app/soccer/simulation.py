"""
Soccer match engine. Deliberately simpler than cricket's ball-by-ball
model: cricket earned that depth because scoring is a long sequence of
discrete, individually-attributable events (each ball). A football match
is much better represented as a handful of genuine chances across 90
minutes, so this simulates ~18 five-minute phases, each phase resolving
to a chance for whichever side has the run of play that phase (weighted
by midfield/passing strength), with a goal probability driven by
attack-vs-defense quality and a RNG draw - real randomness over a
proportionally-sized model, not a re-hash of the cricket engine.
"""
import random
from typing import List, Optional

PHASES = 18  # 5-minute chunks across 90 minutes


def clip(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def _attack_quality(team: List[dict]) -> float:
    attackers = [p for p in team if p["role"] in ("FWD", "MID")]
    pool = attackers or team
    return sum(p["attack"] * 0.6 + p["passing"] * 0.4 for p in pool) / len(pool)


def _midfield_quality(team: List[dict]) -> float:
    mids = [p for p in team if p["role"] == "MID"] or team
    return sum(p["passing"] for p in mids) / len(mids)


def _defense_quality(team: List[dict]) -> float:
    gk = [p for p in team if p["role"] == "GK"]
    defenders = [p for p in team if p["role"] == "DEF"]
    gk_val = gk[0]["defense"] if gk else 55.0
    def_val = sum(p["defense"] for p in defenders) / len(defenders) if defenders else 55.0
    return def_val * 0.7 + gk_val * 0.3


def _pick_scorer(team: List[dict]) -> dict:
    candidates = [p for p in team if p["role"] in ("FWD", "MID", "DEF")]
    weights = [
        (p["attack"] * 2.2 if p["role"] == "FWD" else p["attack"] * 1.1 if p["role"] == "MID" else p["attack"] * 0.3) + 1
        for p in candidates
    ]
    return random.choices(candidates, weights=weights, k=1)[0]


def _pick_assister(team: List[dict], scorer_id: int) -> Optional[dict]:
    # Not every goal has a credited assist - solo runs, penalties, etc.
    if random.random() < 0.3:
        return None
    candidates = [p for p in team if p["id"] != scorer_id]
    if not candidates:
        return None
    weights = [
        (p["passing"] * 1.6 if p["role"] == "MID" else p["passing"] * 1.0 if p["role"] == "FWD" else p["passing"] * 0.6) + 1
        for p in candidates
    ]
    return random.choices(candidates, weights=weights, k=1)[0]


def team_elo_rating(squad: List[dict]) -> float:
    avg_rating = sum(p["rating"] for p in squad) / len(squad)
    return round(1200 + (avg_rating - 65.0) * 22, 1)


def name_opponent(squad: List[dict]) -> str:
    countries = [p["country"] for p in squad]
    top = max(set(countries), key=countries.count)
    share = countries.count(top) / len(countries)
    if share >= 0.6:
        return f"{top} Select XI"
    return "World All-Stars"


def build_ai_opponent(exclude_ids: List[int], target_elo: float, pool: List[dict]) -> List[dict]:
    target_avg = 65.0 + (target_elo - 1200.0) / 22.0
    candidates_pool = [p for p in pool if p["id"] not in exclude_ids]
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

    take("GK", 1)
    take("DEF", random.choice([3, 4]))
    take("MID", random.choice([3, 4]))
    remaining = 11 - len(squad)
    take("FWD", remaining)
    if len(squad) < 11:
        leftovers = [p for p in candidates_pool if p["id"] not in used]
        random.shuffle(leftovers)
        for p in leftovers:
            if len(squad) >= 11:
                break
            squad.append(p)
            used.add(p["id"])
    return squad[:11]


def _simulate_match_score(home: List[dict], away: List[dict]):
    home_mid, away_mid = _midfield_quality(home), _midfield_quality(away)
    home_attack, away_attack = _attack_quality(home), _attack_quality(away)
    home_def, away_def = _defense_quality(home), _defense_quality(away)

    score = {"home": 0, "away": 0}
    scorers = {"home": [], "away": []}
    assisters = {"home": [], "away": []}
    timeline: List[dict] = []

    for phase in range(PHASES):
        minute = (phase + 1) * 5
        late_game_push = 1.15 if minute >= 75 and score["home"] != score["away"] else 1.0

        attacking = "home" if random.random() < home_mid / (home_mid + away_mid) else "away"
        if attacking == "home":
            attacker_q, defender_q = home_attack * late_game_push, away_def
            team, opp_key = home, "away"
        else:
            attacker_q, defender_q = away_attack * late_game_push, home_def
            team, opp_key = away, "home"

        # The (attacker_q - defender_q) coefficient is the main lever on how
        # "stat-driven vs random" results feel - a moderate quality gap
        # should turn into a clearly better record, not a near coin flip.
        goal_prob = clip(0.11 + (attacker_q - defender_q) / 100.0 * 0.62, 0.03, 0.55)
        chance_prob = clip(goal_prob + 0.22, goal_prob, 0.75)

        roll = random.random()
        if roll < goal_prob:
            scorer = _pick_scorer(team)
            assister = _pick_assister(team, scorer["id"])
            score[attacking] += 1
            scorers[attacking].append(scorer["id"])
            if assister:
                assisters[attacking].append(assister["id"])
            event = "goal"
            event_detail = f"{scorer['name']} (assist: {assister['name']})" if assister else scorer["name"]
        elif roll < chance_prob:
            event = "chance"
            event_detail = None
        else:
            event = "quiet"
            event_detail = None

        timeline.append({
            "minute": minute, "side": "team" if attacking == "home" else "opponent",
            "event": event, "scorer": event_detail,
            "score_team": score["home"], "score_opponent": score["away"],
        })

    return score["home"], score["away"], scorers["home"], scorers["away"], assisters["home"], assisters["away"], timeline


def fantasy_points(
    team: List[dict], scorer_ids: List[dict], assister_ids: List[dict], goals_conceded: int, captain_id: int
) -> dict:
    """Every player who takes the pitch earns something, not just goalscorers -
    a match rating built from attacking/passing/defending contribution (each
    player's own stats, since the engine doesn't simulate individual
    shots/tackles/passes) plus the headline attacking and team-result bonuses."""
    points = {p["id"]: 2.0 for p in team}  # appearance points - everyone plays 90 minutes here
    for sid in scorer_ids:
        points[sid] = points.get(sid, 0.0) + 20.0
    for aid in assister_ids:
        points[aid] = points.get(aid, 0.0) + 10.0

    for p in team:
        pid = p["id"]
        if p["role"] in ("GK", "DEF"):
            points[pid] += round(p["defense"] / 100.0 * 4.0, 1)
            if goals_conceded == 0:
                points[pid] += 10.0
            else:
                points[pid] -= min(6.0, goals_conceded * 2.0)
        elif p["role"] == "MID":
            points[pid] += round(p["passing"] / 100.0 * 3.0, 1)
            points[pid] += round(p["defense"] / 100.0 * 1.5, 1)
            if goals_conceded == 0:
                points[pid] += 4.0
        else:  # FWD
            points[pid] += round(p["attack"] / 100.0 * 4.0, 1)

    if captain_id in points:
        points[captain_id] *= 2
    return points


def simulate_match(
    user_squad: List[dict],
    captain_id: int,
    opponent_squad: List[dict],
    opponent_name: str,
    opponent_rating: float,
    opponent_captain_id: Optional[int] = None,
):
    ai_captain = opponent_captain_id or max(opponent_squad, key=lambda p: p["rating"])["id"]

    team_goals, opp_goals, team_scorer_ids, opp_scorer_ids, team_assister_ids, opp_assister_ids, timeline = (
        _simulate_match_score(user_squad, opponent_squad)
    )

    team_points = fantasy_points(user_squad, team_scorer_ids, team_assister_ids, opp_goals, captain_id)
    opp_points = fantasy_points(opponent_squad, opp_scorer_ids, opp_assister_ids, team_goals, ai_captain)

    if team_goals != opp_goals:
        result = "W" if team_goals > opp_goals else "L"
    else:
        result = "D"

    def scorecard(team, points_map, scorer_ids, assister_ids, captain):
        goal_counts, assist_counts = {}, {}
        for sid in scorer_ids:
            goal_counts[sid] = goal_counts.get(sid, 0) + 1
        for aid in assister_ids:
            assist_counts[aid] = assist_counts.get(aid, 0) + 1
        rows = []
        for p in team:
            rows.append({
                "id": p["id"], "name": p["name"], "role": p["role"],
                "goals": goal_counts.get(p["id"], 0),
                "assists": assist_counts.get(p["id"], 0),
                "points": round(points_map.get(p["id"], 0.0), 1),
                "captain": p["id"] == captain,
            })
        return rows

    return {
        "opponent_name": opponent_name,
        "opponent_rating": opponent_rating,
        "result": result,
        "team_goals": team_goals,
        "opponent_goals": opp_goals,
        "timeline": timeline,
        "scorecard": {
            "team": scorecard(user_squad, team_points, team_scorer_ids, team_assister_ids, captain_id),
            "opponent": scorecard(opponent_squad, opp_points, opp_scorer_ids, opp_assister_ids, ai_captain),
        },
        "fantasy_points": round(sum(team_points.values()), 1),
    }
