from pydantic import BaseModel


class NoteCreate(BaseModel):
    title: str
    content: str


class NoteResponse(NoteCreate):
    id: int
    title: str
    content: str

    class Config:
        from_attributes = True
