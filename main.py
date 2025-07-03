from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from datetime import datetime
import uuid

app = FastAPI()


def init_db():
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()

# Pydantic models
class Note(BaseModel):
    id: str
    title: str
    content: str
    created_at: Optional[str] = None  # Added to match SQLite schema

class NoteCreate(BaseModel):
    title: str
    content: str

# function to convert database row to Note model
def row_to_note(row):
    return Note(id=row[0], title=row[1], content=row[2], created_at=row[3])

@app.get("/notes", response_model=List[Note])
def get_notes():
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content, created_at FROM notes")
    rows = cursor.fetchall()
    conn.close()
    return [row_to_note(row) for row in rows]

@app.post("/notes", response_model=Note)
def create_note(note: NoteCreate):
    note_id = str(uuid.uuid4())
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO notes (id, title, content) VALUES (?, ?, ?)",
            (note_id, note.title, note.content)
        )
        conn.commit()
        cursor.execute("SELECT id, title, content, created_at FROM notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()
        if row:
            return row_to_note(row)
        raise HTTPException(status_code=500, detail="Failed to create note")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: str):
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, title, content, created_at FROM notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()
        if row:
            return row_to_note(row)
        raise HTTPException(status_code=404, detail="Note not found")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: str, updated_note: NoteCreate):
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE notes SET title = ?, content = ? WHERE id = ?",
            (updated_note.title, updated_note.content, note_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Note not found")
        cursor.execute("SELECT id, title, content, created_at FROM notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()
        return row_to_note(row)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.delete("/notes/{note_id}")
def delete_note(note_id: str):
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Note not found")
        return {"message": "Note deleted"}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()