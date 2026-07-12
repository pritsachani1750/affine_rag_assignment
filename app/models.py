from sqlalchemy import Column, Integer, String, Text, ForeignKey
from database import Base, engine

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    chunk_number = Column(Integer)
    content = Column(Text)

class Selection(Base):
    __tablename__ = "selections"

    id = Column(Integer, primary_key=True, index=True)
    chunk_ids = Column(String)  # Stored as a comma-separated string (e.g., "1,2,5")

# Create the database tables automatically
Base.metadata.create_all(bind=engine)