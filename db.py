from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from config import DB_PATH, ROOT


class StdDevPop:
    def __init__(self) -> None:
        self.values: list[float] = []

    def step(self, value: Any) -> None:
        if value is not None:
            self.values.append(float(value))

    def finalize(self) -> float | None:
        if not self.values:
            return None
        mean = sum(self.values) / len(self.values)
        return (sum((x - mean) ** 2 for x in self.values) / len(self.values)) ** 0.5


def get_connection() -> sqlite3.Connection:
    path = Path(DB_PATH)
    if not path.exists():
        from database.seed_data import main as seed_main
        seed_main()
    con = sqlite3.connect(path, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.create_aggregate("STDDEV_POP", 1, StdDevPop)
    return con


def query_df(sql: str):
    import pandas as pd
    with get_connection() as con:
        return pd.read_sql_query(sql, con)


def execute(sql: str, params: tuple = ()) -> int:
    with get_connection() as con:
        cur = con.execute(sql, params)
        con.commit()
        return int(cur.lastrowid or 0)


def initialize() -> None:
    schema = (ROOT / "database" / "schema.sql").read_text(encoding="utf-8")
    with get_connection() as con:
        con.executescript(schema)
        con.commit()
