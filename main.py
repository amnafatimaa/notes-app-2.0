from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI()

notes = []

class Note(BaseModel):
    id: str
    title: str
    content: str
    
class NoteCreate(BaseModel):
    title: str
    content: str
    
@app.get("/notes", response_model=List[Note])
def get_notes():
    return notes

@app.post("/notes", response_model=Note)
def create_note(note: NoteCreate):
    new_note = Note(id=str(uuid.uuid4()), title=note.title, content=note.content)
    notes.append(new_note)
    return new_note

@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: str):
    for note in notes:
        if note.id == note_id:
            return note
    raise HTTPException(status_code=404, detail="Note not found")

@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: str, updated_note: NoteCreate):
    for note in notes:
        if note.id == note_id:
            note.title = updated_note.title
            note.content = updated_note.content
            return note
    raise HTTPException(status_code=404, detail="Note not found")

@app.delete("/notes/{note_id}")
def delete_note(note_id: str):
    for index, note in enumerate(notes):
        if note.id == note_id:
            notes.pop(index)
            return {"message": "Note deleted"}
    raise HTTPException(status_code=404, detail="Note not found")