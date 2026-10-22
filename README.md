# cobol_to_java_neuro_symbolic_rag

AST-Guided Neuro-Symbolic RAG COBOL → Java Migration System with Dual Memory (Vector + Graph) and Cross-Language Differential Verification.

## Architecture & Features

- **Dual Memory Retrieval**: Combines semantic vector search with knowledge graph traversals across AST hierarchies, paragraph call graphs, and copybook dependencies.
- **Symbolic Analysis**: AST parser and dependency graph extraction for COBOL copybooks, data divisions, and procedural blocks.
- **Cross-Language Differential Verification**: Compares output and precision across COBOL execution and compiled Java code with numeric tolerance checks and automated repair loops.
- **Web Interface**: Interactive dashboard for uploading legacy COBOL corpora, inspecting AST graphs, managing migrations, and viewing benchmark reports.

## Project Structure

```
cobol_to_java_neuro_symbolic_rag/
├── backend/
│   └── app/
│       ├── config.py
│       ├── db/
│       ├── main.py
│       ├── providers/
│       ├── schemas/
│       └── services/
├── frontend/
│   └── static/
│       └── index.html
├── sample_corpus/
│   └── billing_system/
│       ├── BILLING.cob
│       ├── CUSTOMER.cpy
│       ├── DISCOUNT.cob
│       └── TAXCONFIG.cpy
├── workspace/
├── .env.example
├── .gitignore
└── README.md
```

## Setup & Running

1. **Configure Environment & Dependencies**:
   ```bash
   cp .env.example .env
   # Edit .env or ai_studio_code.env with your LLM provider and API keys if needed
   pip install -r requirements.txt
   ```
   *Note: Java (JDK 17+) should be installed and on PATH for compiling and executing generated Java classes.*

2. **Backend**:
   ```bash
   python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Frontend**:
   Open `http://localhost:8000/` in your browser (served automatically by FastAPI from `frontend/static/index.html`).

4. **Run Test Suite**:
   ```bash
   python -m unittest discover -s backend/tests
   ```
