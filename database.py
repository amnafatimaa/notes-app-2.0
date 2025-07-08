from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base
import os


load_dotenv()


engine = create_engine(os.getenv("DATABASE_URL"), echo=True)
Base = declarative_base()

class NoteDB(Base):
    __tablename__ = "notes"
    id = Column(String, primary_key=True)  
    title = Column(String)
    content = Column(String)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
