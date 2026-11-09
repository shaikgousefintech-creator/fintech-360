
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker


def generate_upi_transactions(n_records=10000, seed=42):

    # Initialize random generators
    rng = np.random.default_rng(seed)
    fake = Faker("en_IN")
    Faker.seed(seed)

    # Project root directory
    project_root = Path(__file__).resolve().parents[2]

    output_dir = project_root / "data" / "raw" / "upi"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Synthetic customer and merchant IDs
    customers = [
        f"CUST{i:05d}" for i in range(1, 5001)
    ]

    merchants = [
        f"MER{i:04d}" for i in range(1, 201)
    ]

    merchant_names = {
        merchant: fake.company()
        for merchant in merchants
    }

    # Generate transaction types
    transaction_types = rng.choice(
        ["P2P", "P2M"],
        size=n_records,
        p=[0.65, 0.35]
    )

    # Generate transaction statuses
    statuses = rng.choice(
        ["SUCCESS", "FAILED", "PENDING"],
        size=n_records,
        p=[0.94, 0.04, 0.02]
    )

    # Generate transaction timestamps
    start_date = pd.Timestamp.now() - pd.Timedelta(days=90)

    timestamps = (
        start_date
        + pd.to_timedelta(
            rng.integers(
                0, 90 * 24 * 60 * 60,
                size=n_records
            ),
            unit="s"
        )
    )

    # Generate transaction amounts
    amounts = np.round(
        np.clip(
            rng.lognormal(
                mean=5.2,
                sigma=1.0,
                size=n_records
            ),
            1,
            100000
        ),
        2
    )

    # Generate payer IDs
    payer_ids = rng.choice(customers, size=n_records)

    # Generate payee IDs
    payee_ids = [
        rng.choice(customers)
        if txn_type == "P2P"
        else rng.choice(merchants)
        for txn_type in transaction_types
    ]

    # Generate bank names
    banks = [
        "SBI",
        "HDFC",
        "ICICI",
        "AXIS",
        "KOTAK",
        "PNB"
    ]

    payer_banks = rng.choice(banks, size=n_records)
    payee_banks = rng.choice(banks, size=n_records)

    # Generate payment applications
    payment_apps = rng.choice(
        ["PhonePe", "Google Pay", "Paytm", "BHIM"],
        size=n_records
    )

    # Generate failure reasons
    failure_reasons = rng.choice(
        [
            "INSUFFICIENT_BALANCE",
            "BANK_SERVER_ERROR",
            "TRANSACTION_TIMEOUT",
            "INVALID_VPA"
        ],
        size=n_records
    )

    # Generate transaction records
    df = pd.DataFrame({

        "transaction_id": [
            f"UPI{i:08d}"
            for i in range(1, n_records + 1)
        ],

        "payer_id": payer_ids,

        "payee_id": payee_ids,

        "transaction_type": transaction_types,

        "amount": amounts,

        "currency": "INR",

        "transaction_timestamp": timestamps,

        "status": statuses,

        "payer_bank": payer_banks,

        "payee_bank": payee_banks,

        "payment_app": payment_apps,

        "failure_reason": [
            failure_reasons[i]
            if statuses[i] == "FAILED"
            else None
            for i in range(n_records)
        ],

        "merchant_name": [
            merchant_names.get(payee_ids[i])
            if transaction_types[i] == "P2M"
            else None
            for i in range(n_records)
        ]

    })

    # Save raw data
    output_file = output_dir / "upi_transactions.csv"

    df.to_csv(output_file, index=False)

    print("UPI transaction data generated successfully!")
    print(f"Total records: {len(df)}")
    print(f"Output file: {output_file}")

    print("\nTransaction status distribution:")
    print(df["status"].value_counts())

    print("\nSample records:")
    print(df.head())


if __name__ == "__main__":
    generate_upi_transactions()
