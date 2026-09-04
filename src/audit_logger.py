"""
RecoverAI - Audit Logger

Records every recovery decision so that the system is
traceable, explainable, and easy to review.
"""

import csv
import os
from datetime import datetime


AUDIT_FILE = "data/audit_log.csv"


def log_decision(
    transaction_id,
    recovery_probability,
    diagnosis,
    recommended_action,
    decision_reason,
    previous_attempts,
    outcome,
    recovered_amount,
):
    """Store one recovery decision in the audit trail."""

    os.makedirs("data", exist_ok=True)

    file_exists = os.path.exists(AUDIT_FILE)

    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "transaction_id": transaction_id,
        "recovery_probability": round(float(recovery_probability), 4),
        "diagnosis": diagnosis,
        "recommended_action": recommended_action,
        "decision_reason": decision_reason,
        "previous_attempts": previous_attempts,
        "outcome": outcome,
        "recovered_amount": round(float(recovered_amount), 2),
    }

    with open(
        AUDIT_FILE,
        "a",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=record.keys(),
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(record)

    return record


if __name__ == "__main__":

    test_record = log_decision(
        transaction_id="TEST001",
        recovery_probability=0.446,
        diagnosis="Temporary technical failure detected.",
        recommended_action="MESSAGE",
        decision_reason="Customer intervention is preferred.",
        previous_attempts=2,
        outcome="Message queued",
        recovered_amount=0,
    )

    print("\nRecoverAI - Audit Logger")
    print("-" * 40)
    print("Audit record created successfully.")
    print(f"Transaction: {test_record['transaction_id']}")
    print(f"Action: {test_record['recommended_action']}")
    print(f"Saved to: {AUDIT_FILE}")