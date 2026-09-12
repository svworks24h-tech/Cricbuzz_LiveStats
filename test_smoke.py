from db import get_connection
from sql_queries import load_queries


def test_schema_has_core_tables():
    with get_connection() as con:
        names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {'teams','players','venues','series','matches','innings','batting_performances','bowling_performances','fielding_performances','partnerships'} <= names


def test_all_25_queries_load():
    queries = load_queries()
    assert len(queries) == 25
    assert set(queries) == set(range(1, 26))
