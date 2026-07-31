from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Token, UserLogin, UserOut, UserRegister
from app.services.auth_service import authenticate_user, create_access_token, register_user

router = APIRouter(prefix="/auth", tags=["commands:auth"])


@router.post("/register", status_code=201)
def register(request: UserRegister, db: Session = Depends(get_db)) -> UserOut:
    try:
        return register_user(db, request.email, request.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login(request: UserLogin, db: Session = Depends(get_db)) -> Token:
    user = authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(str(user.id))
    return Token(access_token=token)