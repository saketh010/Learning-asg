from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.deps import get_db
from backend import models, auth

router = APIRouter()


@router.post("/signup")
def signup(username: str, password: str, db: Session = Depends(get_db)):
    role = "admin" if username == "admin" else "user"

    user = models.User(
        username=username,
        password=auth.hash_password(password),
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "user_id": user.id,
        "role": role,
        "token": auth.create_token(user.id)
    }


@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(username=username).first()

    if not user or not auth.verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "user_id": user.id,
        "role": user.role,
        "token": auth.create_token(user.id)
    }
