from __future__ import annotations

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "cricbuzz.db"
SCHEMA = ROOT / "database" / "schema.sql"

random.seed(42)

TEAMS = [
    (1, "India", "India", "IND"), (2, "Australia", "Australia", "AUS"),
    (3, "England", "England", "ENG"), (4, "Pakistan", "Pakistan", "PAK"),
    (5, "New Zealand", "New Zealand", "NZ"), (6, "South Africa", "South Africa", "SA"),
    (7, "Sri Lanka", "Sri Lanka", "SL"), (8, "Bangladesh", "Bangladesh", "BAN"),
]

PLAYERS = [
    (1,"Arjun Sharma","India","Batsman","Right-hand","Right-arm medium"),
    (2,"Rohan Mehta","India","Batsman","Left-hand","Right-arm off break"),
    (3,"Vikram Rao","India","All-rounder","Right-hand","Right-arm medium"),
    (4,"Kabir Singh","India","Wicket-keeper","Right-hand","Right-arm medium"),
    (5,"Dev Patel","India","Bowler","Right-hand","Right-arm fast"),
    (6,"Aman Verma","India","Bowler","Left-hand","Left-arm orthodox"),
    (7,"Liam Carter","Australia","Batsman","Right-hand","Right-arm medium"),
    (8,"Noah Williams","Australia","All-rounder","Left-hand","Right-arm fast"),
    (9,"Ethan Brooks","Australia","Bowler","Right-hand","Right-arm fast"),
    (10,"Oliver Grant","Australia","Wicket-keeper","Right-hand","Right-arm medium"),
    (11,"Harry Wilson","England","Batsman","Right-hand","Right-arm off break"),
    (12,"Jack Turner","England","All-rounder","Right-hand","Right-arm medium"),
    (13,"George Hall","England","Bowler","Left-hand","Left-arm fast"),
    (14,"Ben Foster","England","Wicket-keeper","Left-hand","Right-arm medium"),
    (15,"Babar Khan","Pakistan","Batsman","Right-hand","Right-arm medium"),
    (16,"Hassan Ali","Pakistan","All-rounder","Right-hand","Right-arm fast"),
    (17,"Shadab Malik","Pakistan","Bowler","Right-hand","Right-arm leg break"),
    (18,"Mohammad Rizvi","Pakistan","Wicket-keeper","Right-hand","Right-arm medium"),
    (19,"Tom Mitchell","New Zealand","Batsman","Left-hand","Right-arm medium"),
    (20,"James Wilson","New Zealand","All-rounder","Right-hand","Right-arm medium"),
    (21,"Luke Adams","New Zealand","Bowler","Right-hand","Right-arm fast"),
    (22,"Ryan Clarke","South Africa","Batsman","Right-hand","Right-arm medium"),
    (23,"David Mokoena","South Africa","All-rounder","Right-hand","Right-arm fast"),
    (24,"Kagiso Naidoo","South Africa","Bowler","Right-hand","Right-arm fast"),
    (25,"Dinesh Perera","Sri Lanka","Batsman","Left-hand","Right-arm off break"),
    (26,"Nuwan Silva","Sri Lanka","All-rounder","Right-hand","Right-arm medium"),
    (27,"Mushfiq Rahman","Bangladesh","Wicket-keeper","Right-hand","Right-arm medium"),
    (28,"Sakib Hossain","Bangladesh","All-rounder","Left-hand","Left-arm orthodox"),
]

VENUES = [
    (1,"Wankhede Stadium","Mumbai","India",33000),
    (2,"M. Chinnaswamy Stadium","Bengaluru","India",40000),
    (3,"Narendra Modi Stadium","Ahmedabad","India",132000),
    (4,"Melbourne Cricket Ground","Melbourne","Australia",100024),
    (5,"Sydney Cricket Ground","Sydney","Australia",48000),
    (6,"Lord's","London","England",31800),
    (7,"The Oval","London","England",27700),
    (8,"Gaddafi Stadium","Lahore","Pakistan",27000),
    (9,"Eden Park","Auckland","New Zealand",50000),
    (10,"Newlands Cricket Ground","Cape Town","South Africa",25000),
]

VENUE_BY_COUNTRY = {
    "India": [1,2,3], "Australia": [4,5], "England": [6,7], "Pakistan": [8],
    "New Zealand": [9], "South Africa": [10], "Sri Lanka": [1], "Bangladesh": [2]
}

TEAM_PLAYERS = {}
for p in PLAYERS:
    TEAM_PLAYERS.setdefault(p[2], []).append(p[0])

FORMATS = ["Test", "ODI", "T20I"]


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA.read_text(encoding="utf-8"))
    cur = con.cursor()
    cur.executemany("INSERT INTO teams VALUES (?,?,?,?)", TEAMS)
    cur.executemany("INSERT INTO players VALUES (?,?,?,?,?,?)", PLAYERS)
    cur.executemany("INSERT INTO venues VALUES (?,?,?,?,?)", VENUES)

    series_rows = []
    for sid in range(1, 13):
        host = TEAMS[(sid - 1) % len(TEAMS)][2]
        fmt = FORMATS[(sid - 1) % 3]
        start = date(2024 + (sid - 1) // 4, ((sid - 1) % 4) * 3 + 1, 10)
        series_rows.append((sid, f"{host} International Series {start.year}", host, fmt, start.isoformat(), 8))
    cur.executemany("INSERT INTO series VALUES (?,?,?,?,?,?)", series_rows)

    match_id = innings_id = batting_id = bowling_id = fielding_id = partnership_id = 1
    start_date = date(2023, 1, 1)
    team_pairs = [(1,2),(1,3),(1,4),(2,3),(2,5),(3,4),(4,5),(5,6),(6,7),(7,8),(1,6),(2,7)]

    for m in range(192):
        d = start_date + timedelta(days=m * 7)
        t1, t2 = team_pairs[m % len(team_pairs)]
        fmt = FORMATS[m % 3]
        sid = (m % 12) + 1
        home_country = TEAMS[t1-1][2]
        venue_id = random.choice(VENUE_BY_COUNTRY[home_country])
        toss_winner = random.choice([t1,t2])
        toss_decision = random.choice(["bat","bowl"])
        winner = random.choice([t1,t2])
        win_type = random.choice(["runs","wickets"])
        margin = random.randint(5, 180) if win_type == "runs" else random.randint(1, 9)
        match_date = d.isoformat()
        cur.execute(
            "INSERT INTO matches VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (match_id,sid,match_date,f"{fmt} Match {m+1}",fmt,venue_id,t1,t2,toss_winner,toss_decision,winner,margin,win_type,"completed")
        )

        team1_players = TEAM_PLAYERS[TEAMS[t1-1][2]]
        team2_players = TEAM_PLAYERS[TEAMS[t2-1][2]]
        selected1 = random.sample(team1_players, min(7, len(team1_players)))
        selected2 = random.sample(team2_players, min(7, len(team2_players)))
        for inn_no, (bat_team, bowl_team, players) in enumerate([(t1,t2,selected1),(t2,t1,selected2)], start=1):
            cur.execute("INSERT INTO innings VALUES (?,?,?,?,?)", (innings_id,match_id,inn_no,bat_team,bowl_team))
            positions = list(range(1, len(players)+1))
            for pos, pid in zip(positions, players):
                role = next(p[3] for p in PLAYERS if p[0] == pid)
                base = 35 if role in ("Batsman","Wicket-keeper") else 24
                runs = max(0, int(random.gauss(base, 20)))
                if random.random() < 0.06:
                    runs += random.randint(55, 90)
                balls = max(1, int(runs / random.uniform(0.65, 1.35)))
                fours = min(runs // 4, random.randint(0, 8))
                sixes = min((runs - fours*4) // 6, random.randint(0, 5))
                cur.execute("INSERT INTO batting_performances VALUES (?,?,?,?,?,?,?,?,?)", (batting_id,innings_id,pid,pos,runs,balls,fours,sixes,random.choice([0,1])))
                batting_id += 1
                if pos <= 4:
                    cur.execute("INSERT INTO fielding_performances VALUES (?,?,?,?,?)", (fielding_id,innings_id,pid,random.randint(0,2),random.randint(0,1) if role == "Wicket-keeper" else 0))
                    fielding_id += 1
            bowlers = random.sample(TEAM_PLAYERS[TEAMS[bowl_team-1][2]], min(4, len(TEAM_PLAYERS[TEAMS[bowl_team-1][2]])))
            for pid in bowlers:
                overs = round(random.uniform(2.0, 8.0), 1)
                wickets = random.randint(0, 4)
                conceded = int(overs * random.uniform(4.0, 8.5))
                cur.execute("INSERT INTO bowling_performances VALUES (?,?,?,?,?,?,?,?,?)", (bowling_id,innings_id,pid,overs,conceded,wickets,random.randint(0,1),0,random.randint(0,2)))
                bowling_id += 1
            for a, b in zip(players[:-1], players[1:]):
                pa = cur.execute("SELECT batting_position, runs FROM batting_performances WHERE innings_id=? AND player_id=?", (innings_id,a)).fetchone()
                pb = cur.execute("SELECT batting_position, runs FROM batting_performances WHERE innings_id=? AND player_id=?", (innings_id,b)).fetchone()
                if pa and pb:
                    runs = pa[1] + pb[1]
                    cur.execute("INSERT INTO partnerships VALUES (?,?,?,?,?,?,?,?)", (partnership_id,innings_id,a,b,pa[0],pb[0],runs,random.randint(20,100)))
                    partnership_id += 1
            innings_id += 1
        match_id += 1

    con.commit()
    con.close()
    print(DB_PATH)


if __name__ == "__main__":
    main()
