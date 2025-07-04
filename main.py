from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid

app = FastAPI()

# Set up SQLAlchemy
engine = create_engine("sqlite:///notes.db", echo=True) 
Base = declarative_base()

# Define SQLAlchemy Note model
class NoteDB(Base):
    __tablename__ = "notes"
    id = Column(String, primary_key=True)  
    title = Column(String)
    content = Column(String)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pydantic models
class Note(BaseModel):
    id: str
    title: str
    content: str

class NoteCreate(BaseModel):
    title: str
    content: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API endpoints
@app.get("/")
def read_root():
    return {"message": "Welcome to the Notes API"}

@app.get("/notes", response_model=List[Note])
def get_notes(db=Depends(get_db)):
    notes = db.query(NoteDB).all()  # Fetch all notes from the database
    return [Note(id=note.id, title=note.title, content=note.content) for note in notes]

@app.post("/notes", response_model=Note)
def create_note(note: NoteCreate, db=Depends(get_db)):
    new_note = NoteDB(id=str(uuid.uuid4()), title=note.title, content=note.content)
    db.add(new_note)
    db.commit()  
    notes = db.query(NoteDB).all()  
    return [Note(id=str(note.id), title=str(note.title), content=str(note.content)) for note in notes]

@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: str, db=Depends(get_db)):
    note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if note:
        return Note(id=note.id, title=note.title, content=note.content)
    raise HTTPException(status_code=404, detail="Note not found")

@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: str, updated_note: NoteCreate, db=Depends(get_db)):
    note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if note:
        note.title = updated_note.title
        note.content = updated_note.content
        db.commit()
        db.refresh(note)
        return Note(id=note.id, title=note.title, content=note.content)
    raise HTTPException(status_code=404, detail="Note not found")

@app.delete("/notes/{note_id}")
def delete_note(note_id: str, db=Depends(get_db)):
    note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if note:
        db.delete(note)
        db.commit()
        return {"message": "Note deleted"}
    raise HTTPException(status_code=404, detail="Note not found")