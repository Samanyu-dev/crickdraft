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
    ("Netherlands", 1974, "Total Football Finalists", [
        ("Jan Jongbloedd", "GK", "B"), ("Ruud Krohl", "DEF", "A"), ("Wim Suurbiere", "DEF", "B"),
        ("Wim Rijsbergenn", "DEF", "B"), ("Arie Haan", "DEF", "B"), ("Johan Neeskenss", "MID", "S"),
        ("Wim van Hanegemm", "MID", "A"), ("Johnny Repp", "MID", "A"), ("Rene van de Kerkhoff", "MID", "B"),
        ("Johann Cruyffe", "FWD", "S"), ("Rob Rensenbrinck", "FWD", "A"), ("Piet Keizerr", "FWD", "B"),
    ]),
    ("Uruguay", 1950, "Maracanazo Champions", [
        ("Roque Maspolii", "GK", "B"), ("Schubert Gambettaa", "DEF", "B"), ("Obduulio Varelaa", "DEF", "A"),
        ("Matias Gonzalezz", "DEF", "C"), ("William Martinezz", "DEF", "C"), ("Rodriguez Andradee", "MID", "B"),
        ("Julio Perezz", "MID", "B"), ("Victor Rodriguezz", "MID", "B"), ("Juan Schiaffinoo", "MID", "S"),
        ("Alcides Ghiggiaa", "FWD", "A"), ("Oscar Miguezz", "FWD", "A"), ("Julio Abbadiee", "FWD", "B"),
    ]),
    ("Portugal", 2016, "Euro 2016 Champions", [
        ("Rui Patriciooh", "GK", "B"), ("Pepee", "DEF", "A"), ("Jose Fontee", "DEF", "B"),
        ("Cedric Soaress", "DEF", "B"), ("Raphael Guerreiroo", "DEF", "B"), ("William Carvalhoo", "MID", "B"),
        ("Adrien Silvaa", "MID", "B"), ("Joao Marioo", "MID", "B"), ("Renato Sanchess", "MID", "A"),
        ("Cristiano Ronaldoo", "FWD", "S"), ("Nanii", "FWD", "A"), ("Ederr", "FWD", "B"),
    ]),
    ("Croatia", 2018, "2018 World Cup Finalists", [
        ("Danijel Subasicc", "GK", "B"), ("Dejan Lovrenn", "DEF", "B"), ("Domagoj Vidaa", "DEF", "B"),
        ("Sime Vrsaljkoo", "DEF", "B"), ("Ivan Strinicc", "DEF", "C"), ("Luka Modricc", "MID", "S"),
        ("Ivan Rakiticc", "MID", "A"), ("Marcelo Brozovicc", "MID", "A"), ("Ante Rebicc", "MID", "B"),
        ("Mario Mandzukicc", "FWD", "A"), ("Ivan Perisicc", "FWD", "A"), ("Andrej Kramaricc", "FWD", "B"),
    ]),
    ("Belgium", 2018, "Golden Generation", [
        ("Thibaut Courtoiss", "GK", "S"), ("Toby Alderweireldd", "DEF", "A"), ("Jan Vertonghenn", "DEF", "A"),
        ("Vincent Kompanyy", "DEF", "A"), ("Thomas Meunierr", "DEF", "B"), ("Kevin De Bruynee", "MID", "S"),
        ("Axel Witsell", "MID", "A"), ("Marouane Fellainii", "MID", "B"), ("Dries Mertenss", "MID", "A"),
        ("Eden Hazardd", "FWD", "S"), ("Romelu Lukakuu", "FWD", "S"), ("Yannick Carrascoo", "FWD", "B"),
    ]),
    ("Brazil", 2002, "2002 World Cup Winners", [
        ("Marcoss", "GK", "A"), ("Cafuu", "DEF", "S"), ("Luciio", "DEF", "A"),
        ("Roque Juniorr", "DEF", "B"), ("Roberto Carloss", "DEF", "S"), ("Gilberto Silvaa", "MID", "A"),
        ("Kleberssonn", "MID", "B"), ("Ronaldinhoo", "MID", "S"), ("Edmilsonn", "MID", "B"),
        ("Rivaldoo", "FWD", "S"), ("Ronaldoo", "FWD", "S"), ("Denilsonn", "FWD", "B"),
    ]),
    ("Italy", 1982, "1982 World Cup Winners", [
        ("Dino Zoffe", "GK", "S"), ("Claudio Gentilee", "DEF", "A"), ("Gaetano Screaa", "DEF", "A"),
        ("Antonio Cabrinii", "DEF", "B"), ("Fulvio Collovatii", "DEF", "B"), ("Marco Tardellii", "MID", "A"),
        ("Bruno Contii", "MID", "A"), ("Giancarlo Antognonii", "MID", "A"), ("Franco Baresii", "MID", "B"),
        ("Paolo Rossee", "FWD", "S"), ("Francesco Grazianii", "FWD", "B"), ("Alessandro Altobellii", "FWD", "A"),
    ]),
    ("France", 2018, "2018 World Cup Winners", [
        ("Hugo Llorris", "GK", "A"), ("Raphael Varanee", "DEF", "S"), ("Samuel Umtitii", "DEF", "B"),
        ("Benjamin Pavardd", "DEF", "B"), ("Lucas Hernandezz", "DEF", "B"), ("Paul Pogbaa", "MID", "A"),
        ("N'Golo Kantee", "MID", "S"), ("Blaise Matuidii", "MID", "B"), ("Corentin Tolissoo", "MID", "B"),
        ("Antoine Griezmannn", "FWD", "S"), ("Kylian Mbappee", "FWD", "S"), ("Olivier Giroudd", "FWD", "A"),
    ]),
    ("Germany", 1990, "1990 World Cup Winners", [
        ("Bodo Illgnerr", "GK", "B"), ("Andreas Brehmee", "DEF", "A"), ("Jurgen Kohlerr", "DEF", "A"),
        ("Guido Buchwaldd", "DEF", "B"), ("Klaus Augenthalerr", "DEF", "B"), ("Lothar Matthausz", "MID", "S"),
        ("Thomas Hasslerr", "MID", "A"), ("Pierre Littbarskii", "MID", "B"), ("Olaf Thonn", "MID", "B"),
        ("Rudi Vollerr", "FWD", "S"), ("Jurgen Klinsmannn", "FWD", "S"), ("Karl Heinz Riedlee", "FWD", "B"),
    ]),
    ("England", 2022, "Modern Era", [
        ("Jordan Pickfordd", "GK", "A"), ("Kyle Walkerr", "DEF", "A"), ("John Stoness", "DEF", "A"),
        ("Harry Maguiree", "DEF", "B"), ("Luke Shaww", "DEF", "B"), ("Declan Ricee", "MID", "A"),
        ("Jude Bellinghamm", "MID", "S"), ("Phil Fodenn", "MID", "A"), ("Mason Mountt", "MID", "B"),
        ("Harry Kanee", "FWD", "S"), ("Bukayo Sakaa", "FWD", "A"), ("Raheem Sterlingg", "FWD", "A"),
    ]),
    ("Netherlands", 1988, "Euro 1988 Champions", [
        ("Hans van Breukelenn", "GK", "A"), ("Berry van Aerlee", "DEF", "B"), ("Ronald Koemann", "DEF", "A"),
        ("Adri van Tiggelenn", "DEF", "B"), ("Erwin Koemann", "DEF", "B"), ("Jan Wouterss", "MID", "B"),
        ("Arnold Muhrenn", "MID", "A"), ("Gerald Vanenburgg", "MID", "B"), ("Frank Rijkaardd", "MID", "A"),
        ("Ruud Gullitt", "FWD", "S"), ("Marco van Bastenn", "FWD", "S"), ("Wim Kieftt", "FWD", "B"),
    ]),
    ("Ghana", 2010, "2010 World Cup Quarterfinalists", [
        ("Richard Kingsonn", "GK", "B"), ("John Mensahh", "DEF", "A"), ("Jonathan Mensahh", "DEF", "B"),
        ("Hans Sarpeii", "DEF", "B"), ("John Pantsill", "DEF", "B"), ("Anthony Annann", "MID", "B"),
        ("Kwadwo Asamoahh", "MID", "A"), ("Sulley Muntarii", "MID", "A"), ("Andre Ayeww", "MID", "A"),
        ("Asamoah Gyann", "FWD", "A"), ("Kevin Prince Boatengg", "FWD", "B"), ("Matthew Amoahh", "FWD", "C"),
    ]),
    ("Netherlands", 2010, "2010 World Cup Finalists", [
        ("Maarten Stekelenburgg", "GK", "B"), ("Gregory van der Wiell", "DEF", "B"), ("John Heitingaa", "DEF", "B"),
        ("Joris Mathijsenn", "DEF", "B"), ("Giovanni van Bronckhorstt", "DEF", "A"), ("Mark van Bommell", "MID", "B"),
        ("Nigel de Jongg", "MID", "B"), ("Wesley Sneijderr", "MID", "S"), ("Rafael van der Vaartt", "MID", "A"),
        ("Arjen Robbenn", "FWD", "S"), ("Dirk Kuytt", "FWD", "A"), ("Robin van Persiee", "FWD", "S"),
    ]),
    ("England", 1990, "Italia 90 Semifinalists", [
        ("Peter Shiltonn", "GK", "A"), ("Gary Stevenss", "DEF", "B"), ("Des Walkerr", "DEF", "B"),
        ("Terry Butcherr", "DEF", "B"), ("Stuart Pearcee", "DEF", "B"), ("Paul Gascoignee", "MID", "S"),
        ("David Plattt", "MID", "A"), ("Chris Waddlee", "MID", "A"), ("Peter Beardsleyy", "MID", "A"),
        ("Gary Linekerr", "FWD", "S"), ("John Barness", "FWD", "A"), ("Steve Bulll", "FWD", "B"),
    ]),
    ("Hungary", 1954, "Mighty Magyars", [
        ("Gyula Grosicss", "GK", "A"), ("Jeno Buzanszkyy", "DEF", "B"), ("Gyula Lorantt", "DEF", "B"),
        ("Mihaly Lantoss", "DEF", "B"), ("Jozsef Bozsikk", "DEF", "B"), ("Jozsef Zakariass", "MID", "B"),
        ("Sandor Kocsiss", "MID", "S"), ("Nandor Hidegkutii", "MID", "A"), ("Zoltan Czriborr", "MID", "A"),
        ("Ferenc Puskass", "FWD", "S"), ("Jozsef Tothh", "FWD", "B"), ("Peter Palotass", "FWD", "B"),
    ]),
    ("Brazil", 1982, "Jogo Bonito Generation", [
        ("Waldir Peress", "GK", "B"), ("Leandroo", "DEF", "A"), ("Oscarr", "DEF", "B"),
        ("Luizinhoo", "DEF", "B"), ("Junior Netoo", "DEF", "A"), ("Toninho Cerezoo", "MID", "A"),
        ("Falcaoo", "MID", "S"), ("Socratess", "MID", "S"), ("Zicoo", "MID", "S"),
        ("Ederr", "FWD", "A"), ("Serginhoo", "FWD", "B"), ("Paulo Isidoroo", "FWD", "B"),
    ]),
    ("Netherlands", 1998, "Golden Generation", [
        ("Edwin van der Sarr", "GK", "A"), ("Michael Reizigerr", "DEF", "B"), ("Jaap Stamm", "DEF", "S"),
        ("Frank de Boerr", "DEF", "A"), ("Arthur Numann", "DEF", "B"), ("Edgar Davidss", "MID", "A"),
        ("Ronald de Boerr", "MID", "A"), ("Phillip Cocuu", "MID", "B"), ("Marc Overmarss", "MID", "A"),
        ("Dennis Bergkampp", "FWD", "S"), ("Patrick Kluivertt", "FWD", "S"), ("Boudewijn Zendenn", "FWD", "B"),
    ]),
    ("Colombia", 1994, "Golden Generation", [
        ("Oscar Cordobaa", "GK", "B"), ("Luis Herreraa", "DEF", "B"), ("Andres Escobarr", "DEF", "B"),
        ("Wilson Pereaa", "DEF", "B"), ("Alexis Mendozaa", "DEF", "C"), ("Carlos Valderramaa", "MID", "S"),
        ("Freddy Rincconn", "MID", "A"), ("Leonel Alvarezz", "MID", "B"), ("Barrabas Gomezz", "MID", "B"),
        ("Faustino Asprillaa", "FWD", "A"), ("Adolfo Valenciaa", "FWD", "A"), ("Antony de Avilaa", "FWD", "B"),
    ]),
    ("Nigeria", 1994, "World Cup Breakthrough", [
        ("Peter Rufaii", "GK", "B"), ("Augustine Eguavoenn", "DEF", "B"), ("Uche Okaforr", "DEF", "B"),
        ("Ben Iroshaa", "DEF", "C"), ("Mobi Oparakuu", "DEF", "C"), ("Jay Jay Okochaa", "MID", "S"),
        ("Sunday Olisehh", "MID", "A"), ("Emmanuel Amunikee", "MID", "B"), ("Michael Emenaloo", "MID", "B"),
        ("Rasheedi Yekinii", "FWD", "A"), ("Daniel Amokachii", "FWD", "A"), ("Finidi Georgee", "FWD", "A"),
    ]),
    ("South Korea", 2002, "2002 World Cup Semifinalists", [
        ("Lee Woon Jaee", "GK", "B"), ("Hong Myung Boo", "DEF", "A"), ("Choi Jin Cheull", "DEF", "B"),
        ("Kim Tae Youngg", "DEF", "B"), ("Lee Young Pyoo", "DEF", "B"), ("Yoo Sang Chull", "MID", "B"),
        ("Kim Nam Ill", "MID", "B"), ("Park Ji Sungg", "MID", "A"), ("Song Chong Gugg", "MID", "B"),
        ("Ahn Jung Hwann", "FWD", "A"), ("Seol Ki Hyeonn", "FWD", "B"), ("Choi Yong Soo", "FWD", "B"),
    ]),
]

# A handful of true legends get a deliberate overpowered-outlier boost past
# the normal 100-point cap.
LEGENDS = {"Peleh", "Diego Maradonna", "Lionel Messii", "Zinedine Zidanne", "Johann Cruyffe"}


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


def rating_for(role, attack, defense, passing, morale, name):
    if role == "GK":
        base = defense * 0.7 + passing * 0.3
    elif role == "DEF":
        base = defense * 0.6 + attack * 0.2 + passing * 0.2
    elif role == "MID":
        base = passing * 0.4 + attack * 0.3 + defense * 0.3
    else:
        base = attack * 0.6 + passing * 0.25 + 0.15 * (attack + defense) / 2
    raw = base * (0.8 + 0.2 * (morale / 100))
    # The raw formula naturally tops out well under 100 (weighted averages
    # of sub-100 components) - rescale so the best regular players approach
    # the 100-point cap, matching cricket's scale for a consistent "out of
    # 100" framing across both sports. Empirical raw range is ~24-85.
    rescaled = 20.0 + (raw - 24.0) / (85.0 - 24.0) * 78.0
    capped = min(max(rescaled, 0.0), 100.0)
    if name in LEGENDS:
        return round(min(max(capped, 92.0) * 1.15, 120.0), 1)
    return round(capped, 1)


def credits_for(rating):
    # Keep plenty of slack under the credit cap - a narrow spread (or an
    # average too close to CREDIT_CAP / SQUAD_SIZE) makes careless drafting
    # prone to unrecoverable budget dead-ends on the last pick.
    c = 5.0 + (min(rating, 120.0) / 120.0) * 7.5
    return round(c * 2) / 2


def rarity_for(rating):
    if rating > 100.0:
        return "Legend"
    if rating >= 85.0:
        return "Legendary"
    if rating >= 72.0:
        return "Epic"
    if rating >= 58.0:
        return "Rare"
    if rating >= 45.0:
        return "Uncommon"
    return "Common"


players = []
pid = 1
for country, era, squad_name, roster in SQUADS:
    for (name, role, tier) in roster:
        p = build_player(name, role, tier)
        rating = rating_for(role, p["attack"], p["defense"], p["passing"], p["morale"], name)
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
            "rarity": rarity_for(rating),
            "credit": credit,
        })
        pid += 1

out_path = os.path.join(os.path.dirname(__file__), "players.json")
with open(out_path, "w") as f:
    json.dump(players, f, indent=2)

print(f"wrote {len(players)} players across {len(SQUADS)} squads to {out_path}")
