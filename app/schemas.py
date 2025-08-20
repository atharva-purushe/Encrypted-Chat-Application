from pydantic import BaseModel
from datetime import datetime

class RegisterRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MessageResponse(BaseModel):
    id: int
    room: str
    sender: str
    content: str          # decrypted plaintext returned to clients
    created_at: datetime
