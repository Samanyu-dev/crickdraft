from typing import Optional

TOURNAMENTS = {
    "world-series": {
        "slug": "world-series",
        "name": "World Series",
        "tagline": "Any squad, any era",
        "era_min": None,
        "era_max": None,
    },
    "champions-series": {
        "slug": "champions-series",
        "name": "Champions Series",
        "tagline": "Modern-era squads only (2006+)",
        "era_min": 2006,
        "era_max": None,
    },
    "golden-era-cup": {
        "slug": "golden-era-cup",
        "name": "Golden Era Cup",
        "tagline": "Pre-2000 legends squads only",
        "era_min": None,
        "era_max": 1999,
    },
}

DEFAULT_TOURNAMENT = "world-series"


def get_tournament(slug: Optional[str]) -> dict:
    return TOURNAMENTS.get(slug or DEFAULT_TOURNAMENT, TOURNAMENTS[DEFAULT_TOURNAMENT])


def list_tournaments() -> list:
    return list(TOURNAMENTS.values())
