import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.hash import bcrypt
from datetime import datetime, timedelta

from .db import get_db
from .models import User
from .schemas import RegisterRequest, TokenResponse

SECRET_KEY = "supersecretkey"  # (replace with env var in production)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ✅ Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@router.post(
    "/register",
    response_model=TokenResponse,
    summary="Register a new user",
    description="Create a new account with a **username and password**. The password is securely hashed using bcrypt. Returns a JWT token for authentication.",
)
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    user = User(
        username=request.username,
        hashed_password=bcrypt.hash(request.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"🆕 User registered: {user.username}")

    token_data = {"sub": user.username, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return TokenResponse(access_token=token)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and get a JWT",
    description="Authenticate with **username and password**. If valid, returns a JWT token for use in chat and history APIs.",
)
def login_user(request: RegisterRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not bcrypt.verify(request.password, user.hashed_password):
        logger.warning(f"❌ Failed login attempt for username: {request.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    logger.info(f"✅ User logged in: {user.username}")

    token_data = {"sub": user.username, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return TokenResponse(access_token=token)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        logger.error("🚨 Invalid or expired JWT token")
        raise HTTPException(status_code=401, detail="Invalid token")
