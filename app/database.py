import os
from sqlalchemy import create_all, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from tinydb import TinyDB

# 1. SQLITE (Relational DB for Documents, Chunks, and Selections)
DATABASE_URL = "sqlite:///./rag_database.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. TINYDB (NoSQL DB for flexible Q&A session logs)
history_db = TinyDB("history_db.json")