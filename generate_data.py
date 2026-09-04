import numpy as np
import pandas as pd

np.random.seed(42)

N = 1000

failure_reasons = [
    "bank_timeout",
    "insufficient_funds",
    "card_declined",
    "upi_timeout",
    "network_error",
    "authentication_failed"
]

payment_methods = ["UPI", "Card", "NetBanking", "Wallet"]

data = pd.DataFrame({
    "transaction_id": [f"TXN{100000 + i}" for i in range(N)],
    "amount": np.round(np.random.uniform(199, 15000, N), 2),
    "payment_method": np.random.choice(
        payment_methods, N, p=[0.45, 0.30, 0.15, 0.10]
    ),
    "failure_reason": np.random.choice(
        failure_reasons, N
    ),
    "previous_attempts": np.random.choice(
        [0, 1, 2, 3], N, p=[0.45, 0.30, 0.18, 0.07]
    ),
    "customer_successful_payments": np.random.randint(
        0, 20, N
    ),
    "customer_failed_payments": np.random.randint(
        0, 6, N
    ),
    "hours_since_failure": np.round(
        np.random.uniform(0.1, 72, N), 1
    )
})

# Base recovery probability
probability = np.full(N, 0.55)

# Failure-specific effects
probability += np.where(
    data["failure_reason"].isin(
        ["bank_timeout", "upi_timeout", "network_error"]
    ), 0.20, 0
)

probability -= np.where(
    data["failure_reason"] == "insufficient_funds",
    0.20, 0
)

probability -= np.where(
    data["failure_reason"] == "authentication_failed",
    0.25, 0
)

# Customer history
probability += np.clip(
    data["customer_successful_payments"] * 0.015,
    0,
    0.20
)

probability -= np.clip(
    data["customer_failed_payments"] * 0.025,
    0,
    0.15
)

# Previous attempts reduce recovery probability
probability -= data["previous_attempts"] * 0.08

# Older failures are slightly harder to recover
probability -= np.clip(
    data["hours_since_failure"] / 200,
    0,
    0.20
)

# Amount has a small effect
probability -= np.where(
    data["amount"] > 10000,
    0.05,
    0
)

probability = np.clip(probability, 0.05, 0.95)

data["recovery_probability_true"] = np.round(
    probability, 3
)

data["recovered"] = np.random.binomial(
    1,
    probability
)

data["recovery_status"] = np.where(
    data["recovered"] == 1,
    "Recovered",
    "Unrecovered"
)

data.to_csv(
    "data/transactions.csv",
    index=False
)

print("Dataset created successfully!")
print(f"Total transactions: {len(data)}")
print(f"Total failed revenue: ₹{data['amount'].sum():,.2f}")
print(
    f"Recovered revenue: "
    f"₹{data.loc[data['recovered'] == 1, 'amount'].sum():,.2f}"
)
print(
    f"Recovery rate: "
    f"{data['recovered'].mean() * 100:.2f}%"
)
print("Saved to: data/transactions.csv")