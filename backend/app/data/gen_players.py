"""
One-off generator for players.json.
Names are inspired by real cricket legends but deliberately altered
(different spelling/surname) so no real player's exact name/identity is used.
Stats are approximate/illustrative, not official records.
Run: python3 gen_players.py  (writes players.json next to this file)
"""
import json
import os

# (name, country, era_year, role, bat_avg, bat_sr, bowl_avg, bowl_econ, bowl_sr, consistency)
# role: BAT, BOWL, AR, WK
RAW = [
    # ---------------- INDIA ----------------
    ("Sachin Tendulker", "India", 1998, "BAT", 55.0, 89.0, None, None, None, 0.85),
    ("Sachin Tendulker", "India", 2010, "BAT", 60.5, 82.0, None, None, None, 0.88),
    ("Virat Kohly", "India", 2016, "BAT", 63.0, 92.0, None, None, None, 0.9),
    ("Virat Kohly", "India", 2023, "BAT", 58.0, 95.0, None, None, None, 0.86),
    ("Rahul Draviid", "India", 2002, "BAT", 52.0, 71.0, None, None, None, 0.82),
    ("Sourabh Ganguly", "India", 1999, "BAT", 45.0, 82.0, 45.0, 5.2, 45.0, 0.7),
    ("VVS Laxsman", "India", 2001, "BAT", 47.0, 68.0, None, None, None, 0.68),
    "MSDONI_PLACEHOLDER",
    ("MS Dhonir", "India", 2011, "WK", 50.0, 88.0, None, None, None, 0.83),
    ("Virender Sehwaag", "India", 2004, "BAT", 49.0, 104.0, None, None, None, 0.65),
    ("Yuvraj Singhal", "India", 2011, "AR", 36.0, 87.0, 38.0, 5.1, 42.0, 0.6),
    ("Kapeel Dev", "India", 1983, "AR", 31.0, 72.0, 29.0, 3.7, 60.0, 0.75),
    ("Sunil Gavaskaar", "India", 1979, "BAT", 51.0, 62.0, None, None, None, 0.8),
    ("Anil Kumbley", "India", 1999, "BOWL", 8.0, 45.0, 29.0, 4.3, 52.0, 0.78),
    ("Javagal Srinat", "India", 1996, "BOWL", 10.0, 48.0, 28.0, 4.5, 45.0, 0.6),
    ("Harbajan Singhh", "India", 2001, "BOWL", 12.0, 60.0, 32.0, 3.4, 70.0, 0.62),
    ("Zaheer Khaan", "India", 2011, "BOWL", 11.0, 55.0, 30.0, 4.9, 33.0, 0.66),
    ("Rohit Sharmaa", "India", 2019, "BAT", 48.0, 91.0, None, None, None, 0.8),
    ("Shikar Dhawann", "India", 2015, "BAT", 44.0, 94.0, None, None, None, 0.6),
    ("Ravindra Jadeja", "India", 2021, "AR", 32.0, 85.0, 30.0, 4.9, 40.0, 0.7),
    ("Jasprit Bumrah", "India", 2020, "BOWL", 6.0, 40.0, 20.0, 4.2, 30.0, 0.85),
    ("KL Rahull", "India", 2018, "WK", 46.0, 90.0, None, None, None, 0.62),
    ("Hardik Pandia", "India", 2022, "AR", 34.0, 105.0, 32.0, 5.5, 34.0, 0.55),

    # ---------------- AUSTRALIA ----------------
    ("Don Bradmann", "Australia", 1948, "BAT", 99.9, 60.0, None, None, None, 0.95),
    ("Ricky Pontin", "Australia", 2003, "BAT", 54.0, 85.0, None, None, None, 0.85),
    ("Steven Waughe", "Australia", 1999, "BAT", 51.0, 68.0, 37.0, 3.8, 65.0, 0.8),
    ("Marcus Waughe", "Australia", 1998, "AR", 41.0, 75.0, 41.0, 4.4, 55.0, 0.63),
    ("Adam Gilchrest", "Australia", 2003, "WK", 47.0, 96.0, None, None, None, 0.8),
    ("Shane Warnie", "Australia", 1996, "BOWL", 13.0, 60.0, 25.0, 2.6, 57.0, 0.87),
    ("Glenn McGrah", "Australia", 2001, "BOWL", 7.0, 42.0, 21.0, 2.5, 51.0, 0.86),
    ("Dennis Lilee", "Australia", 1981, "BOWL", 11.0, 55.0, 23.0, 3.0, 52.0, 0.7),
    ("Allan Bordor", "Australia", 1989, "BAT", 50.0, 65.0, None, None, None, 0.7),
    ("Michael Clarkson", "Australia", 2013, "BAT", 49.0, 78.0, None, None, None, 0.72),
    ("David Warnor", "Australia", 2017, "BAT", 48.0, 96.0, None, None, None, 0.65),
    ("Mitchell Starcy", "Australia", 2019, "BOWL", 9.0, 50.0, 22.0, 4.9, 27.0, 0.68),
    ("Patrick Cumminz", "Australia", 2021, "BOWL", 15.0, 58.0, 22.0, 2.9, 55.0, 0.75),
    ("Jeff Thomsen", "Australia", 1976, "BOWL", 9.0, 45.0, 24.0, 3.2, 50.0, 0.6),

    # ---------------- WEST INDIES ----------------
    ("Vivian Richardsson", "West Indies", 1980, "BAT", 61.0, 90.0, None, None, None, 0.88),
    ("Brian Lahra", "West Indies", 1994, "BAT", 58.0, 79.0, None, None, None, 0.83),
    ("Garfield Sobbers", "West Indies", 1966, "AR", 57.0, 70.0, 34.0, 3.0, 68.0, 0.82),
    ("Gordon Greenwich", "West Indies", 1984, "BAT", 44.0, 66.0, None, None, None, 0.65),
    ("Malcolm Marshal", "West Indies", 1985, "BOWL", 18.0, 55.0, 20.0, 2.7, 46.0, 0.8),
    ("Curtley Ambrosse", "West Indies", 1993, "BOWL", 8.0, 42.0, 21.0, 2.4, 55.0, 0.75),
    ("Courtnay Walshe", "West Indies", 1995, "BOWL", 7.0, 40.0, 24.0, 2.9, 52.0, 0.66),
    ("Andy Robarts", "West Indies", 1978, "BOWL", 10.0, 48.0, 25.0, 3.1, 50.0, 0.6),
    ("Chris Gale", "West Indies", 2015, "BAT", 40.0, 92.0, None, None, None, 0.55),
    ("Shivnarine Chandrapaul", "West Indies", 2008, "BAT", 51.0, 60.0, None, None, None, 0.7),

    # ---------------- ENGLAND ----------------
    ("Ian Bothum", "England", 1981, "AR", 33.0, 75.0, 28.0, 3.2, 55.0, 0.72),
    ("Graham Gooche", "England", 1990, "BAT", 42.0, 65.0, None, None, None, 0.6),
    ("Kevin Peterson", "England", 2010, "BAT", 47.0, 86.0, None, None, None, 0.68),
    ("Andrew Flintoft", "England", 2005, "AR", 32.0, 79.0, 32.0, 4.7, 45.0, 0.6),
    ("James Andersen", "England", 2016, "BOWL", 9.0, 45.0, 26.0, 2.8, 55.0, 0.78),
    ("Stuart Broade", "England", 2015, "BOWL", 10.0, 48.0, 28.0, 3.0, 56.0, 0.7),
    ("Joe Root", "England", 2021, "BAT", 50.0, 74.0, None, None, None, 0.75),
    ("Ben Stoke", "England", 2019, "AR", 40.0, 95.0, 32.0, 5.0, 40.0, 0.62),
    ("Alastair Cookie", "England", 2011, "BAT", 47.0, 55.0, None, None, None, 0.6),
    ("Jos Buttlerr", "England", 2022, "WK", 41.0, 121.0, None, None, None, 0.55),

    # ---------------- PAKISTAN ----------------
    ("Imraan Khan", "Pakistan", 1987, "AR", 37.0, 68.0, 22.0, 3.0, 55.0, 0.78),
    ("Waseem Akrem", "Pakistan", 1992, "BOWL", 22.0, 65.0, 23.0, 3.9, 40.0, 0.8),
    ("Waqar Younus", "Pakistan", 1994, "BOWL", 11.0, 50.0, 23.0, 4.7, 30.0, 0.74),
    ("Javed Miandaad", "Pakistan", 1986, "BAT", 52.0, 67.0, None, None, None, 0.72),
    ("Inzamam ul Haque", "Pakistan", 1999, "BAT", 49.0, 74.0, None, None, None, 0.6),
    ("Shahid Afreedi", "Pakistan", 2007, "AR", 23.0, 117.0, 34.0, 4.6, 35.0, 0.5),
    ("Babur Azam", "Pakistan", 2021, "BAT", 56.0, 88.0, None, None, None, 0.8),
    ("Shaheen Afridee", "Pakistan", 2022, "BOWL", 8.0, 44.0, 24.0, 4.6, 32.0, 0.68),

    # ---------------- SOUTH AFRICA ----------------
    ("Jacques Kallistad", "South Africa", 2005, "AR", 55.0, 72.0, 32.0, 3.1, 60.0, 0.8),
    ("AB de Villierz", "South Africa", 2015, "BAT", 53.0, 101.0, None, None, None, 0.78),
    ("Hashim Amlaa", "South Africa", 2012, "BAT", 54.0, 89.0, None, None, None, 0.75),
    ("Dale Steyne", "South Africa", 2013, "BOWL", 10.0, 45.0, 22.0, 2.9, 42.0, 0.83),
    ("Allan Donaldd", "South Africa", 1998, "BOWL", 9.0, 44.0, 22.0, 3.4, 40.0, 0.72),
    ("Faf du Plessy", "South Africa", 2016, "BAT", 45.0, 88.0, None, None, None, 0.65),
    ("Quinton de Kok", "South Africa", 2019, "WK", 45.0, 95.0, None, None, None, 0.66),

    # ---------------- SRI LANKA ----------------
    ("Muttiah Muralidaran", "Sri Lanka", 2000, "BOWL", 12.0, 62.0, 22.0, 3.9, 55.0, 0.85),
    ("Sanath Jayasuryah", "Sri Lanka", 1996, "BAT", 33.0, 91.0, 36.0, 4.6, 45.0, 0.6),
    ("Kumar Sangakarra", "Sri Lanka", 2014, "WK", 57.0, 78.0, None, None, None, 0.8),
    ("Mahela Jayawardana", "Sri Lanka", 2006, "BAT", 51.0, 80.0, None, None, None, 0.74),
    ("Lasith Malingaa", "Sri Lanka", 2011, "BOWL", 13.0, 55.0, 20.0, 4.9, 25.0, 0.66),
    ("Arjuna Ranatungga", "Sri Lanka", 1996, "AR", 35.0, 78.0, 40.0, 4.9, 60.0, 0.55),

    # ---------------- NEW ZEALAND ----------------
    ("Richard Hadlee-son", "New Zealand", 1985, "AR", 27.0, 60.0, 22.0, 2.6, 51.0, 0.75),
    ("Martin Crowee", "New Zealand", 1991, "BAT", 45.0, 70.0, None, None, None, 0.68),
    ("Brendon McCullam", "New Zealand", 2014, "WK", 38.0, 96.0, None, None, None, 0.6),
    ("Kane Williamsen", "New Zealand", 2019, "BAT", 54.0, 82.0, None, None, None, 0.82),
    ("Trent Boultt", "New Zealand", 2019, "BOWL", 12.0, 50.0, 24.0, 4.6, 30.0, 0.7),
    ("Daniel Vettory", "New Zealand", 2007, "BOWL", 16.0, 65.0, 34.0, 3.7, 55.0, 0.6),
    ("Ross Taylorr", "New Zealand", 2015, "BAT", 47.0, 80.0, None, None, None, 0.65),
]

RAW = [r for r in RAW if r != "MSDONI_PLACEHOLDER"]

ROLE_BUDGET = {"BAT": (100, 60), "WK": (100, 60), "BOWL": (0, 0), "AR": (0, 0)}


def rating_for(role, bat_avg, bat_sr, bowl_avg, bowl_econ, bowl_sr, consistency):
    bat_score = 0.0
    if bat_avg:
        bat_score = min(bat_avg, 65) * 0.9 + min(bat_sr or 0, 130) * 0.25
    bowl_score = 0.0
    if bowl_avg:
        # lower average/economy is better -> invert
        bowl_score = max(0, 45 - bowl_avg) * 1.6 + max(0, 6.5 - bowl_econ) * 9 + max(0, 70 - bowl_sr) * 0.3
    if role == "BAT" or role == "WK":
        base = bat_score
    elif role == "BOWL":
        base = bowl_score
    else:  # AR
        base = bat_score * 0.6 + bowl_score * 0.6
    return round(base * (0.75 + 0.25 * consistency), 1)


def credits_for(rating):
    # map rating roughly (0-140) onto a 6.0 - 11.0 credit scale
    c = 6.0 + (min(rating, 130) / 130.0) * 5.0
    return round(c * 2) / 2  # nearest 0.5


players = []
pid = 1
for (name, country, era, role, bat_avg, bat_sr, bowl_avg, bowl_econ, bowl_sr, consistency) in RAW:
    rating = rating_for(role, bat_avg, bat_sr, bowl_avg, bowl_econ, bowl_sr, consistency)
    credit = credits_for(rating)
    players.append({
        "id": pid,
        "name": name,
        "country": country,
        "era": era,
        "role": role,
        "batting": {"avg": bat_avg, "sr": bat_sr} if bat_avg is not None else None,
        "bowling": {"avg": bowl_avg, "econ": bowl_econ, "sr": bowl_sr} if bowl_avg is not None else None,
        "rating": rating,
        "credit": credit,
        "consistency": consistency,
    })
    pid += 1

out_path = os.path.join(os.path.dirname(__file__), "players.json")
with open(out_path, "w") as f:
    json.dump(players, f, indent=2)

print(f"wrote {len(players)} players to {out_path}")
