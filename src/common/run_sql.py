
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = (
    BASE_DIR
    / "data"
    / "warehouse"
    / "database"
    / "fintech360.db"
)

SQL_FILE = (
    BASE_DIR
    / "sql"
    / "transformations"
    / "02_validate_upi_data.sql"
)


def run_sql_file():

    print("=" * 60)
    print("FINTECH 360 - SQL VALIDATION")
    print("=" * 60)

    with sqlite3.connect(DB_PATH) as conn:

        sql_content = SQL_FILE.read_text(
            encoding="utf-8"
        )

        cursor = conn.cursor()

        # Execute each SQL statement separately
        statements = [
            statement.strip()
            for statement in sql_content.split(";")
            if statement.strip()
        ]

        for index, statement in enumerate(
            statements, start=1
        ):

            cursor.execute(statement)

            if cursor.description:

                columns = [
                    column[0]
                    for column in cursor.description
                ]

                rows = cursor.fetchall()

                print(f"\nQUERY {index} RESULTS")
                print("-" * 60)

                print(" | ".join(columns))

                for row in rows:
                    print(" | ".join(
                        str(value) for value in row
                    ))

    print("\nSQL VALIDATION COMPLETED!")


if __name__ == "__main__":
    run_sql_file()
