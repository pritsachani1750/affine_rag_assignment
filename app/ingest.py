import os
import re
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
from models import Document, Chunk


Base.metadata.create_all(bind=engine)

def load_data():
    db: Session = SessionLocal()

    data_dir = "data"
    
    if not os.path.exists(data_dir):
        print(f"Error: Could not find the '{data_dir}' folder. Make sure you run this from the root directory.")
        return

    for filename in os.listdir(data_dir):
        if not filename.endswith(".txt"):
            continue
            
        file_path = os.path.join(data_dir, filename)

        if db.query(Document).filter(Document.filename == filename).first():
            print(f"Skipping {filename}, already processed.")
            continue

        new_doc = Document(filename=filename)
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        raw_chunks = re.split(r'\n?(\d+)\.\s', content)
        
     
        for i in range(1, len(raw_chunks), 2):
            try:
                chunk_num = int(raw_chunks[i])
                text_content = raw_chunks[i+1].strip()
                
                if text_content:
                    new_chunk = Chunk(
                        document_id=new_doc.id,
                        chunk_number=chunk_num,
                        content=text_content
                    )
                    db.add(new_chunk)
            except ValueError as e:
                print(f"Could not parse chunk: {e}")

        db.commit()
        print(f"Successfully processed: {filename}")
        
    db.close()

if __name__ == "__main__":
    load_data()