import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from .. import models, utility
from ..database import get_db
from ..oauth2 import get_current_user
from ..schemas import users_schema
from ..utility import send_otp_email

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=users_schema.UserResponse,
)
def create_user(user: users_schema.UserCreate, db: Annotated[Session, Depends(get_db)]):

    if (
        db.query(models.User).filter(models.User.username == user.username).first()
        != None
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already exists"
        )

    if db.query(models.User).filter(models.User.email == user.email).first() != None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
        )

    otp = str(secrets.randbelow(900000) + 100000)
    otp_hash = utility.get_password_hash(otp)

    hashed_password = utility.get_password_hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.model_dump())

    new_user.otp_hash = otp_hash
    new_user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    send_otp_email(user.email, otp)

    return new_user


@router.post("/verify-email")
def verify_email(
    data: users_schema.VerifyEmail, db: Annotated[Session, Depends(get_db)]
):
    user = db.query(models.User).filter(models.User.email == data.email).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified"
        )

    if user.otp_expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired"
        )

    if not utility.verify_password(data.otp, user.otp_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP"
        )

    user.is_verified = True
    user.otp_hash = None
    user.otp_expires_at = None

    db.commit()

    return {"message": "Email verified successfully"}


@router.post("/resend-otp")
def resend_otp(data: users_schema.ResendOTP, db: Annotated[Session, Depends(get_db)]):
    user = db.query(models.User).filter(models.User.email == data.email).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already verified"
        )

    otp = str(secrets.randbelow(900000) + 100000)
    otp_hash = utility.get_password_hash(otp)

    user.otp_hash = otp_hash
    user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    db.commit()

    send_otp_email(user.email, otp)

    return {"message": "A new OTP has been sent"}


@router.delete("/{id}")
def delete_user(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):

    user_query = db.query(models.User).filter(models.User.id == id)
    user = db.query(models.User).filter(models.User.id == id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found"
        )

    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to delete user with id {id}",
        )

    user_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/forgot-password")
def forgot_password(
    data: users_schema.ForgotPassword, db: Annotated[Session, Depends(get_db)]
):
    user = db.query(models.User).filter(models.User.email == data.email).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    otp = str(secrets.randbelow(900000) + 100000)
    otp_hash = utility.get_password_hash(otp)

    user.otp_hash = otp_hash
    user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    db.commit()

    send_otp_email(user.email, otp)

    return {"message": "Password reset OTP sent"}


@router.post("/reset-password")
def reset_password(
    data: users_schema.ResetPassword, db: Annotated[Session, Depends(get_db)]
):
    user = db.query(models.User).filter(models.User.email == data.email).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user.otp_hash is None or user.otp_expires_at is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No password reset request found",
        )

    if user.otp_expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired"
        )

    if not utility.verify_password(data.otp, user.otp_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP"
        )

    user.password = utility.get_password_hash(data.new_password)

    user.otp_hash = None
    user.otp_expires_at = None

    db.commit()

    return {"message": "Password reset successfully"}
