
import pandas as pd
import pytest

from src.ingestion.upi_ingestion import validate_data


def create_valid_ingestion_data():

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


def test_valid_records_are_processed():

    df = create_valid_ingestion_data()

    valid_df, rejected_df = validate_data(df)

    assert len(valid_df) == 2
    assert len(rejected_df) == 0


def test_invalid_amount_is_rejected():

    df = create_valid_ingestion_data()
    df.loc[0, "amount"] = -100

    valid_df, rejected_df = validate_data(df)

    assert len(valid_df) == 1
    assert len(rejected_df) == 1
    assert "Invalid transaction amount" in (
        rejected_df.iloc[0]["rejection_reason"]
    )


def test_duplicate_transaction_ids_are_rejected():

    df = create_valid_ingestion_data()
    df.loc[1, "transaction_id"] = "UPI000001"

    valid_df, rejected_df = validate_data(df)

    assert len(valid_df) == 0
    assert len(rejected_df) == 2
    assert rejected_df["rejection_reason"].str.contains(
        "Duplicate transaction ID"
    ).all()


def test_failed_transaction_without_reason_is_rejected():

    df = create_valid_ingestion_data()
    df.loc[1, "failure_reason"] = None

    valid_df, rejected_df = validate_data(df)

    assert len(valid_df) == 1
    assert len(rejected_df) == 1
    assert "Missing failure reason" in (
        rejected_df.iloc[0]["rejection_reason"]
    )


def test_p2m_without_merchant_is_rejected():

    df = create_valid_ingestion_data()
    df.loc[1, "merchant_name"] = None

    valid_df, rejected_df = validate_data(df)

    assert len(valid_df) == 1
    assert len(rejected_df) == 1
    assert "Missing merchant name" in (
        rejected_df.iloc[0]["rejection_reason"]
    )


def test_missing_required_column_raises_error():

    df = create_valid_ingestion_data()
    df = df.drop(columns=["payer_id"])

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_data(df)


def test_invalid_timestamp_is_rejected():

    df = create_valid_ingestion_data()
    df.loc[0, "transaction_timestamp"] = "invalid-date"

    valid_df, rejected_df = validate_data(df)

    assert len(valid_df) == 1
    assert len(rejected_df) == 1
    assert "Invalid transaction timestamp" in (
        rejected_df.iloc[0]["rejection_reason"]
    )


def test_string_values_are_standardized():

    df = create_valid_ingestion_data()

    df.loc[0, "status"] = " success "
    df.loc[0, "currency"] = " inr "

    valid_df, rejected_df = validate_data(df)

    assert len(valid_df) == 2
    assert len(rejected_df) == 0
    assert valid_df.loc[0, "status"] == "SUCCESS"
    assert valid_df.loc[0, "currency"] == "INR"
