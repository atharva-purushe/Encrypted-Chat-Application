import os
from cryptography.fernet import Fernet

# Use a single app-wide key (env var preferred in real deployments)
FERNET_SECRET = os.getenv("FERNET_SECRET")

if FERNET_SECRET is None:
    # For local dev: generate a volatile key if not provided.
    # In production, ALWAYS set FERNET_SECRET and keep it safe.
    FERNET_SECRET = Fernet.generate_key().decode("utf-8")

fernet = Fernet(FERNET_SECRET.encode("utf-8"))

def encrypt_text(plaintext: str) -> bytes:
    return fernet.encrypt(plaintext.encode("utf-8"))

def decrypt_text(ciphertext: bytes) -> str:
    return fernet.decrypt(ciphertext).decode("utf-8")
