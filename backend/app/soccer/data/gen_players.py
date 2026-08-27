"""
Generator for soccer players.json. Same spirit as cricket's generator:
squads are grouped by (country, era), names are altered versions of real
historic sides (no exact real name used), stats come from a tier
archetype scaled by role.

Run: python3 gen_players.py  (writes players.json next to this file)
"""
import json
import os
import random

random.seed(11)

TIERS = {
    "S": dict(core=(82, 96), morale=(80, 95)),
    "A": dict(core=(70, 84), morale=(68, 85)),
    "B": dict(core=(56, 71), morale=(55, 72)),
    "C": dict(core=(42, 58), morale=(40, 60)),
}


def roll(lo_hi):
    lo, hi = lo_hi
    return round(random.uniform(lo, hi), 1)


# (country, era, squad_name, [(name, role, tier), ...])  role: GK, DEF, MID, FWD
SQUADS = [
    ("Brazil", 1970, "1970 World Cup Winners", [
        ("Feliks", "GK", "A"), ("Carlos Albertto", "DEF", "A"), ("Britto", "DEF", "B"),
        ("Everaldoo", "DEF", "B"), ("Paulo Cesarr", "DEF", "B"), ("Wilson Piazzaa", "MID", "B"),
        ("Clodoaldoo", "MID", "A"), ("Gersonn", "MID", "A"), ("Riivelino", "MID", "S"),
        ("Jairzinhoo", "FWD", "A"), ("Peleh", "FWD", "S"), ("Tostaum", "FWD", "A"),
    ]),
    ("Argentina", 1986, "1986 World Cup Winners", [
        ("Nery Pumpidoo", "GK", "B"), ("Jose Luis Browne", "DEF", "B"), ("Oscar Ruggerii", "DEF", "A"),
        ("Julio Olarticoecheaa", "DEF", "B"), ("Jose Cuciuffoo", "DEF", "C"), ("Sergio Battista", "MID", "B"),
        ("Ricardo Giustii", "MID", "B"), ("Hector Enriquez", "MID", "C"), ("Jorge Valdanoo", "FWD", "A"),
        ("Jorge Burruchagaa", "FWD", "A"), ("Diego Maradonna", "FWD", "S"), ("Marcelo Trobbianii", "MID", "C"),
    ]),
    ("Germany", 2014, "2014 World Cup Winners", [
        ("Manuel Neuerr", "GK", "S"), ("Philipp Lahmm", "DEF", "S"), ("Jerome Boatengg", "DEF", "A"),
        ("Mats Hummelss", "DEF", "A"), ("Benedikt Howedess", "DEF", "B"), ("Toni Krooss", "MID", "S"),
        ("Sami Khedirah", "MID", "A"), ("Bastian Schweinsteigerr", "MID", "A"), ("Mesut Ozili", "MID", "A"),
        ("Thomas Mulerr", "FWD", "S"), ("Miroslav Klosee", "FWD", "A"), ("Mario Gotzee", "FWD", "B"),
    ]),
    ("France", 1998, "1998 World Cup Winners", [
        ("Fabien Barthezz", "GK", "A"), ("Marcel Desaillyy", "DEF", "A"), ("Laurent Blancc", "DEF", "A"),
        ("Lilian Thuramm", "DEF", "A"), ("Bixente Lizarazuu", "DEF", "B"), ("Didier Deschampps", "MID", "B"),
        ("Zinedine Zidanne", "MID", "S"), ("Emmanuel Petitt", "MID", "A"), ("Youri Djorkaeffe", "MID", "B"),
        ("Stephane Guivarch", "FWD", "C"), ("Thierry Henryy", "FWD", "A"), ("Christophe Dugarryy", "FWD", "B"),
    ]),
    ("Spain", 2010, "2010 World Cup Winners", [
        ("Iker Casillass", "GK", "S"), ("Carles Puyoll", "DEF", "A"), ("Gerard Piquee", "DEF", "A"),
        ("Sergio Ramoss", "DEF", "S"), ("Joan Capdevilaa", "DEF", "B"), ("Xavi Hernandezz", "MID", "S"),
        ("Andres Iniestaa", "MID", "S"), ("Sergio Busquetss", "MID", "A"), ("Xabi Alonsoo", "MID", "A"),
        ("David Villaa", "FWD", "A"), ("Fernando Torress", "FWD", "A"), ("Pedro Rodriguezz", "FWD", "B"),
    ]),
    ("Argentina", 2022, "2022 World Cup Winners", [
        ("Emiliano Martinezz", "GK", "A"), ("Nicolas Otamendii", "DEF", "B"), ("Cristian Romeroo", "DEF", "A"),
        ("Nahuel Molinaa", "DEF", "B"), ("Marcos Acunaa", "DEF", "B"), ("Rodrigo De Paull", "MID", "A"),
        ("Enzo Fernandezz", "MID", "A"), ("Alexis Mac Allisterr", "MID", "A"), ("Leandro Paredess", "MID", "B"),
        ("Lionel Messii", "FWD", "S"), ("Julian Alvarezz", "FWD", "A"), ("Angel Di Mariaa", "FWD", "A"),
    ]),
    ("Italy", 2006, "2006 World Cup Winners", [
        ("Gianluigi Buffonn", "GK", "S"), ("Fabio Cannavaroo", "DEF", "S"), ("Alessandro Nestaa", "DEF", "A"),
        ("Gianluca Zambrottaa", "DEF", "A"), ("Fabio Grossoo", "DEF", "B"), ("Andrea Pirloo", "MID", "S"),
        ("Gennaro Gattusoo", "MID", "A"), ("Mauro Camoranesii", "MID", "B"), ("Simone Perrottaa", "MID", "B"),
        ("Francesco Tottii", "FWD", "A"), ("Alessandro Del Pierro", "FWD", "A"), ("Luca Tonii", "FWD", "B"),
    ]),
    ("England", 1966, "1966 World Cup Winners", [
        ("Gordon Bankss", "GK", "A"), ("Bobby Mooree", "DEF", "S"), ("Jack Charltonn", "DEF", "A"),
        ("George Cohenn", "DEF", "B"), ("Ray Wilsonn", "DEF", "B"), ("Bobby Charltonn", "MID", "S"),
        ("Nobby Stiless", "MID", "B"), ("Alan Balll", "MID", "A"), ("Martin Peterss", "MID", "B"),
        ("Geoff Hurstt", "FWD", "A"), ("Roger Huntt", "FWD", "B"), ("Jimmy Greavess", "FWD", "B"),
    ]),
]


def build_player(name, role, tier):
    t = TIERS[tier]
    core = roll(t["core"])
    morale = roll(t["morale"])
    pace = roll((max(35, core - 15), min(96, core + 6)))

    if role == "GK":
        defense = core
        attack = round(random.uniform(5, 15), 1)
        passing = round(core * random.uniform(0.55, 0.7), 1)
    elif role == "DEF":
        defense = core
        attack = round(core * random.uniform(0.35, 0.5), 1)
        passing = round(core * random.uniform(0.6, 0.8), 1)
    elif role == "MID":
        passing = core
        attack = round(core * random.uniform(0.65, 0.85), 1)
        defense = round(core * random.uniform(0.6, 0.8), 1)
    else:  # FWD
        attack = core
        defense = round(core * random.uniform(0.2, 0.4), 1)
        passing = round(core * random.uniform(0.55, 0.75), 1)

    return {
        "name": name, "role": role, "attack": attack, "defense": defense,
        "passing": passing, "pace": pace, "morale": morale,
    }


def rating_for(role, attack, defense, passing, morale):
    if role == "GK":
        base = defense * 0.7 + passing * 0.3
    elif role == "DEF":
        base = defense * 0.6 + attack * 0.2 + passing * 0.2
    elif role == "MID":
        base = passing * 0.4 + attack * 0.3 + defense * 0.3
    else:
        base = attack * 0.6 + passing * 0.25 + 0.15 * (attack + defense) / 2
    return round(base * (0.8 + 0.2 * (morale / 100)), 1)


def credits_for(rating):
    # Stretch the actual observed rating range (~30-85) across the full
    # credit band, rather than a fixed scale that barely engages it - a
    # narrow credit spread makes random drafting too prone to budget
    # dead ends (every player costing near-average leaves no slack).
    span = min(1.0, max(0.0, (rating - 32.0) / (85.0 - 32.0)))
    c = 5.5 + span * 5.5
    return round(c * 2) / 2


players = []
pid = 1
for country, era, squad_name, roster in SQUADS:
    for (name, role, tier) in roster:
        p = build_player(name, role, tier)
        rating = rating_for(role, p["attack"], p["defense"], p["passing"], p["morale"])
        credit = credits_for(rating)
        players.append({
            "id": pid,
            "name": p["name"],
            "country": country,
            "era": era,
            "squad_name": squad_name,
            "role": role,
            "attack": p["attack"],
            "defense": p["defense"],
            "passing": p["passing"],
            "pace": p["pace"],
            "morale": p["morale"],
            "rating": rating,
            "credit": credit,
        })
        pid += 1

out_path = os.path.join(os.path.dirname(__file__), "players.json")
with open(out_path, "w") as f:
    json.dump(players, f, indent=2)

print(f"wrote {len(players)} players across {len(SQUADS)} squads to {out_path}")
