import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.hash import bcrypt
from datetime import datetime, timedelta

from .db import get_db
from .models import User
from .schemas import RegisterRequest, TokenResponse
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES  # ✅ from config

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)