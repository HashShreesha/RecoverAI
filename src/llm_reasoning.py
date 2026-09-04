import os
import json

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


ALLOWED_ACTIONS = ["RETRY", "MESSAGE", "STOP"]


def deterministic_fallback(transaction, recovery_probability):
    """
    Safe fallback when an LLM is unavailable.
    The fallback never performs a payment action.
    """

    failure = str(transaction.get("failure_reason", "")).lower()
    attempts = int(transaction.get("previous_attempts", 0))

    # Hard safety rule: never retry beyond the limit.
    if attempts >= 3:
        action = "STOP"
        reason = "Retry limit reached. Further automated attempts are blocked."

    # Customer-action failures should use messaging.
    elif "authentication" in failure or "insufficient" in failure:
        action = "MESSAGE"
        reason = "Customer action is required before another payment attempt."

    # High recovery probability + technical failure.
    elif recovery_probability >= 0.60:
        action = "RETRY"
        reason = "Temporary technical failure with a strong recovery probability."

    # Moderate probability: ask the customer to act.
    elif recovery_probability >= 0.35:
        action = "MESSAGE"
        reason = "Recovery probability is moderate; customer intervention is safer."

    else:
        action = "STOP"
        reason = "Recovery probability is low, so another automated attempt is not justified."

    return {
        "action": action,
        "reason": reason,
        "source": "deterministic_fallback"
    }


def get_ai_decision(transaction, recovery_probability):
    """
    Ask the LLM to recommend a recovery action.

    Safety design:
    - LLM can only choose RETRY, MESSAGE, or STOP.
    - Maximum retry attempts are enforced outside the LLM.
    - If the LLM is unavailable, deterministic fallback is used.
    """

    attempts = int(transaction.get("previous_attempts", 0))

    # Hard safety gate BEFORE calling the LLM.
    if attempts >= 3:
        return {
            "action": "STOP",
            "reason": "Retry limit reached. Further automated attempts are blocked.",
            "source": "safety_gate"
        }

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or OpenAI is None:
        return deterministic_fallback(
            transaction,
            recovery_probability
        )

    try:
        client = OpenAI(api_key=api_key)

        prompt = f"""
You are RecoverAI, a revenue recovery decision agent.

Your task is to select ONE bounded intervention for a failed payment.

Allowed actions:
- RETRY: appropriate for temporary technical/payment network failures.
- MESSAGE: appropriate when customer action is required.
- STOP: appropriate when recovery probability is low or another automated attempt is unsafe.

Transaction:
{json.dumps(transaction, default=str)}

ML recovery probability:
{recovery_probability:.3f}

Previous attempts:
{attempts}

Safety rules:
1. Never recommend more than 3 total previous attempts.
2. Never invent transaction information.
3. Never perform or authorize an actual payment.
4. Choose only RETRY, MESSAGE, or STOP.
5. Give a short, explainable reason.

Return ONLY valid JSON in this format:
{{
    "action": "RETRY",
    "reason": "short explanation"
}}
"""

        response = client.responses.create(
            model="gpt-5-mini",
            input=prompt
        )

        text = response.output_text.strip()
        decision = json.loads(text)

        action = str(decision.get("action", "STOP")).upper()
        reason = str(decision.get("reason", "No explanation provided."))

        # Final safety validation.
        if action not in ALLOWED_ACTIONS:
            return deterministic_fallback(
                transaction,
                recovery_probability
            )

        return {
            "action": action,
            "reason": reason,
            "source": "llm"
        }

    except Exception as error:
        # Graceful failure: never let the AI layer break recovery.
        fallback = deterministic_fallback(
            transaction,
            recovery_probability
        )

        fallback["source"] = "fallback_after_llm_error"
        fallback["error"] = str(error)

        return fallback