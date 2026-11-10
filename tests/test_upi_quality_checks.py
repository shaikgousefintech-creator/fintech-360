
import pandas as pd

from src.quality.upi_quality_checks import validate_upi_data


def create_valid_test_data():

    return pd.DataFrame([
        {
            "transaction_id": "UPI000001",
            "payer_id": "P001",
            "payee_id": "P002",
            "transaction_type": "P2P",
            "amount": 500.00,
            "currency": "INR",
            "transaction_timestamp": "2026-11-01 10:30:00.000000",
            "status": "SUCCESS",
            "failure_reason": None,
            "merchant_name": None
        },
        {
            "transaction_id": "UPI000002",
            "payer_id": "P003",
            "payee_id": "P004",
            "transaction_type": "P2M",
            "amount": 750.00,
            "currency": "INR",
            "transaction_timestamp": "2026-11-01 11:30:00.000000",
            "status": "FAILED",
            "failure_reason": "INSUFFICIENT_BALANCE",
            "merchant_name": "ABC Stores"
        }
    ])


def test_valid_data_passes_all_checks():

    df = create_valid_test_data()

    results = validate_upi_data(df)

    assert all(results.values())


def test_duplicate_transaction_ids_fail():

    df = create_valid_test_data()
    df.loc[1, "transaction_id"] = "UPI000001"

    results = validate_upi_data(df)

    assert results["Unique transaction IDs"] is False



def test_invalid_transaction_amount_fails():

    df = create_valid_test_data()
    df.loc[0, "amount"] = -100

    results = validate_upi_data(df)

    assert not results["Valid transaction amounts"]



def test_failed_transaction_without_reason_fails():

    df = create_valid_test_data()
    df.loc[1, "failure_reason"] = None

    results = validate_upi_data(df)

    assert results["Failed transactions have reasons"] is False


def test_missing_required_column_fails():

    df = create_valid_test_data()
    df = df.drop(columns=["payer_id"])

    results = validate_upi_data(df)

    assert results["Required columns present"] is False


def test_invalid_timestamp_fails():

    df = create_valid_test_data()
    df.loc[0, "transaction_timestamp"] = "invalid-date"

    results = validate_upi_data(df)

    assert not results["Valid timestamps"]


def test_invalid_transaction_status_fails():

    df = create_valid_test_data()
    df.loc[0, "status"] = "UNKNOWN"

    results = validate_upi_data(df)

    assert not results["Valid transaction statuses"]


def test_p2m_without_merchant_name_fails():

    df = create_valid_test_data()
    df.loc[1, "merchant_name"] = None

    results = validate_upi_data(df)

    assert not results["P2M transactions have merchant names"]
