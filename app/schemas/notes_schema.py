from datetime import datetime
from pydantic import BaseModel,EmailStr,ConfigDict

class NoteCreate(BaseModel):
    title : str
    content : str

class NoteResponse(NoteCreate):
    username : str

    class Config:
        from_attributes = True