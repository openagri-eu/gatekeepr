import re

ALLOWED_NAME_REGEX = r"^[a-zA-Z0-9\-_.,()\[\]{}@#&]*$"


def validate_email(email: str) -> str:
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if not re.match(email_regex, email):
        raise ValueError("Invalid email format")
    return email


def validate_username(username: str) -> str:
    if len(username) < 3:
        raise ValueError("Username must be at least 3 characters long")
    return username


def validate_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    return password


def validate_name(name: str) -> str:
    if name and not re.match(ALLOWED_NAME_REGEX, name):
        raise ValueError("Only alphanumeric characters and - _ , . () [] {} @ # & are allowed")
    return name

