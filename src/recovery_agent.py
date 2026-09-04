import pandas as pd
import joblib

from src.llm_reasoning import get_ai_decision

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

    # Ask the AI reasoning layer for the recovery decision
    ai_result = get_ai_decision(
        transaction,
        probability
    )

    # Safety validation: only allow approved actions
    allowed_actions = ["RETRY", "MESSAGE", "STOP"]

    if isinstance(ai_result, dict):
        action = str(ai_result.get("action", "STOP")).upper()
        reason = ai_result.get(
            "reason",
            "AI reasoning was unavailable."
        )
        source = ai_result.get(
            "source",
            "ai_reasoning"
        )
    else:
        action = "STOP"
        reason = "AI reasoning returned an invalid response."
        source = "safety_fallback"

    # Hard safety gate
    if action not in allowed_actions:
        action = "STOP"
        reason = "AI proposed an invalid action. Safety gate blocked it."
        source = "safety_gate"

    # Never allow another retry after the maximum limit
    if int(transaction["previous_attempts"]) >= 3 and action == "RETRY":
        action = "STOP"
        reason = "Retry limit reached. Further automated retries are blocked."
        source = "safety_gate"

    return {
        "transaction_id": transaction["transaction_id"],
        "amount": transaction["amount"],
        "recovery_probability": round(probability, 3),
        "recovery_percentage": round(probability * 100, 1),
        "diagnosis": diagnosis,
        "recommended_action": action,
        "decision_reason": reason,
        "decision_source": source,
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

    print("\nAI Recommended Action:")
    print(result["recommended_action"])

    print("\nAI Reasoning:")
    print(result["decision_reason"])

    print("\nDecision Source:")
    print(result["decision_source"])

    print("\nPrevious attempts:")
    print(result["previous_attempts"])

    print("====================================")