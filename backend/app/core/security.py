"""Security utilities and anonymous identifier generation."""

import re
import secrets
import string


def generate_learner_id(prefix: str = "mq") -> str:
    """
    Generate a friendly, random, non-identifiable learner token.
    Example: mq_k7x9m2
    Does NOT collect or encode real names, emails, dates of birth, or device IDs.
    """
    alphabet = string.ascii_lowercase + string.digits
    token = "".join(secrets.choice(alphabet) for _ in range(8))
    return f"{prefix}_{token}"


def validate_learner_id(learner_id: str) -> bool:
    """Validate format of an anonymous learner ID."""
    return bool(re.match(r"^[a-zA-Z0-9_\-]{4,64}$", learner_id))


def generate_session_id() -> str:
    """Generate a random unique session token."""
    return f"sess_{secrets.token_hex(8)}"
