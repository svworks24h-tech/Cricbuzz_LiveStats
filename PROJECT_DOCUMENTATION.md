# Project Documentation

## Architecture

`Cricbuzz REST API -> requests -> Python normalization -> Streamlit`

`Python/seed data -> SQLite -> SQL analytics -> Streamlit tables/charts`

## Folder Structure

```text
Cricbuzz_LiveStats/
├── main.py
├── app.py
├── config.py
├── db.py
├── api_client.py
├── sql_queries.py
├── requirements.txt
├── .env.example
├── README.md
├── cricbuzz.db
├── database/
│   ├── schema.sql
│   └── seed_data.py
├── sql/
│   └── queries.sql
├── docs/
│   └── PROJECT_DOCUMENTATION.md
└── tests/
    └── test_smoke.py
```

## Data Flow

1. API credentials are read from `.env`.
2. `api_client.py` calls the REST API.
3. Live JSON is flattened for the Live Matches page.
4. Historical/demo records are stored in SQLite.
5. `db.py` centralizes connections and registers `STDDEV_POP` for analytical SQL.
6. Streamlit executes the 25 assignment queries and renders tables/charts.
7. CRUD forms write through parameterized SQL statements.

## Quality Controls

- Foreign keys enabled.
- Primary and unique keys defined.
- CHECK constraints on role, format, status-related values and non-negative metrics.
- Indexes on common filter/join columns.
- Parameterized CRUD statements.
- API timeout and exception handling.
- Environment-variable API credentials.
