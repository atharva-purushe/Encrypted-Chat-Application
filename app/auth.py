import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.hash import bcrypt

from .db import get_db
from .models import User
from .schemas import RegisterRequest, TokenResponse
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# -------------------------------
# 🔑 JWT Helpers
# -------------------------------
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Generate JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# -------------------------------
# 👤 Register Endpoint
# -------------------------------
@router.post("/register", response_model=TokenResponse, summary="Register new user")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user and return JWT token."""
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash the password
    hashed_pw = bcrypt.hash(request.password)
    new_user = User(username=request.username, password_hash=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create token
    access_token = create_access_token({"sub": new_user.username})
    logger.info(f"🆕 User registered: {new_user.username}")
    return TokenResponse(access_token=access_token)


# -------------------------------
# 🔑 Login Endpoint
# -------------------------------
@router.post("/login", response_model=TokenResponse, summary="Login user")
def login(request: RegisterRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not bcrypt.verify(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Create token
    access_token = create_access_token({"sub": user.username})
    logger.info(f"✅ User logged in: {user.username}")
    return TokenResponse(access_token=access_token)
