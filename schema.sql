PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS teams (
    team_id INTEGER PRIMARY KEY,
    team_name TEXT NOT NULL UNIQUE,
    country TEXT NOT NULL,
    short_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL UNIQUE,
    country TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Batsman','Bowler','All-rounder','Wicket-keeper')),
    batting_style TEXT,
    bowling_style TEXT
);

CREATE TABLE IF NOT EXISTS venues (
    venue_id INTEGER PRIMARY KEY,
    venue_name TEXT NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    capacity INTEGER
);

CREATE TABLE IF NOT EXISTS series (
    series_id INTEGER PRIMARY KEY,
    series_name TEXT NOT NULL,
    host_country TEXT NOT NULL,
    match_type TEXT NOT NULL,
    start_date TEXT NOT NULL,
    planned_matches INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS matches (
    match_id INTEGER PRIMARY KEY,
    series_id INTEGER NOT NULL REFERENCES series(series_id),
    match_date TEXT NOT NULL,
    description TEXT NOT NULL,
    format TEXT NOT NULL CHECK(format IN ('Test','ODI','T20I')),
    venue_id INTEGER NOT NULL REFERENCES venues(venue_id),
    team1_id INTEGER NOT NULL REFERENCES teams(team_id),
    team2_id INTEGER NOT NULL REFERENCES teams(team_id),
    toss_winner_id INTEGER REFERENCES teams(team_id),
    toss_decision TEXT CHECK(toss_decision IN ('bat','bowl')),
    winner_id INTEGER REFERENCES teams(team_id),
    win_margin INTEGER,
    win_type TEXT CHECK(win_type IN ('runs','wickets')),
    status TEXT NOT NULL DEFAULT 'completed'
);

CREATE TABLE IF NOT EXISTS innings (
    innings_id INTEGER PRIMARY KEY,
    match_id INTEGER NOT NULL REFERENCES matches(match_id) ON DELETE CASCADE,
    innings_no INTEGER NOT NULL,
    batting_team_id INTEGER NOT NULL REFERENCES teams(team_id),
    bowling_team_id INTEGER NOT NULL REFERENCES teams(team_id),
    UNIQUE(match_id, innings_no)
);

CREATE TABLE IF NOT EXISTS batting_performances (
    batting_id INTEGER PRIMARY KEY,
    innings_id INTEGER NOT NULL REFERENCES innings(innings_id) ON DELETE CASCADE,
    player_id INTEGER NOT NULL REFERENCES players(player_id),
    batting_position INTEGER NOT NULL,
    runs INTEGER NOT NULL DEFAULT 0 CHECK(runs >= 0),
    balls INTEGER NOT NULL DEFAULT 0 CHECK(balls >= 0),
    fours INTEGER NOT NULL DEFAULT 0 CHECK(fours >= 0),
    sixes INTEGER NOT NULL DEFAULT 0 CHECK(sixes >= 0),
    dismissed INTEGER NOT NULL DEFAULT 1 CHECK(dismissed IN (0,1)),
    UNIQUE(innings_id, player_id)
);

CREATE TABLE IF NOT EXISTS bowling_performances (
    bowling_id INTEGER PRIMARY KEY,
    innings_id INTEGER NOT NULL REFERENCES innings(innings_id) ON DELETE CASCADE,
    player_id INTEGER NOT NULL REFERENCES players(player_id),
    overs REAL NOT NULL DEFAULT 0 CHECK(overs >= 0),
    runs_conceded INTEGER NOT NULL DEFAULT 0 CHECK(runs_conceded >= 0),
    wickets INTEGER NOT NULL DEFAULT 0 CHECK(wickets >= 0),
    maidens INTEGER NOT NULL DEFAULT 0 CHECK(maidens >= 0),
    no_balls INTEGER NOT NULL DEFAULT 0 CHECK(no_balls >= 0),
    wides INTEGER NOT NULL DEFAULT 0 CHECK(wides >= 0),
    UNIQUE(innings_id, player_id)
);

CREATE TABLE IF NOT EXISTS fielding_performances (
    fielding_id INTEGER PRIMARY KEY,
    innings_id INTEGER NOT NULL REFERENCES innings(innings_id) ON DELETE CASCADE,
    player_id INTEGER NOT NULL REFERENCES players(player_id),
    catches INTEGER NOT NULL DEFAULT 0,
    stumpings INTEGER NOT NULL DEFAULT 0,
    UNIQUE(innings_id, player_id)
);

CREATE TABLE IF NOT EXISTS partnerships (
    partnership_id INTEGER PRIMARY KEY,
    innings_id INTEGER NOT NULL REFERENCES innings(innings_id) ON DELETE CASCADE,
    player1_id INTEGER NOT NULL REFERENCES players(player_id),
    player2_id INTEGER NOT NULL REFERENCES players(player_id),
    player1_position INTEGER NOT NULL,
    player2_position INTEGER NOT NULL,
    partnership_runs INTEGER NOT NULL DEFAULT 0,
    partnership_balls INTEGER NOT NULL DEFAULT 0,
    CHECK(player1_position + 1 = player2_position)
);

CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(match_date);
CREATE INDEX IF NOT EXISTS idx_matches_format ON matches(format);
CREATE INDEX IF NOT EXISTS idx_matches_teams ON matches(team1_id, team2_id);
CREATE INDEX IF NOT EXISTS idx_matches_venue ON matches(venue_id);
CREATE INDEX IF NOT EXISTS idx_batting_player ON batting_performances(player_id);
CREATE INDEX IF NOT EXISTS idx_batting_innings ON batting_performances(innings_id);
CREATE INDEX IF NOT EXISTS idx_batting_position ON batting_performances(innings_id, batting_position);
CREATE INDEX IF NOT EXISTS idx_bowling_player ON bowling_performances(player_id);
CREATE INDEX IF NOT EXISTS idx_bowling_innings ON bowling_performances(innings_id);
CREATE INDEX IF NOT EXISTS idx_fielding_player ON fielding_performances(player_id);
CREATE INDEX IF NOT EXISTS idx_partnerships_innings ON partnerships(innings_id);
