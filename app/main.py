from fastapi import FastAPI

from app.routers import notes
from .routers import users,auth


app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(notes.router)

@app.get("/")
async def root():
    return {"message": "Welcome to notes_api"}
