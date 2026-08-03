from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from .. import models, utility
from ..database import get_db
from ..oauth2 import get_current_user
from ..schemas import users_schema

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

    hashed_password = utility.get_password_hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


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
