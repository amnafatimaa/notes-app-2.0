import uuid
from fastapi import HTTPException, Depends
from typing import List
from models import Note, NoteCreate
from database import get_db, NoteDB
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends

router = APIRouter()

@router.get("/notes", response_model=List[Note])
def get_notes(db: Session = Depends(get_db)):
    notes = db.query(NoteDB).all()
    return [Note(id=note.id, title=note.title, content=note.content) for note in notes]

@router.post("/notes", response_model=Note)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    new_note = NoteDB(id=str(uuid.uuid4()), title=note.title, content=note.content)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return Note(id=new_note.id, title=new_note.title, content=new_note.content)

@router.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: str, db: Session = Depends(get_db)):
    note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if note:
        return Note(id=note.id, title=note.title, content=note.content)
    raise HTTPException(status_code=404, detail="Note not found")

@router.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: str, updated_note: NoteCreate, db: Session = Depends(get_db)):
    note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if note:
        note.title = updated_note.title
        note.content = updated_note.content
        db.commit()
        db.refresh(note)
        return Note(id=note.id, title=note.title, content=note.content)
    raise HTTPException(status_code=404, detail="Note not found")

@router.delete("/notes/{note_id}")
def delete_note(note_id: str, db: Session = Depends(get_db)):
    note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if note:
        db.delete(note)
        db.commit()
        return {"message": "Note deleted"}
    raise HTTPException(status_code=404, detail="Note not found")
