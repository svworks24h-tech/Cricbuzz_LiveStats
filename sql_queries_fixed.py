from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Support both the original folder structure and the current GitHub root layout.
SQL_FILE = BASE_DIR / "sql" / "queries.sql"
if not SQL_FILE.exists():
    SQL_FILE = BASE_DIR / "queries.sql"


def load_queries() -> dict[int, str]:
    text = SQL_FILE.read_text(encoding="utf-8")
    chunks = text.split("-- Q")[1:]
    queries = {}
    for chunk in chunks:
        lines = chunk.splitlines()
        qnum = int(lines[0].strip())
        body = []
        for line in lines[1:]:
            if line.startswith("-- Q"):
                break
            body.append(line)
        queries[qnum] = "\n".join(body).strip().rstrip(";")
    return queries


QUERY_TITLES = {
    1: "Indian players",
    2: "Matches in last 30 days",
    3: "Top 10 ODI run scorers",
    4: "Large-capacity venues",
    5: "Team wins",
    6: "Players by role",
    7: "Highest score by format",
    8: "Series started in 2024",
    9: "All-rounders: 1000+ runs and 50+ wickets",
    10: "Last 20 completed matches",
    11: "Cross-format batting comparison",
    12: "Home vs away performance",
    13: "100+ batting partnerships",
    14: "Venue bowling economy",
    15: "Close-match performers",
    16: "Yearly batting trend since 2020",
    17: "Toss advantage",
    18: "Most economical limited-overs bowlers",
    19: "Most consistent batsmen",
    20: "Format match counts and averages",
    21: "Weighted player performance ranking",
    22: "Head-to-head analysis",
    23: "Recent player form",
    24: "Successful batting partnerships",
    25: "Quarterly career trajectory",
}
