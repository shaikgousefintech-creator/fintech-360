
import sqlite3
from pathlib import Path


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

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


# --------------------------------------------------
# 2. READ AND PARSE SQL STATEMENTS
# --------------------------------------------------

def read_sql_statements():

    if not SQL_FILE.exists():
        raise FileNotFoundError(
            f"SQL file not found: {SQL_FILE}"
        )

    sql_content = SQL_FILE.read_text(
        encoding="utf-8"
    )

    statements = []
    current_statement = ""

    # Extract complete SQL statements safely
    for character in sql_content:

        current_statement += character

        if character == ";" and sqlite3.complete_statement(
            current_statement
        ):

            statement = current_statement.strip()

            if statement:
                statements.append(statement)

            current_statement = ""

    # Check for an incomplete final statement
    if current_statement.strip():
        raise ValueError(
            "Incomplete SQL statement found. "
            "Check the SQL file for a missing semicolon."
        )

    if not statements:
        raise ValueError(
            "No SQL statements found in the SQL file."
        )

    return statements


# --------------------------------------------------
# 3. EXECUTE SQL VALIDATION
# --------------------------------------------------

def run_sql_file():

    print("=" * 60)
    print("FINTECH 360 - SQL VALIDATION")
    print("=" * 60)

    # Check database existence
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )

    statements = read_sql_statements()

    print(f"\nSQL statements found: {len(statements)}")

    try:

        with sqlite3.connect(DB_PATH) as conn:

            cursor = conn.cursor()

            # Execute each SQL statement
            for index, statement in enumerate(
                statements,
                start=1
            ):

                print(f"\nQUERY {index}")
                print("-" * 60)

                cursor.execute(statement)

                # Display query results
                if cursor.description:

                    columns = [
                        column[0]
                        for column in cursor.description
                    ]

                    rows = cursor.fetchall()

                    print(" | ".join(columns))
                    print("-" * 60)

                    if rows:

                        for row in rows[:20]:
                            print(
                                " | ".join(
                                    str(value)
                                    for value in row
                                )
                            )

                        if len(rows) > 20:
                            print(
                                f"\nShowing 20 of {len(rows)} rows."
                            )

                    else:
                        print("No records returned.")

                    print(
                        f"\nTotal rows returned: {len(rows)}"
                    )

                else:

                    print("Statement executed successfully.")

        print("\n" + "=" * 60)
        print("SQL VALIDATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)

    except sqlite3.Error as error:

        print("\n" + "=" * 60)
        print("SQL VALIDATION FAILED!")
        print("=" * 60)

        print(f"Error: {error}")

        raise


# --------------------------------------------------
# 4. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_sql_file()
