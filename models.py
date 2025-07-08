from pydantic import BaseModel

class Note(BaseModel):
    id: str
    title: str
    content: str

class NoteCreate(BaseModel):
    title: str
    content: str
