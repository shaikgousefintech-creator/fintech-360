
import sqlite3

import pandas as pd
import pytest

from src.analytics import digital_gold_analytics


# --------------------------------------------------
# TEST DATABASE
# --------------------------------------------------

@pytest.fixture
def sample_database(tmp_path):

    db_path = tmp_path / "digital_gold_test.db"

    with sqlite3.connect(db_path) as conn:

        # CUSTOMER PERFORMANCE MART

        pd.DataFrame({
            "customer_id": ["C001", "C002"],
            "customer_name": ["Aarav Sharma", "Isha Kumar"],
            "customer_segment": ["REGULAR", "PREMIUM"],
            "city": ["Mumbai", "Bengaluru"],
            "total_transactions": [3, 2],
            "successful_transactions": [2, 2],
            "failed_transactions": [1, 0],
            "pending_transactions": [0, 0],
            "total_buy_amount": [20000.00, 30000.00],
            "total_sell_amount": [5000.00, 10000.00],
            "total_gold_bought_grams": [10.0, 15.0],
            "total_gold_sold_grams": [2.5, 5.0]
        }).to_sql(
            "mart_dg_customer_performance",
            conn,
            index=False
        )

        # CUSTOMER SEGMENT PERFORMANCE MART

        pd.DataFrame({
            "customer_segment": ["REGULAR", "PREMIUM"],
            "total_customers": [1, 1],
            "total_transactions": [3, 2],
            "successful_transactions": [2, 2],
            "failed_transactions": [1, 0],
            "pending_transactions": [0, 0],
            "total_buy_amount": [20000.00, 30000.00],
            "total_sell_amount": [5000.00, 10000.00],
            "success_rate_percentage": [66.67, 100.00]
        }).to_sql(
            "mart_dg_customer_segment_performance",
            conn,
            index=False
        )

        # DAILY PERFORMANCE MART

        pd.DataFrame({
            "transaction_date": [
                "2026-01-01",
                "2026-01-02"
            ],
            "total_transactions": [3, 2],
            "successful_transactions": [2, 2],
            "failed_transactions": [1, 0],
            "pending_transactions": [0, 0],
            "successful_buy_transactions": [1, 1],
            "successful_sell_transactions": [1, 1],
            "total_successful_transaction_amount": [
                15000.00,
                35000.00
            ],
            "total_buy_amount": [10000.00, 30000.00],
            "total_sell_amount": [5000.00, 5000.00],
            "success_rate_percentage": [66.67, 100.00]
        }).to_sql(
            "mart_dg_daily_performance",
            conn,
            index=False
        )

        # TRANSACTION SOURCE TABLE

        pd.DataFrame({
            "transaction_id": [
                "T001",
                "T002",
                "T003",
                "T004"
            ],
            "investment_mode": [
                "UPI",
                "CARD",
                "UPI",
                "WALLET"
            ],
            "transaction_status": [
                "SUCCESS",
                "SUCCESS",
                "FAILED",
                "PENDING"
            ],
            "transaction_type": [
                "BUY",
                "BUY",
                "SELL",
                "SELL"
            ],
            "amount": [
                10000.00,
                20000.00,
                5000.00,
                3000.00
            ],
            "gold_quantity_grams": [
                5.0,
                10.0,
                2.5,
                1.5
            ]
        }).to_sql(
            "dg_transactions",
            conn,
            index=False
        )

        # TRANSACTION TYPE PERFORMANCE MART

        pd.DataFrame({
            "transaction_type": ["BUY", "SELL"],
            "total_transactions": [2, 2],
            "successful_transactions": [2, 0],
            "failed_transactions": [0, 1],
            "pending_transactions": [0, 1],
            "total_successful_amount": [
                30000.00,
                0.00
            ],
            "total_successful_gold_quantity_grams": [
                15.0,
                0.0
            ],
            "success_rate_percentage": [100.00, 0.00]
        }).to_sql(
            "mart_dg_transaction_type_performance",
            conn,
            index=False
        )

        # GOLD PRICE HISTORY

        pd.DataFrame({
            "price_id": ["P001", "P002", "P003"],
            "price_date": [
                "2026-01-01",
                "2026-01-02",
                "2026-01-03"
            ],
            "gold_price_per_gram": [
                10000.00,
                10100.00,
                10050.00
            ],
            "buy_price_per_gram": [
                10300.00,
                10403.00,
                10351.50
            ],
            "sell_price_per_gram": [
                9700.00,
                9797.00,
                9748.50
            ]
        }).to_sql(
            "dg_price_history",
            conn,
            index=False
        )

        # CUSTOMER MASTER

        pd.DataFrame({
            "customer_id": ["C001", "C002"],
            "customer_name": [
                "Aarav Sharma",
                "Isha Kumar"
            ],
            "customer_segment": [
                "REGULAR",
                "PREMIUM"
            ],
            "city": [
                "Mumbai",
                "Bengaluru"
            ]
        }).to_sql(
            "dg_customers",
            conn,
            index=False
        )

        # WALLET LEDGER

        pd.DataFrame({
            "ledger_id": [
                "L001",
                "L002",
                "L003"
            ],
            "customer_id": [
                "C001",
                "C001",
                "C002"
            ],
            "balance_after_grams": [
                5.0,
                7.5,
                10.0
            ],
            "entry_date": [
                "2026-01-01",
                "2026-01-03",
                "2026-01-02"
            ]
        }).to_sql(
            "dg_wallet_ledger",
            conn,
            index=False
        )

    return db_path


# --------------------------------------------------
# TEST OUTPUT DIRECTORY
# --------------------------------------------------

@pytest.fixture
def output_directory(tmp_path, monkeypatch):

    output_dir = tmp_path / "digital_gold_output"
    output_dir.mkdir()

    monkeypatch.setattr(
        digital_gold_analytics,
        "OUTPUT_DIR",
        output_dir
    )

    return output_dir


# --------------------------------------------------
# TEST CUSTOMER BEHAVIOR ANALYSIS
# --------------------------------------------------

def test_generate_customer_behavior(
    sample_database,
    output_directory
):

    with sqlite3.connect(sample_database) as conn:

        result = digital_gold_analytics.generate_customer_behavior(
            conn
        )

    assert len(result) == 2

    assert "customer_id" in result.columns
    assert "customer_name" in result.columns
    assert "success_rate_percentage" in result.columns

    customer = result.loc[
        result["customer_id"] == "C001"
    ].iloc[0]

    assert customer["total_transactions"] == 3
    assert customer["successful_transactions"] == 2
    assert customer["total_buy_amount"] == 20000.00
    assert customer["total_sell_amount"] == 5000.00
    assert customer["success_rate_percentage"] == 66.67

    assert (
        output_directory / "dg_customer_behavior.csv"
    ).exists()


# --------------------------------------------------
# TEST CUSTOMER SEGMENT ANALYSIS
# --------------------------------------------------

def test_generate_customer_segment_analysis(
    sample_database,
    output_directory
):

    with sqlite3.connect(sample_database) as conn:

        result = (
            digital_gold_analytics
            .generate_customer_segment_analysis(conn)
        )

    assert len(result) == 2

    regular = result.loc[
        result["customer_segment"] == "REGULAR"
    ].iloc[0]

    assert regular["total_customers"] == 1
    assert regular["total_transactions"] == 3
    assert regular["successful_transactions"] == 2
    assert regular["net_purchase_amount"] == 15000.00
    assert regular["average_buy_amount_per_customer"] == 20000.00

    assert (
        output_directory / "dg_customer_segment_analysis.csv"
    ).exists()


# --------------------------------------------------
# TEST DAILY TRANSACTION TRENDS
# --------------------------------------------------

def test_generate_daily_trends(
    sample_database,
    output_directory
):

    with sqlite3.connect(sample_database) as conn:

        result = digital_gold_analytics.generate_daily_trends(
            conn
        )

    assert len(result) == 2

    first_day = result.iloc[0]
    second_day = result.iloc[1]

    assert first_day["transaction_date"] == "2026-01-01"
    assert first_day["total_transactions"] == 3
    assert first_day["successful_transactions"] == 2
    assert first_day["failed_transactions"] == 1
    assert first_day["total_successful_transaction_amount"] == 15000.00

    assert second_day["transaction_date"] == "2026-01-02"
    assert second_day["total_transactions"] == 2
    assert second_day["successful_transactions"] == 2
    assert second_day["total_successful_transaction_amount"] == 35000.00

    assert (
        output_directory / "dg_daily_trends.csv"
    ).exists()


# --------------------------------------------------
# TEST INVESTMENT MODE ANALYSIS
# --------------------------------------------------

def test_generate_investment_mode_analysis(
    sample_database,
    output_directory
):

    with sqlite3.connect(sample_database) as conn:

        result = (
            digital_gold_analytics
            .generate_investment_mode_analysis(conn)
        )

    assert len(result) == 3

    upi = result.loc[
        result["investment_mode"] == "UPI"
    ].iloc[0]

    assert upi["total_transactions"] == 2
    assert upi["successful_transactions"] == 1
    assert upi["failed_transactions"] == 1
    assert upi["pending_transactions"] == 0
    assert upi["successful_transaction_amount"] == 10000.00
    assert upi["successful_gold_quantity_grams"] == 5.0
    assert upi["success_rate_percentage"] == 50.0

    assert (
        output_directory / "dg_investment_mode_analysis.csv"
    ).exists()


# --------------------------------------------------
# TEST BUY AND SELL ANALYSIS
# --------------------------------------------------

def test_generate_buy_sell_analysis(
    sample_database,
    output_directory
):

    with sqlite3.connect(sample_database) as conn:

        result = (
            digital_gold_analytics
            .generate_buy_sell_analysis(conn)
        )

    assert len(result) == 2

    buy = result.loc[
        result["transaction_type"] == "BUY"
    ].iloc[0]

    sell = result.loc[
        result["transaction_type"] == "SELL"
    ].iloc[0]

    assert buy["total_transactions"] == 2
    assert buy["successful_transactions"] == 2
    assert buy["total_successful_amount"] == 30000.00
    assert buy["total_successful_gold_quantity_grams"] == 15.0

    assert sell["total_transactions"] == 2
    assert sell["successful_transactions"] == 0
    assert sell["total_successful_amount"] == 0.00

    assert (
        output_directory / "dg_buy_sell_analysis.csv"
    ).exists()


# --------------------------------------------------
# TEST GOLD PRICE TRENDS
# --------------------------------------------------

def test_generate_gold_price_trends(
    sample_database,
    output_directory
):

    with sqlite3.connect(sample_database) as conn:

        result = (
            digital_gold_analytics
            .generate_gold_price_trends(conn)
        )

    assert len(result) == 3

    first_day = result.iloc[0]
    second_day = result.iloc[1]
    third_day = result.iloc[2]

    assert first_day["gold_price_per_gram"] == 10000.00
    assert pd.isna(first_day["daily_price_change"])

    assert second_day["daily_price_change"] == 100.00
    assert second_day["daily_price_change_percentage"] == 1.00

    assert third_day["daily_price_change"] == -50.00

    assert (
        output_directory / "dg_gold_price_trends.csv"
    ).exists()


# --------------------------------------------------
# TEST WALLET BALANCE ANALYSIS
# --------------------------------------------------

def test_generate_wallet_balance_analysis(
    sample_database,
    output_directory
):

    with sqlite3.connect(sample_database) as conn:

        result = (
            digital_gold_analytics
            .generate_wallet_balance_analysis(conn)
        )

    assert len(result) == 2

    customer_one = result.loc[
        result["customer_id"] == "C001"
    ].iloc[0]

    customer_two = result.loc[
        result["customer_id"] == "C002"
    ].iloc[0]

    assert customer_one["current_gold_balance_grams"] == 7.5
    assert customer_one["last_ledger_entry_date"] == "2026-01-03"

    assert customer_two["current_gold_balance_grams"] == 10.0

    assert (
        output_directory / "dg_wallet_balance_analysis.csv"
    ).exists()


# --------------------------------------------------
# TEST COMPLETE ANALYTICS PIPELINE
# --------------------------------------------------

def test_run_digital_gold_analytics(
    sample_database,
    output_directory,
    monkeypatch
):

    monkeypatch.setattr(
        digital_gold_analytics,
        "DB_PATH",
        sample_database
    )

    digital_gold_analytics.run_digital_gold_analytics()

    expected_files = [
        "dg_customer_behavior.csv",
        "dg_customer_segment_analysis.csv",
        "dg_daily_trends.csv",
        "dg_investment_mode_analysis.csv",
        "dg_buy_sell_analysis.csv",
        "dg_gold_price_trends.csv",
        "dg_wallet_balance_analysis.csv"
    ]

    for filename in expected_files:

        output_file = output_directory / filename

        assert output_file.exists()

        result = pd.read_csv(output_file)

        assert len(result) > 0
