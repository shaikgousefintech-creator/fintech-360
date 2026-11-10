
from pathlib import Path

import pandas as pd
import pytest

from src.analytics import upi_business_insights as business


# --------------------------------------------------
# 1. SAMPLE ANALYTICAL DATA
# --------------------------------------------------

@pytest.fixture
def sample_data():

    return {
        "banks": pd.DataFrame({
            "payer_bank": ["ICICI", "PNB"],
            "total_transactions": [100, 100],
            "failed_transactions": [10, 3],
            "failure_rate_percentage": [10.0, 3.0]
        }),

        "apps": pd.DataFrame({
            "payment_app": ["BHIM", "PHONEPE"],
            "total_transactions": [100, 100],
            "failed_transactions": [8, 2],
            "failure_rate_percentage": [8.0, 2.0]
        }),

        "reasons": pd.DataFrame({
            "failure_reason": [
                "INSUFFICIENT_BALANCE",
                "INVALID_VPA"
            ],
            "failed_transactions": [15, 5],
            "failure_percentage": [75.0, 25.0]
        }),

        "hourly": pd.DataFrame({
            "transaction_hour": [10, 14],
            "total_transactions": [100, 200],
            "failed_transactions": [5, 20],
            "failure_rate_percentage": [5.0, 10.0]
        }),

        "weekdays": pd.DataFrame({
            "transaction_day_of_week": ["Monday", "Sunday"],
            "total_transactions": [100, 150],
            "failed_transactions": [3, 12],
            "failure_rate_percentage": [3.0, 8.0]
        })
    }


# --------------------------------------------------
# 2. BUSINESS INSIGHTS TESTS
# --------------------------------------------------

def test_generate_seven_business_insights(sample_data):

    insights = business.generate_insights(sample_data)

    assert len(insights) == 7


def test_highest_and_lowest_bank_failure_rates(sample_data):

    insights = business.generate_insights(sample_data)

    assert "ICICI" in insights[0]
    assert "PNB" in insights[1]


def test_highest_and_lowest_app_failure_rates(sample_data):

    insights = business.generate_insights(sample_data)

    assert "BHIM" in insights[2]
    assert "PHONEPE" in insights[3]


def test_failure_reason_insight(sample_data):

    insights = business.generate_insights(sample_data)

    assert "INSUFFICIENT_BALANCE" in insights[4]


def test_highest_risk_hour_and_weekday(sample_data):

    insights = business.generate_insights(sample_data)

    assert "14:00" in insights[5]
    assert "Sunday" in insights[6]


# --------------------------------------------------
# 3. BUSINESS RECOMMENDATION TESTS
# --------------------------------------------------

def test_generate_five_recommendations(sample_data):

    recommendations = business.generate_recommendations(
        sample_data
    )

    assert len(recommendations) == 5

    assert list(recommendations.columns) == [
        "area",
        "observation",
        "recommendation"
    ]


# --------------------------------------------------
# 4. ANALYTICAL FILE VALIDATION TESTS
# --------------------------------------------------

def test_load_all_valid_analytics_files(
    tmp_path, monkeypatch
):

    monkeypatch.setattr(business, "INPUT_DIR", tmp_path)

    sample_files = {
        "upi_bank_failure_analysis.csv": pd.DataFrame({
            "payer_bank": ["ICICI"],
            "total_transactions": [100],
            "failed_transactions": [5],
            "failure_rate_percentage": [5.0]
        }),

        "upi_app_failure_analysis.csv": pd.DataFrame({
            "payment_app": ["BHIM"],
            "total_transactions": [100],
            "failed_transactions": [5],
            "failure_rate_percentage": [5.0]
        }),

        "upi_failure_reason_analysis.csv": pd.DataFrame({
            "failure_reason": ["INVALID_VPA"],
            "failed_transactions": [5],
            "failure_percentage": [100.0]
        }),

        "upi_hourly_analysis.csv": pd.DataFrame({
            "transaction_hour": [14],
            "total_transactions": [100],
            "failed_transactions": [5],
            "failure_rate_percentage": [5.0]
        }),

        "upi_weekday_analysis.csv": pd.DataFrame({
            "transaction_day_of_week": ["Sunday"],
            "total_transactions": [100],
            "failed_transactions": [5],
            "failure_rate_percentage": [5.0]
        })
    }

    for file_name, df in sample_files.items():
        df.to_csv(tmp_path / file_name, index=False)

    data = business.load_analytics()

    assert len(data) == 5


def test_missing_analytics_file_raises_error(
    tmp_path, monkeypatch
):

    monkeypatch.setattr(business, "INPUT_DIR", tmp_path)

    with pytest.raises(FileNotFoundError):
        business.load_analytics()


def test_empty_analytics_file_raises_error(
    tmp_path, monkeypatch
):

    monkeypatch.setattr(business, "INPUT_DIR", tmp_path)

    for file_name in [
        "upi_bank_failure_analysis.csv",
        "upi_app_failure_analysis.csv",
        "upi_failure_reason_analysis.csv",
        "upi_hourly_analysis.csv",
        "upi_weekday_analysis.csv"
    ]:
        pd.DataFrame().to_csv(
            tmp_path / file_name,
            index=False
        )

    with pytest.raises(ValueError):
        business.load_analytics()


def test_missing_required_columns_raises_error(
    tmp_path, monkeypatch
):

    monkeypatch.setattr(business, "INPUT_DIR", tmp_path)

    pd.DataFrame({
        "wrong_column": [100]
    }).to_csv(
        tmp_path / "upi_bank_failure_analysis.csv",
        index=False
    )

    with pytest.raises(ValueError):
        business.load_analytics()


# --------------------------------------------------
# 5. OUTPUT FILE TEST
# --------------------------------------------------

def test_save_business_insights_outputs(
    tmp_path, monkeypatch, sample_data
):

    monkeypatch.setattr(business, "OUTPUT_DIR", tmp_path)

    insights = business.generate_insights(sample_data)

    recommendations = business.generate_recommendations(
        sample_data
    )

    business.save_outputs(insights, recommendations)

    insights_file = tmp_path / "upi_business_insights.txt"

    recommendations_file = (
        tmp_path / "upi_business_recommendations.csv"
    )

    assert insights_file.exists()
    assert recommendations_file.exists()

    saved_recommendations = pd.read_csv(
        recommendations_file
    )

    assert len(saved_recommendations) == 5
