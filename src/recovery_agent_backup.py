import pandas as pd
import joblib


MODEL_PATH = "models/recovery_model.pkl"

model = joblib.load(MODEL_PATH)


def predict_recovery(transaction):
    features = [
        "amount",
        "payment_method",
        "failure_reason",
        "previous_attempts",
        "customer_successful_payments",
        "customer_failed_payments",
        "hours_since_failure"
    ]

    df = pd.DataFrame([transaction])[features]

    probability = model.predict_proba(df)[0][1]

    return probability


def diagnose_failure(transaction):
    reason = transaction["failure_reason"]

    diagnoses = {
        "bank_timeout":
            "Temporary bank-side timeout. A controlled retry may recover the payment.",

        "upi_timeout":
            "Temporary UPI/network timeout. A delayed retry may recover the payment.",

        "network_error":
            "Temporary network issue. A controlled retry is appropriate.",

        "insufficient_funds":
            "Customer may not have sufficient funds. Customer notification is preferable to repeated retries.",

        "card_declined":
            "Card issuer declined the transaction. Customer may need to use another payment method.",

        "authentication_failed":
            "Authentication failed. Customer action is required before another attempt."
    }

    return diagnoses.get(
        reason,
        "Unknown payment failure. Manual review recommended."
    )


def choose_action(transaction, probability):

    attempts = transaction["previous_attempts"]
    reason = transaction["failure_reason"]

    # Safety rule
    if attempts >= 3:
        return "STOP", "Maximum retry limit reached."

    # Customer-action failures
    if reason == "authentication_failed":
        return "MESSAGE", "Customer authentication is required."

    if reason == "insufficient_funds":
        return "MESSAGE", "Customer should resolve the balance before another payment attempt."

    # Temporary technical failures
    technical_failures = [
        "bank_timeout",
        "upi_timeout",
        "network_error"
    ]

    if reason in technical_failures:

        if probability >= 0.40:
            return "RETRY", "Temporary technical failure with reasonable recovery probability."

        if probability >= 0.25:
            return "MESSAGE", "Technical failure has moderate recovery potential; customer notification is safer."

        return "STOP", "Very low recovery probability."

    # Card declines
    if reason == "card_declined":

        if probability >= 0.60:
            return "MESSAGE", "Customer should retry using the same or another payment method."

        return "STOP", "Low recovery probability for the current payment attempt."

    # General fallback
    if probability >= 0.75:
        return "RETRY", "High predicted recovery probability."

    if probability >= 0.45:
        return "MESSAGE", "Moderate recovery probability."

    return "STOP", "Low recovery probability."


def analyze_transaction(transaction):

    probability = predict_recovery(transaction)

    diagnosis = diagnose_failure(transaction)

    action, reason = choose_action(
        transaction,
        probability
    )

    return {
        "transaction_id": transaction["transaction_id"],
        "amount": transaction["amount"],
        "recovery_probability": round(probability, 3),
        "recovery_percentage": round(probability * 100, 1),
        "diagnosis": diagnosis,
        "recommended_action": action,
        "decision_reason": reason,
        "previous_attempts": transaction["previous_attempts"],
        "failure_reason": transaction["failure_reason"],
        "payment_method": transaction["payment_method"]
    }


if __name__ == "__main__":

    data = pd.read_csv("data/transactions.csv")

    transaction = data.iloc[0].to_dict()

    result = analyze_transaction(transaction)

    print("\n========== RecoverAI Agent ==========")
    print(f"Transaction: {result['transaction_id']}")
    print(f"Amount: ₹{result['amount']:,.2f}")
    print(f"Recovery probability: {result['recovery_percentage']}%")

    print("\nAI Diagnosis:")
    print(result["diagnosis"])

    print("\nRecommended Action:")
    print(result["recommended_action"])

    print("\nReason:")
    print(result["decision_reason"])

    print("\nPrevious attempts:")
    print(result["previous_attempts"])

    print("====================================")