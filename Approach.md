# Architectural Approach & Technical Decisions

## 1. Chunking Strategy
The provided SOP documents are highly structured and follow a strict numbered list format. Rather than using an arbitrary character-count splitter (which often breaks sentences or concepts in half and degrades LLM comprehension), I implemented a deterministic, Regex-based chunking strategy (`r'\n?(\d+)\.\s'`). 

This parses the documents exactly by their numbered sections. This ensures that every individual chunk represents a single, logically self-contained procedural rule, making it much easier for the LLM to process and cite accurately.

## 2. Hybrid Data Model (SQLite + TinyDB)
This system handles two fundamentally different types of data, requiring a hybrid storage approach:

* **Relational (SQLite + SQLAlchemy):** Deployed for core domain entities (`Documents`, `Chunks`, and `Selections`). This data is highly structured. A chunk inherently belongs to a specific document, and SQLAlchemy enforces these relationships and schema validations perfectly.
* **NoSQL (TinyDB):** Deployed for the Q&A Session `History`. Session logs are transactional and can vary in shape (e.g., varying lengths of citation arrays). Using a lightweight JSON document store like TinyDB allows the application to quickly record audit logs without dealing with complex SQL migrations or join tables just to save conversation history.

## 3. Prompt Design for Grounding
To prevent the LLM from hallucinating or relying on its pre-trained data—a critical requirement in medical device compliance—the prompt architecture is strictly constrained:

1. **Explicit Restriction:** The system prompt explicitly instructs the model to *"Answer the user's question using ONLY the following provided chunks."*
2. **Hard Fallback:** A strict escape hatch is programmed into the prompt: *"If the answer is not contained in the chunks, state exactly: 'I do not have enough information.'"* During testing, this successfully forced the model to reject out-of-scope questions when the provided `selection_id` did not contain the relevant SOP steps, rather than fabricating a non-compliant procedure.

## 4. Tradeoffs & Future Improvements
If allocating more time to scale this system for a production environment, I would prioritize the following architectural iterations:

* **Vector Database Integration:** Currently, the system relies on the user (or a frontend client) explicitly passing an array of chunk IDs to build the context window. At scale, I would replace this manual selection process with a Vector Database (e.g., Pinecone or Milvus) and generate embeddings to enable automated semantic search retrieval across thousands of SOPs.
* **Strict SQL Normalization:** To optimize development velocity, the `Selection` model currently stores `chunk_ids` as a comma-separated string. In a true enterprise SQL deployment, I would refactor this into a proper Many-to-Many association table mapping Selections directly to Chunks to enforce strict database normalization.