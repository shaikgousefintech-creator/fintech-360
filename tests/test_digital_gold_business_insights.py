
import sqlite3

import pandas as pd
import pytest

from src.analytics import digital_gold_business_insights as business


# --------------------------------------------------
# 1. SAMPLE DATABASE
# --------------------------------------------------

@pytest.fixture
def sample_database(tmp_path):

    db_path = tmp_path / "digital_gold_test.db"

    with sqlite3.connect(db_path) as conn:

        # CUSTOMER PERFORMANCE MART

        pd.DataFrame({
            "customer_id": ["C001", "C002", "C003"],
            "customer_name": [
                "Aarav Sharma",
                "Isha Kumar",
                "Rohan Mehta"
            ],
            "customer_segment": [
                "REGULAR",
                "PREMIUM",
                "REGULAR"
            ],
            "city": [
                "Mumbai",
                "Bengaluru",
                "Mumbai"
            ],
            "total_transactions": [3, 2, 2],
            "successful_transactions": [2, 2, 1],
            "failed_transactions": [1, 0, 1],
            "pending_transactions": [0, 0, 0],
            "total_buy_amount": [20000.00, 30000.00, 10000.00],
            "total_sell_amount": [5000.00, 10000.00, 2000.00],
            "total_gold_bought_grams": [10.0, 15.0, 5.0],
            "total_gold_sold_grams": [2.0, 5.0, 1.0]
        }).to_sql(
            "mart_dg_customer_performance",
            conn,
            index=False
        )

        # CUSTOMER SEGMENT PERFORMANCE MART

        pd.DataFrame({
            "customer_segment": ["REGULAR", "PREMIUM"],
            "total_customers": [2, 1],
            "total_transactions": [5, 2],
            "successful_transactions": [3, 2],
            "failed_transactions": [2, 0],
            "pending_transactions": [0, 0],
            "total_buy_amount": [30000.00, 30000.00],
            "total_sell_amount": [7000.00, 10000.00],
            "success_rate_percentage": [60.0, 100.0]
        }).to_sql(
            "mart_dg_customer_segment_performance",
            conn,
            index=False
        )

        # TRANSACTION TYPE PERFORMANCE MART

        pd.DataFrame({
            "transaction_type": ["BUY", "SELL"],
            "total_transactions": [4, 3],
            "successful_transactions": [3, 2],
            "failed_transactions": [1, 1],
            "pending_transactions": [0, 0],
            "total_successful_amount": [
                60000.00,
                17000.00
            ],
            "total_successful_gold_quantity_grams": [
                30.0,
                8.0
            ],
            "success_rate_percentage": [75.0, 66.67]
        }).to_sql(
            "mart_dg_transaction_type_performance",
            conn,
            index=False
        )

        # DIGITAL GOLD TRANSACTIONS

        pd.DataFrame({
            "transaction_id": [
                "T001",
                "T002",
                "T003",
                "T004",
                "T005",
                "T006"
            ],
            "customer_id": [
                "C001",
                "C001",
                "C002",
                "C002",
                "C003",
                "C003"
            ],
            "transaction_date": [
                "2026-01-01",
                "2026-01-01",
                "2026-01-02",
                "2026-02-01",
                "2026-02-01",
                "2026-02-02"
            ],
            "transaction_type": [
                "BUY",
                "SELL",
                "BUY",
                "SELL",
                "BUY",
                "BUY"
            ],
            "investment_mode": [
                "UPI",
                "CARD",
                "CARD",
                "WALLET",
                "UPI",
                "WALLET"
            ],
            "transaction_status": [
                "SUCCESS",
                "SUCCESS",
                "SUCCESS",
                "FAILED",
                "SUCCESS",
                "PENDING"
            ],
            "amount": [
                10000.00,
                5000.00,
                30000.00,
                4000.00,
                10000.00,
                3000.00
            ],
            "gold_quantity_grams": [
                5.0,
                2.0,
                15.0,
                2.0,
                5.0,
                1.5
            ]
        }).to_sql(
            "dg_transactions",
            conn,
            index=False
        )

    return db_path


# --------------------------------------------------
# 2. OUTPUT DIRECTORY FIXTURE
# --------------------------------------------------

@pytest.fixture
def output_directory(tmp_path, monkeypatch):

    output_dir = tmp_path / "business_insights"
    output_dir.mkdir()

    monkeypatch.setattr(
        business,
        "OUTPUT_DIR",
        output_dir
    )

    return output_dir


# --------------------------------------------------
# 3. TOP CUSTOMER INSIGHTS TESTS
# --------------------------------------------------

def test_generate_top_customers(
    sample_database,
    output_directory
):

    with sqlite3.connect(sample_database) as conn:

        result = business.generate_top_customers(conn)

    assert len(result) == 3

    assert list(result.columns) == [
        "customer_id",
        "customer_name",
        "customer_segment",
        "city",
        "total_transactions",
        "successful_transactions",
        "failed_transactions",
        "pending_transactions",
        "total_buy_amount",
        "total_sell_amount",
        "total_gold_bought_grams",
        "total_gold_sold_grams",
        "net_gold_accumulated_grams",
        "success_rate_percentage"
    ]

    # Isha has the highest net gold accumulation:
    # 15 grams bought - 5 grams sold = 10 grams.

    assert result.iloc[0]["customer_id"] == "C002"

    assert result.iloc[0][
        "net_gold_accumulated_grams"
    ] == 10.0

    assert (
        output_directory / "dg_top_customers.csv"
    ).exists()


def test_top_customer_net_gold_calculation(
    sample_database,
    output_directory
):

    with sqlite3.connect(sample_database) as conn:

        result = business.generate_top_customers(conn)

    aarav = result.loc[
        result["customer_id"] == "C001"
    ].iloc[0]

    assert aarav["total_gold_bought_grams"] == 10.0
    assert aarav["total_gold_sold_grams"] == 2.0

    assert aarav[
        "net_gold_accumulated_grams"
    ] == 8.0


# --------------------------------------------------
# 4. CUSTOMER SEGMENT INSIGHTS TESTS
# --------------------------------------------------

def test_generate_segment_insights(
    sample_database,
    output_directory
):

    with sqlite3.connect(sample_database) as conn:

        result = business.generate_segment_insights(conn)

    assert len(result) == 2

    premium = result.loc[
        result["customer_segment"] == "PREMIUM"
    ].iloc[0]

    assert premium["total_customers"] == 1
    assert premium["total_transactions"] == 2
    assert premium["successful_transactions"] == 2

    assert premium["net_purchase_amount"] == 20000.00

    assert premium["total_gold_bought_grams"] == 15.0
    assert premium["total_gold_sold_grams"] == 5.0

    assert premium[
        "net_gold_accumulated_grams"
    ] == 10.0

    assert (
        output_directory / "dg_customer_segment_insights.csv"
    ).exists()


# --------------------------------------------------
# 5. CITY-WISE INSIGHTS TESTS
# --------------------------------------------------

def test_generate_city_insights(
    sample_database,
    output_directory
):

    with sqlite3.connect(sample_database) as conn:

        result = business.generate_city_insights(conn)

    assert len(result) == 2

    mumbai = result.loc[
        result["city"] == "Mumbai"
    ].iloc[0]

    assert mumbai["total_customers"] == 2
    assert mumbai["total_transactions"] == 5
    assert mumbai["successful_transactions"] == 3
    assert mumbai["failed_transactions"] == 2

    assert mumbai["total_buy_amount"] == 30000.00
    assert mumbai["total_sell_amount"] == 7000.00

    assert mumbai[
        "total_gold_bought_grams"
    ] == 15.0

    assert mumbai[
        "total_gold_sold_grams"
    ] == 3.0

    assert mumbai[
        "net_gold_accumulated_grams"
    ] == 12.0

    assert (
        output_directory / "dg_city_wise_insights.csv"
    ).exists()


# --------------------------------------------------
# 6. BUY AND SELL INSIGHTS TESTS
# --------------------------------------------------

def test_generate_transaction_type_insights(
    sample_database,
    output_directory
):

    with sqlite3.connect(sample_database) as conn:

        result = (
            business.generate_transaction_type_insights(conn)
        )

    assert len(result) == 2

    buy = result.loc[
        result["transaction_type"] == "BUY"
    ].iloc[0]

    sell = result.loc[
        result["transaction_type"] == "SELL"
    ].iloc[0]

    assert buy["total_transactions"] == 4
    assert buy["successful_transactions"] == 3
    assert buy["failed_transactions"] == 1

    assert buy["total_successful_amount"] == 60000.00

    assert (
        buy["total_successful_gold_quantity_grams"]
        == 30.0
    )

    assert sell["total_transactions"] == 3
    assert sell["successful_transactions"] == 2
    assert sell["failed_transactions"] == 1

    assert sell["total_successful_amount"] == 17000.00

    assert (
        output_directory / "dg_transaction_type_insights.csv"
    ).exists()


# --------------------------------------------------
# 7. INVESTMENT MODE INSIGHTS TESTS
# --------------------------------------------------

def test_generate_investment_mode_insights(
    sample_database,
    output_directory
):

    with sqlite3.connect(sample_database) as conn:

        result = (
            business.generate_investment_mode_insights(conn)
        )

    assert len(result) == 3

    upi = result.loc[
        result["investment_mode"] == "UPI"
    ].iloc[0]

    assert upi["total_transactions"] == 2
    assert upi["successful_transactions"] == 2
    assert upi["failed_transactions"] == 0
    assert upi["pending_transactions"] == 0

    assert (
        upi["successful_transaction_amount"]
        == 20000.00
    )

    assert (
        upi["successful_gold_quantity_grams"]
        == 10.0
    )

    assert (
        upi["average_successful_transaction_amount"]
        == 10000.00
    )

    assert upi["success_rate_percentage"] == 100.0

    assert (
        output_directory / "dg_investment_mode_insights.csv"
    ).exists()


# --------------------------------------------------
# 8. MONTHLY GOLD FLOW INSIGHTS TESTS
# --------------------------------------------------

def test_generate_monthly_flow_insights(
    sample_database,
    output_directory
):

    with sqlite3.connect(sample_database) as conn:

        result = business.generate_monthly_flow_insights(conn)

    assert len(result) == 2

    january = result.loc[
        result["transaction_month"] == "2026-01"
    ].iloc[0]

    february = result.loc[
        result["transaction_month"] == "2026-02"
    ].iloc[0]

    # JANUARY

    assert january["total_transactions"] == 3
    assert january["successful_transactions"] == 3
    assert january["failed_transactions"] == 0
    assert january["pending_transactions"] == 0

    assert january["successful_buy_amount"] == 40000.00
    assert january["successful_sell_amount"] == 5000.00

    assert (
        january["net_successful_transaction_amount"]
        == 35000.00
    )

    assert (
        january["net_gold_accumulated_grams"]
        == 18.0
    )

    # FEBRUARY

    assert february["total_transactions"] == 3
    assert february["successful_transactions"] == 1
    assert february["failed_transactions"] == 1
    assert february["pending_transactions"] == 1

    assert february["successful_buy_amount"] == 10000.00
    assert february["successful_sell_amount"] == 0.00

    assert (
        february["net_successful_transaction_amount"]
        == 10000.00
    )

    assert (
        february["net_gold_accumulated_grams"]
        == 5.0
    )

    assert (
        output_directory / "dg_monthly_gold_flows.csv"
    ).exists()


# --------------------------------------------------
# 9. BUSINESS FINDINGS TESTS
# --------------------------------------------------

def test_print_business_findings(
    capsys
):

    customers = pd.DataFrame({
        "customer_name": ["Isha Kumar"],
        "customer_segment": ["PREMIUM"],
        "net_gold_accumulated_grams": [10.0]
    })

    segments = pd.DataFrame({
        "customer_segment": ["PREMIUM"],
        "net_gold_accumulated_grams": [10.0]
    })

    cities = pd.DataFrame({
        "city": ["Mumbai"],
        "net_gold_accumulated_grams": [12.0]
    })

    transaction_types = pd.DataFrame({
        "transaction_type": ["BUY"],
        "total_successful_amount": [60000.00]
    })

    modes = pd.DataFrame({
        "investment_mode": ["UPI"],
        "successful_transaction_amount": [20000.00]
    })

    monthly = pd.DataFrame({
        "transaction_month": ["2026-01"],
        "successful_buy_amount": [40000.00]
    })

    business.print_business_findings(
        customers,
        segments,
        cities,
        transaction_types,
        modes,
        monthly
    )

    captured = capsys.readouterr()

    assert "Isha Kumar" in captured.out
    assert "PREMIUM" in captured.out
    assert "Mumbai" in captured.out
    assert "BUY" in captured.out
    assert "UPI" in captured.out
    assert "2026-01" in captured.out

    assert "synthetic transaction activity" in captured.out
    assert "does not represent investment returns" in captured.out


# --------------------------------------------------
# 10. DATABASE CONNECTION TEST
# --------------------------------------------------

def test_get_connection_missing_database(
    tmp_path,
    monkeypatch
):

    missing_database = (
        tmp_path / "missing_database.db"
    )

    monkeypatch.setattr(
        business,
        "DB_PATH",
        missing_database
    )

    with pytest.raises(
        FileNotFoundError,
        match="Database not found"
    ):
        business.get_connection()


# --------------------------------------------------
# 11. COMPLETE BUSINESS INSIGHTS PIPELINE TEST
# --------------------------------------------------

def test_run_business_insights(
    sample_database,
    output_directory,
    monkeypatch,
    capsys
):

    monkeypatch.setattr(
        business,
        "DB_PATH",
        sample_database
    )

    business.run_business_insights()

    expected_files = [
        "dg_top_customers.csv",
        "dg_customer_segment_insights.csv",
        "dg_city_wise_insights.csv",
        "dg_transaction_type_insights.csv",
        "dg_investment_mode_insights.csv",
        "dg_monthly_gold_flows.csv"
    ]

    for filename in expected_files:

        output_file = output_directory / filename

        assert output_file.exists()

        result = pd.read_csv(output_file)

        assert len(result) > 0

    captured = capsys.readouterr()

    assert "DIGITAL GOLD BUSINESS INSIGHTS COMPLETED!" in captured.out
    assert "Datasets generated: 6" in captured.out
