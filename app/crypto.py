import logging
from cryptography.fernet import Fernet
from .config import FERNET_SECRET

if not FERNET_SECRET:
    raise ValueError("FERNET_SECRET not set in .env")

fernet = Fernet(FERNET_SECRET.encode())

def encrypt_text(text: str) -> str:
    return fernet.encrypt(text.encode()).decode()

def decrypt_text(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
