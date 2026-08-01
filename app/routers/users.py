from .. import models,utility
from fastapi import FastAPI , Response , status , HTTPException ,Depends,APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from ..schemas import users_schema


router = APIRouter(
    prefix="/users",
    tags=['users']
)

@router.post("/create",status_code=status.HTTP_201_CREATED,response_model=users_schema.UserResponse)
def create_user(user : users_schema.UserCreate,db : Session = Depends(get_db)):

    if db.query(models.User).filter(models.User.username == user.username).first() != None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Username already exists")

    if db.query(models.User).filter(models.User.email == user.email).first() != None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Email already exists")

    hashed_password = utility.get_password_hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user