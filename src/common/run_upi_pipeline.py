
import subprocess
import sys
import logging
import time

from pathlib import Path


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# --------------------------------------------------
# 2. LOGGING CONFIGURATION
# --------------------------------------------------

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "upi_pipeline.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    force=True
)


# --------------------------------------------------
# 3. PIPELINE STAGES
# --------------------------------------------------

PIPELINE_STAGES = [
    (
        "DATA INGESTION",
        PROJECT_ROOT / "src" / "ingestion" / "upi_ingestion.py"
    ),
    (
        "DATA QUALITY VALIDATION",
        PROJECT_ROOT / "src" / "quality" / "upi_quality_checks.py"
    ),
    (
        "DATA TRANSFORMATION",
        PROJECT_ROOT / "src" / "transformation" / "upi_transformation.py"
    ),
    (
        "SQLITE DATA LOADING",
        PROJECT_ROOT / "src" / "ingestion" / "load_upi_to_sqlite.py"
    ),
    (
        "SQL VALIDATION",
        PROJECT_ROOT / "src" / "common" / "run_sql.py"
    ),
    (
        "MART QUALITY VALIDATION",
        PROJECT_ROOT / "src" / "quality" / "upi_mart_quality_check.py"
    ),
    (
        "UPI FAILURE ANALYSIS",
        PROJECT_ROOT / "src" / "analytics" / "upi_failure_analysis.py"
    ),
    (
        "UPI TIME ANALYSIS",
        PROJECT_ROOT / "src" / "analytics" / "upi_time_analysis.py"
    ),
    (
        "UPI ANALYTICS",
        PROJECT_ROOT / "src" / "analytics" / "upi_analytics.py"
    ),
    (
        "UPI BUSINESS INSIGHTS",
        PROJECT_ROOT / "src" / "analytics" / "upi_business_insights.py"
    )
]


# --------------------------------------------------
# 4. EXECUTE PIPELINE STAGES
# --------------------------------------------------

def run_pipeline():

    pipeline_start_time = time.perf_counter()

    start_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    total_stages = len(PIPELINE_STAGES)

    completed_stages = 0

    logging.info("=" * 60)
    logging.info("UPI PIPELINE EXECUTION STARTED")
    logging.info("Start time: %s", start_timestamp)
    logging.info("Total stages: %s", total_stages)

    print("=" * 60)
    print("FINTECH 360 - UPI PIPELINE ORCHESTRATOR")
    print("=" * 60)

    try:

        for index, (stage_name, script_path) in enumerate(
            PIPELINE_STAGES,
            start=1
        ):

            print("\n" + "=" * 60)
            print(f"STAGE {index}/{total_stages}: {stage_name}")
            print("=" * 60)

            if not script_path.exists():
                raise FileNotFoundError(
                    f"Pipeline script not found: {script_path}"
                )

            try:

                stage_start_time = time.perf_counter()

                logging.info("STAGE STARTED: %s", stage_name)

                subprocess.run(
                    [sys.executable, str(script_path)],
                    cwd=PROJECT_ROOT,
                    check=True
                )

                execution_time = (
                    time.perf_counter() - stage_start_time
                )

                completed_stages += 1

                logging.info(
                    "STAGE COMPLETED: %s | Execution time: %.2f seconds",
                    stage_name,
                    execution_time
                )

                print(
                    f"\n{stage_name} COMPLETED SUCCESSFULLY! "
                    f"({execution_time:.2f} seconds)"
                )

            except subprocess.CalledProcessError as error:

                logging.exception(
                    "STAGE FAILED: %s | Exit code: %s",
                    stage_name,
                    error.returncode
                )

                print(f"\nPIPELINE FAILED AT: {stage_name}")
                print(f"Exit code: {error.returncode}")

                raise SystemExit(error.returncode)

    except Exception:

        logging.exception("UPI PIPELINE EXECUTION FAILED")

        raise

    finally:

        total_execution_time = (
            time.perf_counter() - pipeline_start_time
        )

        logging.info(
            "PIPELINE SUMMARY | Completed stages: %s/%s | "
            "Execution time: %.2f seconds",
            completed_stages,
            total_stages,
            total_execution_time
        )


    # --------------------------------------------------
    # 5. PIPELINE COMPLETION REPORT
    # --------------------------------------------------

    end_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    logging.info("UPI PIPELINE EXECUTION COMPLETED")
    logging.info("End time: %s", end_timestamp)

    print("\n" + "=" * 60)
    print("UPI PIPELINE EXECUTION SUMMARY")
    print("=" * 60)

    print(f"Total stages     : {total_stages}")
    print(f"Completed stages : {completed_stages}")
    print(f"Failed stages    : 0")
    print(f"Execution time   : {total_execution_time:.2f} seconds")
    print(f"Log file         : {LOG_FILE}")

    print("\nALL UPI PIPELINE STAGES COMPLETED SUCCESSFULLY!")

    print("=" * 60)


# --------------------------------------------------
# 6. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_pipeline()
