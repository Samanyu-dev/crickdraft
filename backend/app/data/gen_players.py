"""
Generator for players.json. Players are grouped into SQUADS: one squad is a
specific (country, era) roster of 11-13 players, mirroring a real historic
team without using anyone's exact real name (names are deliberately altered).
Stats are approximate/illustrative, derived from a tier archetype, not
official records.

Run: python3 gen_players.py  (writes players.json next to this file)
"""
import json
import os
import random

random.seed(42)

# tier -> stat ranges. AR players draw from the SAME tier for both bat and
# bowl; the simulation engine already discounts all-rounder contributions.
TIERS = {
    "S": dict(bat_avg=(55, 68), bat_sr=(85, 108), bowl_avg=(18, 24), bowl_econ=(2.3, 3.2), bowl_sr=(38, 48), consistency=(0.85, 0.95)),
    "A": dict(bat_avg=(45, 55), bat_sr=(75, 95), bowl_avg=(22, 28), bowl_econ=(3.0, 4.2), bowl_sr=(44, 54), consistency=(0.75, 0.85)),
    "B": dict(bat_avg=(34, 45), bat_sr=(68, 88), bowl_avg=(26, 32), bowl_econ=(3.8, 5.0), bowl_sr=(50, 60), consistency=(0.65, 0.75)),
    "C": dict(bat_avg=(22, 34), bat_sr=(60, 80), bowl_avg=(29, 36), bowl_econ=(4.4, 5.6), bowl_sr=(55, 66), consistency=(0.55, 0.65)),
}


def roll(lo_hi):
    lo, hi = lo_hi
    return round(random.uniform(lo, hi), 1)


# Each squad: (country, era, squad_name, [(name, role, tier), ...])
SQUADS = [
    ("India", 1983, "1983 World Cup Winners", [
        ("Kapeel Dev", "AR", "S"), ("Sunil Gavaskaar", "BAT", "A"), ("Krish Srikanthh", "BAT", "B"),
        ("Mohinder Amarnathh", "AR", "A"), ("Yashpal Sharmaa", "BAT", "B"), ("Sandeep Patiil", "AR", "B"),
        ("Kirti Azaad", "BOWL", "C"), ("Roger Binnyy", "AR", "B"), ("Madan Laal", "BOWL", "B"),
        ("Syed Kirmanii", "WK", "B"), ("Balwinder Sandhuu", "BOWL", "C"), ("Ravi Shastrii", "AR", "B"),
    ]),
    ("India", 2011, "2011 World Cup Winners", [
        ("Sachin Tendulker", "BAT", "S"), ("Virender Sehwaag", "BAT", "A"), ("Gautam Gambheer", "BAT", "B"),
        ("Virat Kohly", "BAT", "A"), ("Yuvraj Singhal", "AR", "A"), ("MS Dhonir", "WK", "A"),
        ("Suresh Rainaa", "BAT", "B"), ("Zaheer Khaan", "BOWL", "A"), ("Harbajan Singhh", "BOWL", "B"),
        ("Ashish Nehraa", "BOWL", "B"), ("Munaf Pateel", "BOWL", "C"), ("R Ashwinn", "BOWL", "B"),
        ("Yusuf Pathaan", "AR", "C"),
    ]),
    ("India", 2019, "Modern Era", [
        ("Virat Kohly", "BAT", "S"), ("Rohit Sharmaa", "BAT", "A"), ("KL Rahull", "WK", "A"),
        ("Shikar Dhawann", "BAT", "B"), ("Rishabh Pantt", "WK", "B"), ("Ravindra Jadejaa", "AR", "A"),
        ("Hardik Pandiya", "AR", "B"), ("Jasprit Bumraah", "BOWL", "S"), ("Mohammed Shamii", "BOWL", "A"),
        ("Yuzvendra Chahaal", "BOWL", "B"), ("Kuldeep Yadhav", "BOWL", "B"), ("Shreyas Iyerr", "BAT", "B"),
        ("Bhuvneshwar Kumaar", "BOWL", "C"),
    ]),
    ("Australia", 1985, "1980s Ashes Era", [
        ("Allan Bordor", "BAT", "A"), ("Dean Jonness", "BAT", "B"), ("David Boone", "BAT", "B"),
        ("Geoff Marshh", "BAT", "C"), ("Dennis Lilee", "BOWL", "A"), ("Rodney Marshe", "WK", "B"),
        ("Jeff Thomsen", "BOWL", "B"), ("Kim Hughess", "BAT", "B"), ("Greg Chappelle", "BAT", "A"),
        ("Terry Aldermann", "BOWL", "C"), ("Craig McDermot", "BOWL", "B"),
    ]),
    ("Australia", 1999, "1999 World Cup Winners", [
        ("Steven Waughe", "BAT", "A"), ("Adam Gilchrest", "WK", "S"), ("Mark Waughe", "BAT", "A"),
        ("Ricky Pontin", "BAT", "A"), ("Michael Bevann", "BAT", "B"), ("Darren Lehmaan", "BAT", "B"),
        ("Shane Warnie", "BOWL", "S"), ("Glenn McGrah", "BOWL", "S"), ("Damien Flemmingg", "BOWL", "B"),
        ("Tom Moodey", "AR", "C"), ("Paul Reiffell", "BOWL", "C"), ("Shane Leey", "BOWL", "C"),
    ]),
    ("Australia", 2021, "Modern Era", [
        ("Patrick Cumminz", "BOWL", "S"), ("David Warnor", "BAT", "A"), ("Steve Smithe", "BAT", "S"),
        ("Marnus Labuschayne", "BAT", "A"), ("Glenn Maxwelll", "AR", "A"), ("Mitchell Starcy", "BOWL", "A"),
        ("Josh Hazzlewood", "BOWL", "A"), ("Adam Zampaa", "BOWL", "B"), ("Alex Careyy", "WK", "B"),
        ("Marcus Stoiniss", "AR", "B"), ("Mitchell Marshh", "AR", "B"),
    ]),
    ("West Indies", 1979, "1979 World Cup Champions", [
        ("Clive Loyd", "BAT", "A"), ("Vivian Richardsson", "BAT", "S"), ("Gordon Greenwich", "BAT", "A"),
        ("Desmond Haynz", "BAT", "B"), ("Alvin Kallicharann", "BAT", "B"), ("Andy Robarts", "BOWL", "A"),
        ("Michael Holdinng", "BOWL", "S"), ("Joel Garnerr", "BOWL", "A"), ("Colin Croftt", "BOWL", "B"),
        ("Deryck Murrayy", "WK", "B"), ("Collis Kingg", "AR", "C"),
    ]),
    ("West Indies", 1994, "Lara's Prime", [
        ("Brian Lahra", "BAT", "S"), ("Courtnay Walshe", "BOWL", "A"), ("Curtley Ambrosse", "BOWL", "S"),
        ("Shivnarine Chanderpaull", "BAT", "A"), ("Jimmy Adamss", "BAT", "B"), ("Carl Hooperr", "AR", "B"),
        ("Roland Holderr", "BAT", "C"), ("Junior Murrayy", "WK", "C"), ("Ottis Gibsonn", "BOWL", "C"),
        ("Ian Bishopp", "BOWL", "B"), ("Cameron Cuffey", "BOWL", "C"),
    ]),
    ("West Indies", 2016, "T20 World Champions", [
        ("Darren Sammyy", "AR", "B"), ("Chris Gale", "BAT", "A"), ("Marlon Samuelz", "BAT", "B"),
        ("Andre Russel", "AR", "A"), ("Dwayne Bravoo", "AR", "B"), ("Carlos Brathwaitee", "AR", "C"),
        ("Johnson Charless", "BAT", "C"), ("Lendl Simmonz", "BAT", "C"), ("Samuel Badreee", "BOWL", "C"),
        ("Sulieman Bennn", "BOWL", "C"), ("Denesh Ramdinn", "WK", "C"),
    ]),
    ("England", 1981, "Botham's Ashes", [
        ("Ian Bothum", "AR", "A"), ("Geoffrey Boycot", "BAT", "A"), ("Graham Gooche", "BAT", "B"),
        ("David Gowerr", "BAT", "A"), ("Mike Gattingg", "BAT", "B"), ("Bob Williss", "BOWL", "B"),
        ("Bob Taylorr", "WK", "C"), ("John Emburyy", "BOWL", "C"), ("Chris Oldd", "BOWL", "C"),
        ("Paul Allot", "BOWL", "C"), ("Derek Underwoodd", "BOWL", "B"),
    ]),
    ("England", 2005, "2005 Ashes Winners", [
        ("Michael Vaughn", "BAT", "A"), ("Andrew Strausse", "BAT", "B"), ("Marcus Trescothik", "BAT", "B"),
        ("Kevin Peterson", "BAT", "A"), ("Andrew Flintoft", "AR", "A"), ("Ian Belll", "BAT", "B"),
        ("Geraint Jonesz", "WK", "C"), ("Ashley Giless", "BOWL", "C"), ("Matthew Hoggardd", "BOWL", "B"),
        ("Steve Harmisonn", "BOWL", "B"), ("Simon Jonesz", "BOWL", "C"),
    ]),
    ("England", 2019, "2019 World Cup Winners", [
        ("Eoin Morgen", "BAT", "B"), ("Jason Royy", "BAT", "B"), ("Jonny Bairstoww", "BAT", "A"),
        ("Joe Rootes", "BAT", "S"), ("Ben Stoke", "AR", "A"), ("Jos Buttlerr", "WK", "A"),
        ("Chris Woakess", "AR", "B"), ("Liam Plunkettt", "BOWL", "C"), ("Jofra Archerr", "BOWL", "A"),
        ("Adil Rashidd", "BOWL", "B"), ("Mark Woodd", "BOWL", "B"),
    ]),
    ("Pakistan", 1992, "1992 World Cup Winners", [
        ("Imraan Khan", "AR", "A"), ("Javed Miandaad", "BAT", "A"), ("Waseem Akrem", "BOWL", "S"),
        ("Waqar Younuss", "BOWL", "S"), ("Inzamam ul Haque", "BAT", "A"), ("Aamer Sohaill", "BAT", "B"),
        ("Ramiz Rajaa", "BAT", "B"), ("Moin Khaan", "WK", "C"), ("Mushtaq Ahmedd", "BOWL", "B"),
        ("Aaqib Javeedd", "BOWL", "C"), ("Salim Malikk", "BAT", "B"),
    ]),
    ("Pakistan", 2009, "2009 T20 World Champions", [
        ("Younis Khaan", "BAT", "A"), ("Shahid Afreedi", "AR", "B"), ("Umar Akmall", "BAT", "B"),
        ("Kamran Akmall", "WK", "C"), ("Umar Gull", "BOWL", "B"), ("Shoaib Malikk", "AR", "B"),
        ("Abdul Razzaaq", "AR", "C"), ("Saeed Ajmall", "BOWL", "A"), ("Mohammad Aamerr", "BOWL", "B"),
        ("Sohail Tanveer", "BOWL", "C"), ("Fawad Alamm", "BAT", "C"),
    ]),
    ("Pakistan", 2021, "Modern Era", [
        ("Babur Azam", "BAT", "S"), ("Mohammad Rizwaan", "WK", "A"), ("Fakhar Zamaan", "BAT", "B"),
        ("Shaheen Afridee", "BOWL", "A"), ("Hasan Alii", "BOWL", "B"), ("Shadab Khaan", "AR", "B"),
        ("Imad Wasimm", "AR", "C"), ("Haris Raufi", "BOWL", "B"), ("Mohammad Hafeeze", "AR", "C"),
        ("Asif Alii", "BAT", "C"), ("Naseem Shahh", "BOWL", "B"),
    ]),
    ("South Africa", 1998, "Rainbow Era", [
        ("Hansie Cronjee", "AR", "B"), ("Gary Kirstenn", "BAT", "A"), ("Herschelle Gibbz", "BAT", "B"),
        ("Jacques Kallistad", "AR", "S"), ("Jonty Rhodess", "BAT", "B"), ("Lance Klusenerr", "AR", "A"),
        ("Mark Boucherr", "WK", "B"), ("Allan Donaldd", "BOWL", "A"), ("Shaun Pollockk", "AR", "A"),
        ("Paul Adamss", "BOWL", "C"), ("Fanie de Villierss", "BOWL", "C"),
    ]),
    ("South Africa", 2015, "AB's Era", [
        ("AB de Villierz", "BAT", "S"), ("Hashim Amlaa", "BAT", "A"), ("Quinton de Kok", "WK", "A"),
        ("Faf du Plessy", "BAT", "A"), ("David Millerr", "BAT", "B"), ("JP Duminyy", "AR", "B"),
        ("Dale Steyne", "BOWL", "S"), ("Morne Morkell", "BOWL", "A"), ("Imran Tahirr", "BOWL", "B"),
        ("Vernon Philanderr", "BOWL", "A"), ("Kyle Abbott", "BOWL", "C"),
    ]),
    ("South Africa", 2023, "Modern Era", [
        ("Temba Bavumaa", "BAT", "B"), ("Quinton de Kokk", "WK", "A"), ("Aiden Markraam", "BAT", "A"),
        ("Rassie van der Dussenn", "BAT", "A"), ("Heinrich Klaasenn", "BAT", "A"), ("David Millerz", "BAT", "B"),
        ("Marco Jansenn", "AR", "B"), ("Kagiso Rabadaa", "BOWL", "S"), ("Lungi Ngidii", "BOWL", "A"),
        ("Keshav Maharaaj", "BOWL", "B"), ("Tabraiz Shamsii", "BOWL", "B"),
    ]),
    ("Sri Lanka", 1996, "1996 World Cup Winners", [
        ("Arjuna Ranatungga", "AR", "B"), ("Sanath Jayasuryah", "AR", "A"), ("Romesh Kaluwitharanaa", "WK", "B"),
        ("Aravinda de Silvaa", "BAT", "A"), ("Asanka Gurusinhaa", "BAT", "B"), ("Roshan Mahanamaa", "BAT", "C"),
        ("Hashan Tillakaratnee", "BAT", "B"), ("Muttiah Muralidaran", "BOWL", "S"), ("Chaminda Vaass", "BOWL", "A"),
        ("Upul Chandanaa", "BOWL", "C"), ("Sajeewa de Silvaa", "BOWL", "C"),
    ]),
    ("Sri Lanka", 2011, "2011 World Cup Finalists", [
        ("Kumar Sangakarra", "WK", "S"), ("Mahela Jayawardana", "BAT", "A"), ("Tillakaratne Dilshann", "BAT", "A"),
        ("Upul Tharangaa", "BAT", "B"), ("Thisara Pereraa", "AR", "B"), ("Angelo Mathewss", "AR", "A"),
        ("Lasith Malingaa", "BOWL", "A"), ("Muttiah Muralidaran", "BOWL", "S"), ("Rangana Heratth", "BOWL", "B"),
        ("Nuwan Kulasekaraa", "BOWL", "C"), ("Suraj Randivv", "BOWL", "C"),
    ]),
    ("Sri Lanka", 2022, "Modern Era", [
        ("Dasun Shanakaa", "AR", "B"), ("Kusal Mendiss", "WK", "B"), ("Pathum Nissankaa", "BAT", "B"),
        ("Charith Asalankaa", "BAT", "B"), ("Wanindu Hasarangaa", "AR", "A"), ("Dhananjaya de Silvaa", "AR", "B"),
        ("Dushmantha Chameeraa", "BOWL", "B"), ("Maheesh Theekshanaa", "BOWL", "B"), ("Lahiru Kumaraa", "BOWL", "C"),
        ("Dilshan Madushankaa", "BOWL", "C"), ("Bhanuka Rajapaksaa", "BAT", "C"),
    ]),
    ("New Zealand", 1992, "1992 World Cup Semifinalists", [
        ("Martin Crowee", "BAT", "A"), ("John Wrightt", "BAT", "B"), ("Mark Greatbatchh", "BAT", "B"),
        ("Ken Rutherfordd", "BAT", "C"), ("Andrew Joness", "BAT", "C"), ("Chris Harriss", "AR", "C"),
        ("Ian Smithe", "WK", "C"), ("Gavin Larsenn", "BOWL", "C"), ("Danny Morrisonn", "BOWL", "B"),
        ("Willie Watsonn", "BOWL", "C"), ("Rod Lathamm", "AR", "C"),
    ]),
    ("New Zealand", 2015, "2015 World Cup Finalists", [
        ("Brendon McCullam", "WK", "A"), ("Martin Guptilll", "BAT", "B"), ("Kane Williamsen", "BAT", "A"),
        ("Ross Taylorr", "BAT", "B"), ("Grant Elliottt", "AR", "B"), ("Corey Andersonn", "AR", "B"),
        ("Luke Ronchii", "WK", "C"), ("Daniel Vettoryy", "BOWL", "B"), ("Tim Southeee", "BOWL", "A"),
        ("Trent Boultt", "BOWL", "A"), ("Adam Milnee", "BOWL", "C"),
    ]),
    ("New Zealand", 2021, "WTC Champions", [
        ("Kane Williamsen", "BAT", "S"), ("Tom Lathamm", "WK", "B"), ("Devon Conwayy", "BAT", "A"),
        ("Henry Nichollss", "BAT", "B"), ("Ross Taylorr", "BAT", "B"), ("Jimmy Neeshamm", "AR", "B"),
        ("Colin de Grandhommee", "AR", "C"), ("Mitchell Santnerr", "BOWL", "B"), ("Tim Southeee", "BOWL", "A"),
        ("Trent Boultt", "BOWL", "A"), ("Kyle Jamiesonn", "BOWL", "B"),
    ]),
]


def build_player(name, role, tier):
    t = TIERS[tier]
    consistency = roll(t["consistency"])
    if role in ("BAT", "WK"):
        return {
            "name": name, "role": role,
            "batting": {"avg": roll(t["bat_avg"]), "sr": roll(t["bat_sr"])},
            "bowling": None, "consistency": consistency,
        }
    if role == "BOWL":
        return {
            "name": name, "role": role, "batting": None,
            "bowling": {"avg": roll(t["bowl_avg"]), "econ": roll(t["bowl_econ"]), "sr": roll(t["bowl_sr"])},
            "consistency": consistency,
        }
    # AR: both, simulation.py already discounts all-rounder contributions
    return {
        "name": name, "role": role,
        "batting": {"avg": roll(t["bat_avg"]), "sr": roll(t["bat_sr"])},
        "bowling": {"avg": roll(t["bowl_avg"]), "econ": roll(t["bowl_econ"]), "sr": roll(t["bowl_sr"])},
        "consistency": consistency,
    }


def rating_for(role, bat, bowl, consistency):
    bat_score = 0.0
    if bat:
        bat_score = min(bat["avg"], 65) * 0.9 + min(bat["sr"], 130) * 0.25
    bowl_score = 0.0
    if bowl:
        bowl_score = max(0, 45 - bowl["avg"]) * 1.6 + max(0, 6.5 - bowl["econ"]) * 9 + max(0, 70 - bowl["sr"]) * 0.3
    if role in ("BAT", "WK"):
        base = bat_score
    elif role == "BOWL":
        base = bowl_score
    else:
        base = bat_score * 0.6 + bowl_score * 0.6
    return round(base * (0.75 + 0.25 * consistency), 1)


def credits_for(rating):
    c = 6.0 + (min(rating, 130) / 130.0) * 5.0
    return round(c * 2) / 2


players = []
pid = 1
for country, era, squad_name, roster in SQUADS:
    for (name, role, tier) in roster:
        p = build_player(name, role, tier)
        rating = rating_for(role, p["batting"], p["bowling"], p["consistency"])
        credit = credits_for(rating)
        players.append({
            "id": pid,
            "name": p["name"],
            "country": country,
            "era": era,
            "squad_name": squad_name,
            "role": role,
            "batting": p["batting"],
            "bowling": p["bowling"],
            "rating": rating,
            "credit": credit,
            "consistency": p["consistency"],
        })
        pid += 1

out_path = os.path.join(os.path.dirname(__file__), "players.json")
with open(out_path, "w") as f:
    json.dump(players, f, indent=2)

print(f"wrote {len(players)} players across {len(SQUADS)} squads to {out_path}")
