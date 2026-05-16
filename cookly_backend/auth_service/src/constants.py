from pathlib import Path

import argon2

BASE_DIR = Path(__file__).resolve().parent
PARENT_DIR = BASE_DIR.parent

IMAGES_DIR = PARENT_DIR / "images"
print(argon2.PasswordHasher().hash("password"))
