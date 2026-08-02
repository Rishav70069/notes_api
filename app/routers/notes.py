from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..oauth2 import get_current_user
from ..schemas import notes_schema

router = APIRouter(tags=["Notes"], prefix="/notes")


@router.post("/")
def create_notes(
    detalis: notes_schema.NoteCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: int = Depends(get_current_user),
):

    new_note = models.Note(owner_id=current_user.id, **detalis.model_dump())
    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note


@router.get("/", response_model=list[notes_schema.NoteResponse])
def get_notes(
    db: Annotated[Session, Depends(get_db)],
    current_user: int = Depends(get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):

    notes = (
        db.query(models.Note)
        .filter(models.Note.owner_id == current_user.id)
        .filter(models.Note.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )

    if not notes:
        return []

    return notes


@router.get("/{id}", response_model=notes_schema.NoteResponse)
def get_note(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):

    note = db.query(models.Note).filter(models.Note.id == id).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with {id} does not exist",
        )

    if note.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to see note with id {id}",
        )

    return note
