
import sqlite3
from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Database location
DB_DIR = BASE_DIR / "data" / "warehouse" / "database"
DB_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DB_DIR / "fintech360.db"


def get_connection():
    """Create a SQLite database connection."""

    return sqlite3.connect(DB_PATH)


def execute_sql_file(sql_file):
    """Execute SQL statements from a file."""

    sql_path = BASE_DIR / sql_file

    with get_connection() as conn:
        sql_script = sql_path.read_text(encoding="utf-8")
        conn.executescript(sql_script)

    print("SQL schema created successfully!")


if __name__ == "__main__":

    execute_sql_file(
        "sql/ddl/01_create_upi_transactions.sql"
    )

    print(f"Database location: {DB_PATH}")
