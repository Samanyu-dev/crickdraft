"""
Tournament definitions. Each tournament is a (squad-pool filter, match
format) pair with its own Elo ladder - picked before drafting, since the
squad pool determines what you can even roll.
"""
from typing import Optional

TOURNAMENTS = {
    "showdown-league": {
        "slug": "showdown-league",
        "name": "Showdown League",
        "tagline": "Franchise-style T20 - any squad, any era",
        "format": "T20",
        "overs": 20,
        "innings_per_side": 1,
        "era_min": None,
        "era_max": None,
    },
    "world-championship": {
        "slug": "world-championship",
        "name": "World Championship",
        "tagline": "50-over showpiece - modern-era international squads only",
        "format": "ODI",
        "overs": 50,
        "innings_per_side": 1,
        "era_min": 2015,
        "era_max": None,
    },
    "classic-series": {
        "slug": "classic-series",
        "name": "Classic Series",
        "tagline": "20-over cricket, pre-2000 legends squads only",
        "format": "T20",
        "overs": 20,
        "innings_per_side": 1,
        "era_min": None,
        "era_max": 1999,
    },
    "test-trophy": {
        "slug": "test-trophy",
        "name": "Test Trophy",
        "tagline": "Two innings a side - draws are possible, any squad or era",
        "format": "TEST",
        "overs": 50,
        "innings_per_side": 2,
        "era_min": None,
        "era_max": None,
    },
}

DEFAULT_TOURNAMENT = "showdown-league"


def get_tournament(slug: Optional[str]) -> dict:
    return TOURNAMENTS.get(slug or DEFAULT_TOURNAMENT, TOURNAMENTS[DEFAULT_TOURNAMENT])


def list_tournaments() -> list:
    return list(TOURNAMENTS.values())
