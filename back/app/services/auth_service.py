import uuid
from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import SECRET_KEY
from app.db_models import UserRow
from app.models import UserOut

security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Decode and verify the JWT from the Authorization header, return the user id.
    Raises 401 if the token is missing, invalid, or expired."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 24  # 24h


def hash_password(plain_password: str) -> str:
    """Turn a plaintext password into an irreversible hash (e.g. $2b$12$...).
    This is one-way: even with direct DB access, the original password
    cannot be recovered from the stored hash."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plaintext password (typed at login) against the stored hash,
    without ever reversing/decrypting the hash itself."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str) -> str:
    """Generate a JWT: a cryptographically signed string containing the
    user id ('sub') and an expiration date ('exp'). Anyone can read its
    content, but no one can forge or alter it without knowing SECRET_KEY."""
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def register_user(db: Session, email: str, password: str) -> UserOut:
    """Create a new user: enforce email uniqueness, hash the password
    before storing it, never keep the plaintext password anywhere."""
    existing = db.query(UserRow).filter(UserRow.email == email).first()
    if existing:
        raise ValueError("Email already registered")

    user = UserRow(
        id=uuid.uuid4(),
        email=email,
        hashed_password=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut(id=str(user.id), email=user.email)


def authenticate_user(db: Session, email: str, password: str) -> UserRow | None:
    """Look up the user by email and verify the given password against
    the stored hash. Returns None if either the email or password is wrong
    (deliberately not distinguishing which one, to avoid leaking which
    emails are registered)."""
    user = db.query(UserRow).filter(UserRow.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user