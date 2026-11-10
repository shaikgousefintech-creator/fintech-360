
import pandas as pd
import pytest

from src.analytics import upi_analytics


# --------------------------------------------------
# TEST DATA
# --------------------------------------------------

@pytest.fixture
def sample_data():

    return pd.DataFrame({
        "transaction_id": ["T001", "T002", "T003", "T004"],
        "amount": [100.00, 50.00, 200.00, 150.00],
        "status": ["SUCCESS", "FAILED", "PENDING", "SUCCESS"],
        "transaction_date": [
            "2026-01-01",
            "2026-01-01",
            "2026-01-02",
            "2026-01-02"
        ],
        "payment_app": ["BHIM", "BHIM", "PHONEPE", "PHONEPE"],
        "payer_bank": ["ICICI", "PNB", "ICICI", "PNB"]
    }).assign(
        transaction_date=lambda df: pd.to_datetime(
            df["transaction_date"]
        ).dt.date
    )


# --------------------------------------------------
# TEST OVERALL BUSINESS KPIs
# --------------------------------------------------

def test_overall_kpis(sample_data):

    result = upi_analytics.generate_overall_kpis(sample_data)

    kpis = result.set_index("metric")["value"]

    assert kpis["total_transactions"] == 4
    assert kpis["successful_transactions"] == 2
    assert kpis["failed_transactions"] == 1
    assert kpis["pending_transactions"] == 1

    assert kpis["total_transaction_value"] == 500.00
    assert kpis["successful_transaction_value"] == 250.00
    assert kpis["average_transaction_amount"] == 125.00

    assert kpis["success_rate_percentage"] == 50.00
    assert kpis["failure_rate_percentage"] == 25.00
    assert kpis["pending_rate_percentage"] == 25.00


# --------------------------------------------------
# TEST DAILY TRANSACTION TRENDS
# --------------------------------------------------

def test_daily_trends(sample_data):

    result = upi_analytics.generate_daily_trends(sample_data)

    assert len(result) == 2

    first_day = result.iloc[0]
    second_day = result.iloc[1]

    assert first_day["total_transactions"] == 2
    assert first_day["successful_transactions"] == 1
    assert first_day["failed_transactions"] == 1
    assert first_day["total_transaction_value"] == 150.00

    assert second_day["total_transactions"] == 2
    assert second_day["successful_transactions"] == 1
    assert second_day["pending_transactions"] == 1
    assert second_day["total_transaction_value"] == 350.00


# --------------------------------------------------
# TEST PAYMENT APP PERFORMANCE
# --------------------------------------------------

def test_payment_app_performance(sample_data):

    result = upi_analytics.generate_dimension_performance(
        sample_data, "payment_app"
    )

    assert len(result) == 2

    bhim = result.loc[
        result["payment_app"] == "BHIM"
    ].iloc[0]

    assert bhim["total_transactions"] == 2
    assert bhim["successful_transactions"] == 1
    assert bhim["failed_transactions"] == 1
    assert bhim["success_rate_percentage"] == 50.00
    assert bhim["successful_transaction_value"] == 100.00


# --------------------------------------------------
# TEST PAYER BANK PERFORMANCE
# --------------------------------------------------

def test_payer_bank_performance(sample_data):

    result = upi_analytics.generate_dimension_performance(
        sample_data, "payer_bank"
    )

    assert len(result) == 2

    icici = result.loc[
        result["payer_bank"] == "ICICI"
    ].iloc[0]

    assert icici["total_transactions"] == 2
    assert icici["successful_transactions"] == 1
    assert icici["pending_transactions"] == 1
    assert icici["total_transaction_value"] == 300.00


# --------------------------------------------------
# TEST CURATED DATA LOADING
# --------------------------------------------------

def test_load_curated_data(sample_data, tmp_path, monkeypatch):

    input_file = tmp_path / "upi_transactions_curated.csv"

    sample_data.to_csv(input_file, index=False)

    monkeypatch.setattr(
        upi_analytics,
        "INPUT_DIR",
        tmp_path
    )

    result = upi_analytics.load_curated_data()

    assert len(result) == 4
    assert "transaction_id" in result.columns
    assert result["amount"].notna().all()


def test_load_curated_data_missing_columns(tmp_path, monkeypatch):

    input_file = tmp_path / "upi_transactions_curated.csv"

    pd.DataFrame({
        "transaction_id": ["T001"],
        "amount": [100]
    }).to_csv(input_file, index=False)

    monkeypatch.setattr(
        upi_analytics,
        "INPUT_DIR",
        tmp_path
    )

    with pytest.raises(ValueError, match="Missing required columns"):
        upi_analytics.load_curated_data()


def test_load_curated_data_invalid_amount(tmp_path, monkeypatch):

    input_file = tmp_path / "upi_transactions_curated.csv"

    pd.DataFrame({
        "transaction_id": ["T001"],
        "amount": ["invalid"],
        "status": ["SUCCESS"],
        "transaction_date": ["2026-01-01"],
        "payment_app": ["BHIM"],
        "payer_bank": ["ICICI"]
    }).to_csv(input_file, index=False)

    monkeypatch.setattr(
        upi_analytics,
        "INPUT_DIR",
        tmp_path
    )

    with pytest.raises(ValueError, match="Invalid or missing transaction amounts"):
        upi_analytics.load_curated_data()


def test_save_analytics(sample_data, tmp_path, monkeypatch):

    output = upi_analytics.generate_overall_kpis(sample_data)

    monkeypatch.setattr(
        upi_analytics,
        "OUTPUT_DIR",
        tmp_path
    )

    upi_analytics.save_analytics({
        "test_upi_kpis.csv": output
    })

    saved_file = tmp_path / "test_upi_kpis.csv"

    assert saved_file.exists()

    saved_data = pd.read_csv(saved_file)

    assert len(saved_data) == 10
