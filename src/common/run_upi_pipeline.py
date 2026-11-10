
import subprocess
import sys
from pathlib import Path


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]


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
# 2. EXECUTE PIPELINE STAGES
# --------------------------------------------------

def run_pipeline():

    print("=" * 60)
    print("FINTECH 360 - UPI PIPELINE ORCHESTRATOR")
    print("=" * 60)

    total_stages = len(PIPELINE_STAGES)

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

            subprocess.run(
                [sys.executable, str(script_path)],
                cwd=PROJECT_ROOT,
                check=True
            )

            print(f"\n{stage_name} COMPLETED SUCCESSFULLY!")

        except subprocess.CalledProcessError as error:

            print(f"\nPIPELINE FAILED AT: {stage_name}")
            print(f"Exit code: {error.returncode}")

            raise SystemExit(error.returncode)

    print("\n" + "=" * 60)
    print("ALL UPI PIPELINE STAGES COMPLETED SUCCESSFULLY!")
    print("=" * 60)


# --------------------------------------------------
# 3. EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_pipeline()
