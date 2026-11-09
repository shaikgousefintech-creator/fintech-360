"""
FINTECH 360 - UPI BUSINESS INSIGHTS

Reads existing UPI analytical CSV files and generates:
1. Bank performance insights
2. Payment app performance insights
3. Failure reason insights
4. High-risk transaction hour and weekday insights
5. Business recommendations
"""

from pathlib import Path
import pandas as pd


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "data" / "warehouse" / "upi"

OUTPUT_DIR = PROJECT_ROOT / "data" / "warehouse" / "upi"


# --------------------------------------------------
# 2. LOAD EXISTING ANALYTICAL OUTPUTS
# --------------------------------------------------

def load_analytics():

    files = {
        "banks": "upi_bank_failure_analysis.csv",
        "apps": "upi_app_failure_analysis.csv",
        "reasons": "upi_failure_reason_analysis.csv",
        "hourly": "upi_hourly_analysis.csv",
        "weekdays": "upi_weekday_analysis.csv"
    }

    data = {}

    for name, file_name in files.items():

        file_path = INPUT_DIR / file_name

        if not file_path.exists():
            raise FileNotFoundError(
                f"Required analytics file not found: {file_path}"
            )

        data[name] = pd.read_csv(file_path)

        if data[name].empty:
            raise ValueError(
                f"Analytics file contains no records: {file_name}"
            )

    print("All five analytical files loaded successfully.")

    return data


# --------------------------------------------------
# 3. GENERATE BUSINESS INSIGHTS
# --------------------------------------------------

def generate_insights(data):

    banks = data["banks"]
    apps = data["apps"]
    reasons = data["reasons"]
    hourly = data["hourly"]
    weekdays = data["weekdays"]

    insights = []

    # Bank insights
    worst_bank = banks.loc[
        banks["failure_rate_percentage"].idxmax()
    ]

    best_bank = banks.loc[
        banks["failure_rate_percentage"].idxmin()
    ]

    insights.append(
        f"Bank with highest failure rate: "
        f"{worst_bank['payer_bank']} "
        f"({worst_bank['failure_rate_percentage']:.2f}%)."
    )

    insights.append(
        f"Bank with lowest failure rate: "
        f"{best_bank['payer_bank']} "
        f"({best_bank['failure_rate_percentage']:.2f}%)."
    )

    # Payment app insights
    worst_app = apps.loc[
        apps["failure_rate_percentage"].idxmax()
    ]

    best_app = apps.loc[
        apps["failure_rate_percentage"].idxmin()
    ]

    insights.append(
        f"Payment app with highest failure rate: "
        f"{worst_app['payment_app']} "
        f"({worst_app['failure_rate_percentage']:.2f}%)."
    )

    insights.append(
        f"Payment app with lowest failure rate: "
        f"{best_app['payment_app']} "
        f"({best_app['failure_rate_percentage']:.2f}%)."
    )

    # Failure reason insights
    top_reason = reasons.loc[
        reasons["failed_transactions"].idxmax()
    ]

    insights.append(
        f"Most common failure reason: "
        f"{top_reason['failure_reason']} "
        f"({top_reason['failed_transactions']} failures, "
        f"{top_reason['failure_percentage']:.2f}% of failures)."
    )

    # Hourly insights
    worst_hour = hourly.loc[
        hourly["failure_rate_percentage"].idxmax()
    ]

    insights.append(
        f"Hour with highest failure rate: "
        f"{int(worst_hour['transaction_hour']):02d}:00 "
        f"({worst_hour['failure_rate_percentage']:.2f}%, "
        f"{int(worst_hour['total_transactions'])} transactions)."
    )

    # Weekday insights
    worst_weekday = weekdays.loc[
        weekdays["failure_rate_percentage"].idxmax()
    ]

    insights.append(
        f"Weekday with highest failure rate: "
        f"{worst_weekday['transaction_day_of_week']} "
        f"({worst_weekday['failure_rate_percentage']:.2f}%)."
    )

    return insights


# --------------------------------------------------
# 4. GENERATE BUSINESS RECOMMENDATIONS
# --------------------------------------------------

def generate_recommendations(data):

    banks = data["banks"]
    apps = data["apps"]
    reasons = data["reasons"]
    hourly = data["hourly"]
    weekdays = data["weekdays"]

    recommendations = []

    worst_bank = banks.loc[
        banks["failure_rate_percentage"].idxmax()
    ]

    recommendations.append({
        "area": "Bank Performance",
        "observation": (
            f"{worst_bank['payer_bank']} has the highest "
            f"failure rate of "
            f"{worst_bank['failure_rate_percentage']:.2f}%."
        ),
        "recommendation": (
            "Investigate bank-specific failures, server "
            "availability and transaction response times."
        )
    })

    worst_app = apps.loc[
        apps["failure_rate_percentage"].idxmax()
    ]

    recommendations.append({
        "area": "Payment App Performance",
        "observation": (
            f"{worst_app['payment_app']} has the highest "
            f"failure rate of "
            f"{worst_app['failure_rate_percentage']:.2f}%."
        ),
        "recommendation": (
            "Review app integration, payment routing and "
            "error-handling mechanisms."
        )
    })

    top_reason = reasons.loc[
        reasons["failed_transactions"].idxmax()
    ]

    recommendations.append({
        "area": "Failure Reasons",
        "observation": (
            f"{top_reason['failure_reason']} is the most "
            f"common failure reason."
        ),
        "recommendation": (
            "Investigate the underlying cause and introduce "
            "appropriate customer guidance or technical fixes."
        )
    })

    worst_hour = hourly.loc[
        hourly["failure_rate_percentage"].idxmax()
    ]

    recommendations.append({
        "area": "Transaction Timing",
        "observation": (
            f"{int(worst_hour['transaction_hour']):02d}:00 "
            f"has the highest hourly failure rate of "
            f"{worst_hour['failure_rate_percentage']:.2f}%."
        ),
        "recommendation": (
            "Monitor transaction processing and bank response "
            "times during this hour."
        )
    })

    worst_weekday = weekdays.loc[
        weekdays["failure_rate_percentage"].idxmax()
    ]

    recommendations.append({
        "area": "Weekday Performance",
        "observation": (
            f"{worst_weekday['transaction_day_of_week']} "
            f"has the highest weekday failure rate of "
            f"{worst_weekday['failure_rate_percentage']:.2f}%."
        ),
        "recommendation": (
            "Monitor service reliability and failure patterns "
            "on this weekday."
        )
    })

    return pd.DataFrame(recommendations)


# --------------------------------------------------
# 5. SAVE BUSINESS INSIGHTS
# --------------------------------------------------

def save_outputs(insights, recommendations):

    insights_file = OUTPUT_DIR / "upi_business_insights.txt"

    recommendations_file = (
        OUTPUT_DIR / "upi_business_recommendations.csv"
    )

    with open(insights_file, "w", encoding="utf-8") as file:

        file.write("FINTECH 360 - UPI BUSINESS INSIGHTS\n")
        file.write("=" * 55 + "\n\n")

        for number, insight in enumerate(insights, start=1):

            file.write(f"{number}. {insight}\n")

    recommendations.to_csv(
        recommendations_file,
        index=False
    )

    print(f"\nGenerated: {insights_file}")
    print(f"Generated: {recommendations_file}")


# --------------------------------------------------
# 6. EXECUTION ENTRY POINT
# --------------------------------------------------

def run_business_insights():

    print("\n" + "=" * 55)
    print("FINTECH 360 - UPI BUSINESS INSIGHTS")
    print("=" * 55)

    data = load_analytics()

    insights = generate_insights(data)

    recommendations = generate_recommendations(data)

    print("\nBUSINESS INSIGHTS")
    print("-" * 55)

    for number, insight in enumerate(insights, start=1):
        print(f"{number}. {insight}")

    print("\nBUSINESS RECOMMENDATIONS")
    print("-" * 55)

    print(
        recommendations.to_string(index=False)
    )

    save_outputs(insights, recommendations)

    print("\nUPI BUSINESS INSIGHTS COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    run_business_insights()