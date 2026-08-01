from fastapi import APIRouter,Depends
from .. schemas import notes_schema
from typing import Annotated
from sqlalchemy.orm import Session
from .. database import get_db
from .. Oauth2 import get_current_user
from .. import models


router = APIRouter(tags=['Notes'],prefix="/notes")

@router.post("/")
def create_notes(detalis : notes_schema.NoteCreate,db :Annotated[Session,Depends(get_db)],current_user : int = Depends(get_current_user)):

    new_note = models.Note(owner_id = current_user.id,**detalis.model_dump())
    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note
