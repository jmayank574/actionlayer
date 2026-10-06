"""Fail fast, with the real reason, when the model API is unusable.

Found the hard way: with the account's credit balance at zero, every call in a
paid eval failed -- but the tagger swallows errors into "FAILED" rows, so the
run looked like 180 mysterious tagging failures and then crashed scoring an
empty result. One 1-token call up front turns that into a clear message.
"""

import os


def api_error() -> str | None:
    """None if the API is usable, otherwise a human-readable reason."""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return "ANTHROPIC_API_KEY is not set."
    try:
        import anthropic
        anthropic.Anthropic(api_key=key).messages.create(
            model="claude-sonnet-4-6", max_tokens=1, messages=[{"role": "user", "content": "hi"}],
        )
    except Exception as e:  # any failure here means the paid evals can't run
        msg = str(e)
        if "credit balance" in msg.lower():
            return "Anthropic credit balance is too low -- add credit at console.anthropic.com (Plans & Billing)."
        return f"{type(e).__name__}: {msg[:300]}"
    return None
