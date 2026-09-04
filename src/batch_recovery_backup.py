import numpy as np
import pandas as pd

from recovery_agent import analyze_transaction


# Reproducible simulation
np.random.seed(42)

# Load transactions
data = pd.read_csv("data/transactions.csv")

results = []

print("\nStarting RecoverAI batch analysis...")
print(f"Processing {len(data)} transactions...\n")


for _, row in data.iterrows():

    transaction = row.to_dict()

    analysis = analyze_transaction(transaction)

    # Hidden synthetic probability is used ONLY to simulate
    # what would happen after the recommended intervention.
    true_probability = transaction["recovery_probability_true"]

    action = analysis["recommended_action"]

    # Simulate the outcome of the chosen intervention.
    if action == "RETRY":
        recovery_chance = true_probability

    elif action == "MESSAGE":
        # Customer messaging is slightly less effective
        # than a direct retry in this simulation.
        recovery_chance = true_probability * 0.70

    else:
        # STOP means no recovery attempt.
        recovery_chance = 0.0

    recovered = (
        np.random.random() < recovery_chance
    )

    recovered_amount = (
        transaction["amount"]
        if recovered
        else 0
    )

    results.append({
        "transaction_id": analysis["transaction_id"],
        "amount": analysis["amount"],
        "payment_method": analysis["payment_method"],
        "failure_reason": analysis["failure_reason"],
        "previous_attempts": analysis["previous_attempts"],
        "recovery_probability": analysis["recovery_probability"],
        "recommended_action": action,
        "diagnosis": analysis["diagnosis"],
        "decision_reason": analysis["decision_reason"],
        "recovered": int(recovered),
        "recovered_amount": recovered_amount,
        "simulation_note":
            "Synthetic outcome; no real payment was processed."
    })


# Results DataFrame
results_df = pd.DataFrame(results)


# Save
results_df.to_csv(
    "data/recovery_results.csv",
    index=False
)


# Metrics
total_transactions = len(results_df)

total_revenue = results_df["amount"].sum()

recovered_revenue = results_df["recovered_amount"].sum()

recovery_rate = (
    recovered_revenue / total_revenue * 100
    if total_revenue > 0
    else 0
)

recovered_transactions = (
    results_df["recovered"] == 1
).sum()

retry_count = (
    results_df["recommended_action"] == "RETRY"
).sum()

message_count = (
    results_df["recommended_action"] == "MESSAGE"
).sum()

stop_count = (
    results_df["recommended_action"] == "STOP"
).sum()

# Action success rates
retry_results = results_df[
    results_df["recommended_action"] == "RETRY"
]

message_results = results_df[
    results_df["recommended_action"] == "MESSAGE"
]

retry_success_rate = (
    retry_results["recovered"].mean() * 100
    if len(retry_results) > 0
    else 0
)

message_success_rate = (
    message_results["recovered"].mean() * 100
    if len(message_results) > 0
    else 0
)


print("========== RecoverAI Batch Results ==========")

print(f"Transactions analyzed: {total_transactions}")

print(
    f"Revenue analyzed: ₹{total_revenue:,.2f}"
)

print(
    f"Recovered transactions: {recovered_transactions}"
)

print(
    f"Recovered revenue: ₹{recovered_revenue:,.2f}"
)

print(
    f"Recovery rate: {recovery_rate:.2f}%"
)

print("\nRecommended actions:")
print(f"RETRY:   {retry_count}")
print(f"MESSAGE: {message_count}")
print(f"STOP:    {stop_count}")

print("\nIntervention performance:")
print(f"Retry success rate: {retry_success_rate:.2f}%")
print(f"Message success rate: {message_success_rate:.2f}%")

print("\nResults saved to:")
print("data/recovery_results.csv")

print("\nNOTE:")
print("All payment outcomes are synthetic simulations.")
print("No real payment was processed.")

print("============================================")