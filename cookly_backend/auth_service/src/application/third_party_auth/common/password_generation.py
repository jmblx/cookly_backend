import random
import string


def generate_random_password(length: int = 12):
    """Генерирует полностью случайный пароль"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = "".join(random.choices(chars, k=length))
        if any(c.isdigit() for c in password) and any(
            c in "!@#$%^&*" for c in password
        ):
            return password
