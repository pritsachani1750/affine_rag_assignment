import os
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

from .database import SessionLocal, history_db
from .models import Document, Chunk, Selection

load_dotenv()

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

app = FastAPI(title="SOP RAG API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class SelectionRequest(BaseModel):
    chunk_ids: List[int]

class QARequest(BaseModel):
    selection_id: int
    question: str


@app.get("/documents")
def get_documents(db: Session = Depends(get_db)):
    """List all available documents."""
    docs = db.query(Document).all()
    return [{"id": d.id, "filename": d.filename} for d in docs]

@app.get("/documents/{doc_id}/chunks")
def get_chunks(doc_id: int, db: Session = Depends(get_db)):
    """List all chunks for a specific document."""
    chunks = db.query(Chunk).filter(Chunk.document_id == doc_id).all()
    if not chunks:
        raise HTTPException(status_code=404, detail="Document not found or has no chunks")
    return [{"id": c.id, "chunk_number": c.chunk_number, "content": c.content} for c in chunks]

@app.post("/selections")
def create_selection(req: SelectionRequest, db: Session = Depends(get_db)):
    """Save a user's selection of chunks."""
    chunk_ids_str = ",".join(map(str, req.chunk_ids))
    new_selection = Selection(chunk_ids=chunk_ids_str)
    
    db.add(new_selection)
    db.commit()
    db.refresh(new_selection)
    
    return {"selection_id": new_selection.id, "chunk_ids": req.chunk_ids}


@app.post("/grounded-qa")
def grounded_qa(req: QARequest, db: Session = Depends(get_db)):
    """Answer a question based strictly on the selected chunks."""
    selection = db.query(Selection).filter(Selection.id == req.selection_id).first()
    if not selection:
        raise HTTPException(status_code=404, detail="Selection not found")
    
    chunk_ids = [int(cid) for cid in selection.chunk_ids.split(",")]
    chunks = db.query(Chunk).filter(Chunk.id.in_(chunk_ids)).all()
    selected_text = "\n\n".join([f"Chunk ID {c.id}: {c.content}" for c in chunks])
    
 
    prompt = f"""You are a helpful medical device compliance assistant. 
    Answer the user's question using ONLY the following provided chunks. 
    If the answer is not contained in the chunks, state exactly: 'I do not have enough information.'
    
    Selected Content:
    {selected_text}
    
    Question: {req.question}
    """
    
    try:
        response = model.generate_content(prompt)
        final_answer = response.text
    except Exception as e:
        final_answer = f"Error calling LLM: {str(e)}"
    

    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": req.question,
        "answer": final_answer,
        "selection_id": req.selection_id,
        "citations": chunk_ids
    }
    history_db.insert(history_entry)
    
    return {
        "answer": final_answer,
        "citations": chunk_ids
    }

@app.get("/history")
def get_history():
    """Retrieve past Q&A sessions."""
    return history_db.all()