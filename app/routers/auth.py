from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models, oauth2, utility
from ..database import get_db
from ..schemas import users_schema

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=users_schema.Token)
def get_user(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    user = (
        db.query(models.User)
        .filter(
            or_(
                models.User.email == user_credentials.username,
                models.User.username == user_credentials.username,
            )
        )
        .first()
    )

    if not user:
        utility.verify_password_or_dummy(user_credentials.password, utility.DUMMY_HASH)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
        )

    if not utility.verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in",
        )

    access_token = oauth2.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token}
