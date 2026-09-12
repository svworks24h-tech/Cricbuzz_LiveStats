# Cricbuzz LiveStats

**Real-Time Cricket Insights & SQL-Based Analytics**

A complete Streamlit cricket analytics dashboard built around a normalized SQLite database, 25 SQL analytics questions, CRUD operations, pandas, requests and optional Cricbuzz-compatible RapidAPI integration.

## Run

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
streamlit run main.py
```

The bundled `cricbuzz.db` already contains demo data. To rebuild it:

```bash
python database/seed_data.py
```

## Live API

Copy `.env.example` to `.env` and add a RapidAPI key for the Cricbuzz-compatible API:

```text
RAPIDAPI_KEY=your_key
```

The dashboard uses live API data when configured and automatically falls back to the bundled SQL database when the API is unavailable.

## Pages

1. Home
2. Live Matches
3. Top Player Stats
4. SQL Analytics — Q1 to Q25
5. CRUD Operations

## Database

The normalized schema includes:

- teams
- players
- venues
- series
- matches
- innings
- batting_performances
- bowling_performances
- fielding_performances
- partnerships

Indexes are included for dates, formats, teams, venues, players and performance foreign keys.

## Security

API credentials are read from environment variables and are not stored in source code.

## Assignment Coverage

The implementation covers the required live match view, top player statistics, 25 SQL analytics queries, CRUD operations, database schema/sample data, API configuration, requirements and error handling.
