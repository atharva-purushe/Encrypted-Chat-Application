import os
from dotenv import load_dotenv

# Load from .env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chat.db")

FERNET_SECRET = os.getenv("FERNET_SECRET")

