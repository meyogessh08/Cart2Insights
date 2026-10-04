import os
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, bindparam

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def get_engine():
    password = quote_plus(os.getenv("DB_PASSWORD", ""))
    url = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{password}"
        f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}"
        f"/{os.getenv('DB_NAME')}"
    )
    return create_engine(url, pool_pre_ping=True)


def run_query(sql: str, params: dict | None = None) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql(sql, conn, params=params)


def run_query_filtered(sql: str, params: dict, list_params: list[str] = None) -> pd.DataFrame:
    """Like run_query, but supports IN (:param) clauses bound to Python lists."""
    stmt = text(sql)
    if list_params:
        stmt = stmt.bindparams(*[bindparam(p, expanding=True) for p in list_params])
    with get_engine().connect() as conn:
        return pd.read_sql(stmt, conn, params=params)