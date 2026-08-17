"""Apply sql/001_agent_memory.sql to live CockroachDB. Requires CRDB_DSN."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "sql" / "001_agent_memory.sql"


def main() -> int:
    dsn = os.environ.get("CRDB_DSN") or os.environ.get("DATABASE_URL")
    if not dsn:
        print("FAIL: set CRDB_DSN to your CockroachDB Cloud connection string")
        print('  $env:CRDB_DSN = "postgresql://user:pass@host:26257/defaultdb?sslmode=verify-full"')
        return 1
    try:
        import psycopg
    except ImportError:
        print("FAIL: pip install 'psycopg[binary]>=3.1.0'")
        return 1

    sql = SQL.read_text(encoding="utf-8")
    print(f"Connecting (host redacted)…")
    # never print full DSN (may contain password)
    try:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
        print("OK: schema applied from sql/001_agent_memory.sql")
        print("Next: python scripts/02_run_live_demo.py")
        return 0
    except Exception as e:
        print(f"FAIL: {e}")
        print("Check: cluster running, user/password, network allowlist, sslmode")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
