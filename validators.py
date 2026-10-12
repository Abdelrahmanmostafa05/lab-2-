def validate_register(name, email, password, confirm):
    errors = {}
    if name == "":
        errors["name"] = "Name is required"
    elif len(name) > 100:
        errors["name"] = "Name is too long (100 characters at most)"

    if email == "":
        errors["email"] = "Email is required"
    elif len(email) > 255:
        errors["email"] = "Email is too long (255 characters at most)"

    if password.strip() == "":
        errors["password"] = "Password is required"
    elif len(password.encode("utf-8")) > 72:
        errors["password"] = "Password is too long (72 characters at most)"

    if confirm.strip() == "":
        errors["confirm_password"] = "Confirm password is required"
    elif password != confirm:
        errors["confirm_password"] = "Passwords do not match"
    return errors


def validate_login(email, password):
    errors = {}
    if email == "":
        errors["email"] = "Email is required"
    if password.strip() == "":
        errors["password"] = "Password is required"
    return errors


def validate_title(title):
    """Returns an error message, or None if the title is fine."""
    if title == "":
        return "Title is required"
    if len(title) > 200:
        return "Title is too long (200 characters at most)"
    return None