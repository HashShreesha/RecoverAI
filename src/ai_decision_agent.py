"""
RecoverAI - AI Decision Agent

Combines ML recovery probability with explainable decision logic.
The agent is bounded by safety rules and can only choose:
RETRY, MESSAGE, or STOP.
"""

from typing import Dict, Any


ALLOWED_ACTIONS = {"RETRY", "MESSAGE", "STOP"}


def diagnose_failure(row: Dict[str, Any]) -> str:
    """Generate an explainable diagnosis from transaction signals."""

    failure_type = str(row.get("failure_type", "")).lower()
    payment_method = str(row.get("payment_method", "")).lower()
    attempts = int(row.get("previous_attempts", 0))

    if "timeout" in failure_type or "network" in failure_type:
        return (
            "Temporary technical failure detected. "
            "A controlled retry may recover the payment."
        )

    if "insufficient" in failure_type or "fund" in failure_type:
        return (
            "Customer-action failure detected. "
            "Messaging the customer is safer than automatically retrying."
        )

    if "declined" in failure_type:
        return (
            "Payment was declined. "
            "Customer intervention is likely required."
        )

    if "expired" in failure_type:
        return (
            "Payment attempt has expired. "
            "A customer reminder is appropriate."
        )

    if attempts >= 3:
        return (
            "Multiple previous attempts detected. "
            "Further automatic retries should be stopped."
        )

    return (
        f"Payment failure detected for {payment_method or 'unknown'} payment method. "
        "Recovery probability is used to select the safest intervention."
    )


def decide_action(
    recovery_probability: float,
    previous_attempts: int,
    failure_type: str,
) -> str:
    """
    Apply hard safety guardrails.

    The decision is deliberately bounded:
    the agent can never choose an action outside the allowlist.
    """

    failure = failure_type.lower()

    # Hard stopping rule
    if previous_attempts >= 3:
        return "STOP"

    # Customer-action failures should not be automatically retried
    customer_action_failures = [
        "insufficient",
        "fund",
        "declined",
        "expired",
    ]

    if any(item in failure for item in customer_action_failures):
        return "MESSAGE"

    # High-confidence temporary failures
    if recovery_probability >= 0.45:
        return "RETRY"

    # Medium probability -> customer communication
    if recovery_probability >= 0.25:
        return "MESSAGE"

    return "STOP"


def generate_reason(
    action: str,
    recovery_probability: float,
    previous_attempts: int,
    failure_type: str,
) -> str:

    if action == "RETRY":
        return (
            f"Recovery probability is {recovery_probability:.1%}. "
            "The failure appears temporary and the retry limit has not been reached."
        )

    if action == "MESSAGE":
        return (
            f"Recovery probability is {recovery_probability:.1%}. "
            "Customer intervention is preferred over another automatic payment attempt."
        )

    if previous_attempts >= 3:
        return (
            "Automatic recovery stopped because the maximum retry limit "
            "has already been reached."
        )

    return (
        f"Recovery probability is {recovery_probability:.1%} and the failure "
        "does not justify another automatic intervention."
    )


def run_agent(row: Dict[str, Any]) -> Dict[str, Any]:
    """Run the complete RecoverAI decision pipeline."""

    probability = float(row.get("recovery_probability", 0))
    previous_attempts = int(row.get("previous_attempts", 0))
    failure_type = str(row.get("failure_type", ""))

    diagnosis = diagnose_failure(row)

    action = decide_action(
        probability,
        previous_attempts,
        failure_type,
    )

    # Final safety validation
    if action not in ALLOWED_ACTIONS:
        action = "STOP"

    reason = generate_reason(
        action,
        probability,
        previous_attempts,
        failure_type,
    )

    return {
        "transaction_id": row.get("transaction_id", "UNKNOWN"),
        "recovery_probability": probability,
        "diagnosis": diagnosis,
        "recommended_action": action,
        "decision_reason": reason,
        "previous_attempts": previous_attempts,
        "allowed_actions": ", ".join(sorted(ALLOWED_ACTIONS)),
    }


if __name__ == "__main__":

    demo_transaction = {
        "transaction_id": "TXN100000",
        "recovery_probability": 0.446,
        "previous_attempts": 2,
        "failure_type": "Temporary UPI/network timeout",
        "payment_method": "UPI",
    }

    result = run_agent(demo_transaction)

    print("\nRecoverAI - AI Decision Agent")
    print("-" * 45)

    for key, value in result.items():
        print(f"{key}: {value}")