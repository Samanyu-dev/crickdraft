"""
Generator for players.json. Players are grouped into SQUADS: one squad is a
specific (country, era) roster of 11-13 players, mirroring a real historic
team without using anyone's exact real name (names are deliberately altered).

Each player carries four skill dimensions - batting, bowling, fielding,
morale - plus a (position_min, position_max) batting-order restriction
based on how that player actually batted historically (openers can only
slot in at 1-2, recognized #3s at 1-3, tailenders at 8-11, etc).

Stats are approximate/illustrative, not official records.
Run: python3 gen_players.py  (writes players.json next to this file)
"""
import json
import os
import random

random.seed(42)

TIERS = {
    "S": dict(bat_avg=(55, 68), bat_sr=(85, 108), bowl_avg=(18, 24), bowl_econ=(2.3, 3.2), bowl_sr=(38, 48),
              consistency=(0.85, 0.95), fielding=(78, 95), morale=(75, 95)),
    "A": dict(bat_avg=(45, 55), bat_sr=(75, 95), bowl_avg=(22, 28), bowl_econ=(3.0, 4.2), bowl_sr=(44, 54),
              consistency=(0.75, 0.85), fielding=(68, 85), morale=(65, 85)),
    "B": dict(bat_avg=(34, 45), bat_sr=(68, 88), bowl_avg=(26, 32), bowl_econ=(3.8, 5.0), bowl_sr=(50, 60),
              consistency=(0.65, 0.75), fielding=(55, 75), morale=(55, 75)),
    "C": dict(bat_avg=(22, 34), bat_sr=(60, 80), bowl_avg=(29, 36), bowl_econ=(4.4, 5.6), bowl_sr=(55, 66),
              consistency=(0.55, 0.65), fielding=(40, 62), morale=(40, 65)),
}


def roll(lo_hi):
    lo, hi = lo_hi
    return round(random.uniform(lo, hi), 1)


# Each squad: (country, era, squad_name, [(name, role, tier, pos_min, pos_max), ...])
# Position range reflects how that player actually batted historically.
SQUADS = [
    ("India", 1983, "1983 World Cup Winners", [
        ("Kapeel Dev", "AR", "S", 5, 7), ("Sunil Gavaskaar", "BAT", "A", 1, 2), ("Krish Srikanthh", "BAT", "B", 1, 2),
        ("Mohinder Amarnathh", "AR", "A", 3, 5), ("Yashpal Sharmaa", "BAT", "B", 3, 5), ("Sandeep Patiil", "AR", "B", 4, 6),
        ("Kirti Azaad", "BOWL", "C", 8, 10), ("Roger Binnyy", "AR", "B", 6, 8), ("Madan Laal", "BOWL", "B", 8, 10),
        ("Syed Kirmanii", "WK", "B", 6, 8), ("Balwinder Sandhuu", "BOWL", "C", 9, 11), ("Ravi Shastrii", "AR", "B", 5, 7),
    ]),
    ("India", 2011, "2011 World Cup Winners", [
        ("Sachin Tendulker", "BAT", "S", 1, 2), ("Virender Sehwaag", "BAT", "A", 1, 2), ("Gautam Gambheer", "BAT", "B", 1, 2),
        ("Virat Kohly", "BAT", "A", 1, 3), ("Yuvraj Singhal", "AR", "A", 3, 5), ("MS Dhonir", "WK", "A", 5, 7),
        ("Suresh Rainaa", "BAT", "B", 4, 6), ("Zaheer Khaan", "BOWL", "A", 9, 11), ("Harbajan Singhh", "BOWL", "B", 8, 10),
        ("Ashish Nehraa", "BOWL", "B", 9, 11), ("Munaf Pateel", "BOWL", "C", 10, 11), ("R Ashwinn", "BOWL", "B", 8, 10),
        ("Yusuf Pathaan", "AR", "C", 6, 8),
    ]),
    ("India", 2019, "Modern Era", [
        ("Virat Kohly", "BAT", "S", 1, 3), ("Rohit Sharmaa", "BAT", "A", 1, 2), ("KL Rahull", "WK", "A", 1, 4),
        ("Shikar Dhawann", "BAT", "B", 1, 2), ("Rishabh Pantt", "WK", "B", 4, 6), ("Ravindra Jadejaa", "AR", "A", 6, 8),
        ("Hardik Pandiya", "AR", "B", 5, 7), ("Jasprit Bumraah", "BOWL", "S", 10, 11), ("Mohammed Shamii", "BOWL", "A", 9, 11),
        ("Yuzvendra Chahaal", "BOWL", "B", 10, 11), ("Kuldeep Yadhav", "BOWL", "B", 10, 11), ("Shreyas Iyerr", "BAT", "B", 3, 5),
        ("Bhuvneshwar Kumaar", "BOWL", "C", 9, 11),
    ]),
    ("Australia", 1985, "1980s Ashes Era", [
        ("Allan Bordor", "BAT", "A", 3, 5), ("Dean Jonness", "BAT", "B", 3, 5), ("David Boone", "BAT", "B", 1, 2),
        ("Geoff Marshh", "BAT", "C", 1, 2), ("Dennis Lilee", "BOWL", "A", 9, 11), ("Rodney Marshe", "WK", "B", 6, 8),
        ("Jeff Thomsen", "BOWL", "B", 9, 11), ("Kim Hughess", "BAT", "B", 3, 6), ("Greg Chappelle", "BAT", "A", 3, 5),
        ("Terry Aldermann", "BOWL", "C", 10, 11), ("Craig McDermot", "BOWL", "B", 9, 11),
    ]),
    ("Australia", 1999, "1999 World Cup Winners", [
        ("Steven Waughe", "BAT", "A", 3, 5), ("Adam Gilchrest", "WK", "S", 1, 3), ("Mark Waughe", "BAT", "A", 2, 4),
        ("Ricky Pontin", "BAT", "A", 2, 4), ("Michael Bevann", "BAT", "B", 5, 7), ("Darren Lehmaan", "BAT", "B", 4, 6),
        ("Shane Warnie", "BOWL", "S", 8, 10), ("Glenn McGrah", "BOWL", "S", 10, 11), ("Damien Flemmingg", "BOWL", "B", 9, 11),
        ("Tom Moodey", "AR", "C", 6, 8), ("Paul Reiffell", "BOWL", "C", 9, 11), ("Shane Leey", "BOWL", "C", 10, 11),
    ]),
    ("Australia", 2021, "Modern Era", [
        ("Patrick Cumminz", "BOWL", "S", 9, 11), ("David Warnor", "BAT", "A", 1, 2), ("Steve Smithe", "BAT", "S", 2, 4),
        ("Marnus Labuschayne", "BAT", "A", 2, 4), ("Glenn Maxwelll", "AR", "A", 4, 6), ("Mitchell Starcy", "BOWL", "A", 9, 11),
        ("Josh Hazzlewood", "BOWL", "A", 10, 11), ("Adam Zampaa", "BOWL", "B", 10, 11), ("Alex Careyy", "WK", "B", 5, 7),
        ("Marcus Stoiniss", "AR", "B", 4, 7), ("Mitchell Marshh", "AR", "B", 3, 6),
    ]),
    ("West Indies", 1979, "1979 World Cup Champions", [
        ("Clive Loyd", "BAT", "A", 4, 6), ("Vivian Richardsson", "BAT", "S", 2, 4), ("Gordon Greenwich", "BAT", "A", 1, 2),
        ("Desmond Haynz", "BAT", "B", 1, 2), ("Alvin Kallicharann", "BAT", "B", 3, 5), ("Andy Robarts", "BOWL", "A", 9, 11),
        ("Michael Holdinng", "BOWL", "S", 9, 11), ("Joel Garnerr", "BOWL", "A", 10, 11), ("Colin Croftt", "BOWL", "B", 10, 11),
        ("Deryck Murrayy", "WK", "B", 6, 8), ("Collis Kingg", "AR", "C", 5, 7),
    ]),
    ("West Indies", 1994, "Lara's Prime", [
        ("Brian Lahra", "BAT", "S", 2, 4), ("Courtnay Walshe", "BOWL", "A", 10, 11), ("Curtley Ambrosse", "BOWL", "S", 9, 11),
        ("Shivnarine Chanderpaull", "BAT", "A", 3, 5), ("Jimmy Adamss", "BAT", "B", 3, 6), ("Carl Hooperr", "AR", "B", 4, 6),
        ("Roland Holderr", "BAT", "C", 4, 6), ("Junior Murrayy", "WK", "C", 6, 8), ("Ottis Gibsonn", "BOWL", "C", 9, 11),
        ("Ian Bishopp", "BOWL", "B", 9, 11), ("Cameron Cuffey", "BOWL", "C", 10, 11),
    ]),
    ("West Indies", 2016, "T20 World Champions", [
        ("Darren Sammyy", "AR", "B", 5, 8), ("Chris Gale", "BAT", "A", 1, 2), ("Marlon Samuelz", "BAT", "B", 2, 4),
        ("Andre Russel", "AR", "A", 5, 7), ("Dwayne Bravoo", "AR", "B", 5, 8), ("Carlos Brathwaitee", "AR", "C", 6, 9),
        ("Johnson Charless", "BAT", "C", 1, 3), ("Lendl Simmonz", "BAT", "C", 1, 3), ("Samuel Badreee", "BOWL", "C", 9, 11),
        ("Sulieman Bennn", "BOWL", "C", 9, 11), ("Denesh Ramdinn", "WK", "C", 4, 7),
    ]),
    ("England", 1981, "Botham's Ashes", [
        ("Ian Bothum", "AR", "A", 4, 6), ("Geoffrey Boycot", "BAT", "A", 1, 2), ("Graham Gooche", "BAT", "B", 1, 2),
        ("David Gowerr", "BAT", "A", 2, 4), ("Mike Gattingg", "BAT", "B", 3, 5), ("Bob Williss", "BOWL", "B", 9, 11),
        ("Bob Taylorr", "WK", "C", 6, 8), ("John Emburyy", "BOWL", "C", 9, 11), ("Chris Oldd", "BOWL", "C", 8, 10),
        ("Paul Allot", "BOWL", "C", 9, 11), ("Derek Underwoodd", "BOWL", "B", 10, 11),
    ]),
    ("England", 2005, "2005 Ashes Winners", [
        ("Michael Vaughn", "BAT", "A", 1, 3), ("Andrew Strausse", "BAT", "B", 1, 2), ("Marcus Trescothik", "BAT", "B", 1, 2),
        ("Kevin Peterson", "BAT", "A", 3, 5), ("Andrew Flintoft", "AR", "A", 5, 7), ("Ian Belll", "BAT", "B", 3, 5),
        ("Geraint Jonesz", "WK", "C", 6, 8), ("Ashley Giless", "BOWL", "C", 8, 10), ("Matthew Hoggardd", "BOWL", "B", 9, 11),
        ("Steve Harmisonn", "BOWL", "B", 10, 11), ("Simon Jonesz", "BOWL", "C", 9, 11),
    ]),
    ("England", 2019, "2019 World Cup Winners", [
        ("Eoin Morgen", "BAT", "B", 3, 5), ("Jason Royy", "BAT", "B", 1, 2), ("Jonny Bairstoww", "BAT", "A", 1, 3),
        ("Joe Rootes", "BAT", "S", 2, 4), ("Ben Stoke", "AR", "A", 4, 6), ("Jos Buttlerr", "WK", "A", 5, 7),
        ("Chris Woakess", "AR", "B", 6, 8), ("Liam Plunkettt", "BOWL", "C", 9, 11), ("Jofra Archerr", "BOWL", "A", 9, 11),
        ("Adil Rashidd", "BOWL", "B", 10, 11), ("Mark Woodd", "BOWL", "B", 10, 11),
    ]),
    ("Pakistan", 1992, "1992 World Cup Winners", [
        ("Imraan Khan", "AR", "A", 3, 5), ("Javed Miandaad", "BAT", "A", 3, 5), ("Waseem Akrem", "BOWL", "S", 7, 9),
        ("Waqar Younuss", "BOWL", "S", 10, 11), ("Inzamam ul Haque", "BAT", "A", 3, 5), ("Aamer Sohaill", "BAT", "B", 1, 2),
        ("Ramiz Rajaa", "BAT", "B", 1, 2), ("Moin Khaan", "WK", "C", 6, 8), ("Mushtaq Ahmedd", "BOWL", "B", 9, 11),
        ("Aaqib Javeedd", "BOWL", "C", 9, 11), ("Salim Malikk", "BAT", "B", 3, 5),
    ]),
    ("Pakistan", 2009, "2009 T20 World Champions", [
        ("Younis Khaan", "BAT", "A", 2, 4), ("Shahid Afreedi", "AR", "B", 3, 6), ("Umar Akmall", "BAT", "B", 3, 6),
        ("Kamran Akmall", "WK", "C", 5, 7), ("Umar Gull", "BOWL", "B", 9, 11), ("Shoaib Malikk", "AR", "B", 3, 6),
        ("Abdul Razzaaq", "AR", "C", 5, 8), ("Saeed Ajmall", "BOWL", "A", 9, 11), ("Mohammad Aamerr", "BOWL", "B", 10, 11),
        ("Sohail Tanveer", "BOWL", "C", 8, 10), ("Fawad Alamm", "BAT", "C", 4, 6),
    ]),
    ("Pakistan", 2021, "Modern Era", [
        ("Babur Azam", "BAT", "S", 2, 4), ("Mohammad Rizwaan", "WK", "A", 1, 3), ("Fakhar Zamaan", "BAT", "B", 1, 2),
        ("Shaheen Afridee", "BOWL", "A", 9, 11), ("Hasan Alii", "BOWL", "B", 9, 11), ("Shadab Khaan", "AR", "B", 5, 8),
        ("Imad Wasimm", "AR", "C", 5, 8), ("Haris Raufi", "BOWL", "B", 10, 11), ("Mohammad Hafeeze", "AR", "C", 1, 4),
        ("Asif Alii", "BAT", "C", 5, 7), ("Naseem Shahh", "BOWL", "B", 10, 11),
    ]),
    ("South Africa", 1998, "Rainbow Era", [
        ("Hansie Cronjee", "AR", "B", 4, 6), ("Gary Kirstenn", "BAT", "A", 1, 2), ("Herschelle Gibbz", "BAT", "B", 1, 2),
        ("Jacques Kallistad", "AR", "S", 2, 4), ("Jonty Rhodess", "BAT", "B", 5, 7), ("Lance Klusenerr", "AR", "A", 6, 8),
        ("Mark Boucherr", "WK", "B", 6, 8), ("Allan Donaldd", "BOWL", "A", 9, 11), ("Shaun Pollockk", "AR", "A", 6, 9),
        ("Paul Adamss", "BOWL", "C", 10, 11), ("Fanie de Villierss", "BOWL", "C", 9, 11),
    ]),
    ("South Africa", 2015, "AB's Era", [
        ("AB de Villierz", "BAT", "S", 3, 5), ("Hashim Amlaa", "BAT", "A", 2, 4), ("Quinton de Kok", "WK", "A", 1, 3),
        ("Faf du Plessy", "BAT", "A", 2, 4), ("David Millerr", "BAT", "B", 5, 7), ("JP Duminyy", "AR", "B", 4, 7),
        ("Dale Steyne", "BOWL", "S", 9, 11), ("Morne Morkell", "BOWL", "A", 10, 11), ("Imran Tahirr", "BOWL", "B", 10, 11),
        ("Vernon Philanderr", "BOWL", "A", 8, 10), ("Kyle Abbott", "BOWL", "C", 9, 11),
    ]),
    ("South Africa", 2023, "Modern Era", [
        ("Temba Bavumaa", "BAT", "B", 2, 4), ("Quinton de Kokk", "WK", "A", 1, 2), ("Aiden Markraam", "BAT", "A", 1, 3),
        ("Rassie van der Dussenn", "BAT", "A", 3, 5), ("Heinrich Klaasenn", "BAT", "A", 4, 7), ("David Millerz", "BAT", "B", 5, 7),
        ("Marco Jansenn", "AR", "B", 6, 9), ("Kagiso Rabadaa", "BOWL", "S", 9, 11), ("Lungi Ngidii", "BOWL", "A", 10, 11),
        ("Keshav Maharaaj", "BOWL", "B", 9, 11), ("Tabraiz Shamsii", "BOWL", "B", 10, 11),
    ]),
    ("Sri Lanka", 1996, "1996 World Cup Winners", [
        ("Arjuna Ranatungga", "AR", "B", 2, 4), ("Sanath Jayasuryah", "AR", "A", 1, 2), ("Romesh Kaluwitharanaa", "WK", "B", 1, 3),
        ("Aravinda de Silvaa", "BAT", "A", 2, 4), ("Asanka Gurusinhaa", "BAT", "B", 1, 3), ("Roshan Mahanamaa", "BAT", "C", 1, 3),
        ("Hashan Tillakaratnee", "BAT", "B", 4, 6), ("Muttiah Muralidaran", "BOWL", "S", 10, 11), ("Chaminda Vaass", "BOWL", "A", 8, 10),
        ("Upul Chandanaa", "BOWL", "C", 9, 11), ("Sajeewa de Silvaa", "BOWL", "C", 10, 11),
    ]),
    ("Sri Lanka", 2011, "2011 World Cup Finalists", [
        ("Kumar Sangakarra", "WK", "S", 2, 4), ("Mahela Jayawardana", "BAT", "A", 3, 5), ("Tillakaratne Dilshann", "BAT", "A", 1, 2),
        ("Upul Tharangaa", "BAT", "B", 1, 2), ("Thisara Pereraa", "AR", "B", 6, 9), ("Angelo Mathewss", "AR", "A", 4, 7),
        ("Lasith Malingaa", "BOWL", "A", 9, 11), ("Muttiah Muralidaran", "BOWL", "S", 10, 11), ("Rangana Heratth", "BOWL", "B", 9, 11),
        ("Nuwan Kulasekaraa", "BOWL", "C", 8, 10), ("Suraj Randivv", "BOWL", "C", 10, 11),
    ]),
    ("Sri Lanka", 2022, "Modern Era", [
        ("Dasun Shanakaa", "AR", "B", 4, 7), ("Kusal Mendiss", "WK", "B", 1, 4), ("Pathum Nissankaa", "BAT", "B", 1, 2),
        ("Charith Asalankaa", "BAT", "B", 3, 6), ("Wanindu Hasarangaa", "AR", "A", 6, 9), ("Dhananjaya de Silvaa", "AR", "B", 3, 6),
        ("Dushmantha Chameeraa", "BOWL", "B", 9, 11), ("Maheesh Theekshanaa", "BOWL", "B", 10, 11), ("Lahiru Kumaraa", "BOWL", "C", 10, 11),
        ("Dilshan Madushankaa", "BOWL", "C", 10, 11), ("Bhanuka Rajapaksaa", "BAT", "C", 4, 7),
    ]),
    ("New Zealand", 1992, "1992 World Cup Semifinalists", [
        ("Martin Crowee", "BAT", "A", 2, 4), ("John Wrightt", "BAT", "B", 1, 2), ("Mark Greatbatchh", "BAT", "B", 1, 2),
        ("Ken Rutherfordd", "BAT", "C", 3, 6), ("Andrew Joness", "BAT", "C", 1, 3), ("Chris Harriss", "AR", "C", 5, 8),
        ("Ian Smithe", "WK", "C", 6, 9), ("Gavin Larsenn", "BOWL", "C", 8, 10), ("Danny Morrisonn", "BOWL", "B", 9, 11),
        ("Willie Watsonn", "BOWL", "C", 10, 11), ("Rod Lathamm", "AR", "C", 1, 4),
    ]),
    ("New Zealand", 2015, "2015 World Cup Finalists", [
        ("Brendon McCullam", "WK", "A", 1, 2), ("Martin Guptilll", "BAT", "B", 1, 2), ("Kane Williamsen", "BAT", "A", 2, 4),
        ("Ross Taylorr", "BAT", "B", 3, 5), ("Grant Elliottt", "AR", "B", 4, 7), ("Corey Andersonn", "AR", "B", 5, 8),
        ("Luke Ronchii", "WK", "C", 6, 8), ("Daniel Vettoryy", "BOWL", "B", 8, 10), ("Tim Southeee", "BOWL", "A", 9, 11),
        ("Trent Boultt", "BOWL", "A", 10, 11), ("Adam Milnee", "BOWL", "C", 10, 11),
    ]),
    ("New Zealand", 2021, "WTC Champions", [
        ("Kane Williamsen", "BAT", "S", 2, 4), ("Tom Lathamm", "WK", "B", 1, 2), ("Devon Conwayy", "BAT", "A", 1, 2),
        ("Henry Nichollss", "BAT", "B", 3, 6), ("Ross Taylorr", "BAT", "B", 3, 6), ("Jimmy Neeshamm", "AR", "B", 5, 8),
        ("Colin de Grandhommee", "AR", "C", 5, 8), ("Mitchell Santnerr", "BOWL", "B", 8, 10), ("Tim Southeee", "BOWL", "A", 9, 11),
        ("Trent Boultt", "BOWL", "A", 10, 11), ("Kyle Jamiesonn", "BOWL", "B", 8, 10),
    ]),
]


def build_player(name, role, tier):
    t = TIERS[tier]
    consistency = roll(t["consistency"])
    fielding = roll(t["fielding"])
    morale = roll(t["morale"])
    base = {"name": name, "role": role, "consistency": consistency, "fielding": fielding, "morale": morale}
    if role in ("BAT", "WK"):
        base["batting"] = {"avg": roll(t["bat_avg"]), "sr": roll(t["bat_sr"])}
        base["bowling"] = None
    elif role == "BOWL":
        base["batting"] = None
        base["bowling"] = {"avg": roll(t["bowl_avg"]), "econ": roll(t["bowl_econ"]), "sr": roll(t["bowl_sr"])}
    else:  # AR
        base["batting"] = {"avg": roll(t["bat_avg"]), "sr": roll(t["bat_sr"])}
        base["bowling"] = {"avg": roll(t["bowl_avg"]), "econ": roll(t["bowl_econ"]), "sr": roll(t["bowl_sr"])}
    return base


def rating_for(role, bat, bowl, fielding, consistency):
    bat_score = 0.0
    if bat:
        bat_score = min(bat["avg"], 65) * 0.9 + min(bat["sr"], 130) * 0.25
    bowl_score = 0.0
    if bowl:
        bowl_score = max(0, 45 - bowl["avg"]) * 1.6 + max(0, 6.5 - bowl["econ"]) * 9 + max(0, 70 - bowl["sr"]) * 0.3
    if role in ("BAT", "WK"):
        base = bat_score + fielding * 0.08
    elif role == "BOWL":
        base = bowl_score + fielding * 0.05
    else:
        base = bat_score * 0.6 + bowl_score * 0.6 + fielding * 0.08
    return round(base * (0.75 + 0.25 * consistency), 1)


def credits_for(rating):
    c = 6.0 + (min(rating, 130) / 130.0) * 5.0
    return round(c * 2) / 2


players = []
pid = 1
for country, era, squad_name, roster in SQUADS:
    for (name, role, tier, pos_min, pos_max) in roster:
        p = build_player(name, role, tier)
        rating = rating_for(role, p["batting"], p["bowling"], p["fielding"], p["consistency"])
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
            "fielding": p["fielding"],
            "morale": p["morale"],
            "rating": rating,
            "credit": credit,
            "consistency": p["consistency"],
            "position_min": pos_min,
            "position_max": pos_max,
        })
        pid += 1

out_path = os.path.join(os.path.dirname(__file__), "players.json")
with open(out_path, "w") as f:
    json.dump(players, f, indent=2)

print(f"wrote {len(players)} players across {len(SQUADS)} squads to {out_path}")
