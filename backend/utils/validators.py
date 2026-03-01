"""
Insight IS — Additional Validators
"""

import re


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Returns (is_valid, error_message)."""
    if len(password) < 8:
        return False, "Минимум 8 символов"
    if not re.search(r"[A-Z]", password):
        return False, "Нужна хотя бы одна заглавная буква"
    if not re.search(r"\d", password):
        return False, "Нужна хотя бы одна цифра"
    return True, ""