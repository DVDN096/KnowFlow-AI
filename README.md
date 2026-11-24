# KnowFlow AI – Engineering Knowledge Intelligence Platform

An open-source Retrieval-Augmented Generation (RAG) platform designed to transform engineering documents into searchable, context-aware knowledge.

KnowFlow AI enables users to upload technical PDF documents, retrieve relevant information through semantic and hybrid search, and generate context-grounded answers using a locally hosted language model.

## Key Features

- **PDF Ingestion:** Extract text and metadata from engineering PDF documents.
- **Intelligent Chunking:** Split documents into manageable text chunks with configurable chunk size and overlap.
- **Semantic Search:** Retrieve relevant document passages using vector embeddings.
- **Hybrid Retrieval:** Combine semantic similarity and PostgreSQL full-text search using Reciprocal Rank Fusion (RRF).
- **Duplicate Detection:** Identify previously uploaded documents using SHA-256 fingerprints.
- **Context-Grounded Generation:** Generate answers using retrieved document context and a locally hosted LLM.
- **Source Metadata:** Return document names, page numbers, and chunk information alongside generated answers.
- **Document Management:** Upload, list, retrieve, and delete indexed documents through REST APIs.
- **Retrieval Evaluation:** Benchmark retrieval quality using Precision@K, Recall@K, and Mean Reciprocal Rank (MRR).

## Technology Stack

| Category | Technologies |
|---|---|
| Language | Python 3.11 |
| Backend | FastAPI, Uvicorn |
| Database | PostgreSQL 16 |
| Vector Database | pgvector |
| Embeddings | Sentence Transformers |
| Embedding Model | all-MiniLM-L6-v2 |
| LLM | Qwen 2.5 3B |
| LLM Runtime | Ollama |
| PDF Processing | PyMuPDF |
| Retrieval | Semantic Search, Hybrid Search, RRF |
| Database Driver | Psycopg 3 |
| Package Management | uv |
| Containerization | Docker, Docker Compose |

## System Architecture

```text
                Engineering PDF Documents
                          |
                          v
                  Document Ingestion
                          |
                          v
                    PDF Extraction
                          |
                          v
                    Text Chunking
                          |
                          v
                 Embedding Generation
                          |
                          v
                 PostgreSQL + pgvector
                          |
              +-----------+-----------+
              |                       |
              v                       v
        Vector Search           Full-Text Search
              |                       |
              +-----------+-----------+
                          |
                          v
                 Reciprocal Rank Fusion
                          |
                          v
                  Retrieved Context
                          |
                          v
                  Ollama (Qwen 2.5)
                          |
                          v
                  Generated Answer
                          |
                          v
                  REST API Response
```

## Project Structure

```text
KnowFlow_AI/
|
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py
│   │   ├── db/
│   │   │   ├── connection.py
│   │   │   ├── repository.py
│   │   │   └── schema.sql
│   │   ├── evaluation/
│   │   │   ├── dataset.json
│   │   │   ├── copy_questions.py
│   │   │   ├── evaluate_retrieval.py
│   │   │   └── inspect_retrieval.py
│   │   ├── generation/
│   │   │   └── answer.py
│   │   ├── ingestion/
│   │   │   ├── chunker.py
│   │   │   ├── embedder.py
│   │   │   ├── parser.py
│   │   │   ├── pipeline.py
│   │   │   └── service.py
│   │   ├── retrieval/
│   │   │   ├── hybrid_search.py
│   │   │   └── search.py
│   │   └── main.py
│   └── tests/
|
├── docs/
│   └── Engineering PDF documents
|
├── evaluation/
├── frontend/
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── README.md
└── .gitignore
```

## Getting Started

### Prerequisites

Install the following:

- Python 3.11
- [uv](https://docs.astral.sh/uv/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Ollama](https://ollama.com/)

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd KnowFlow_AI
```

### 2. Set Up Python Environment

```bash
uv python install 3.11
uv sync
```

Activate the virtual environment on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
DB_HOST=127.0.0.1
DB_PORT=5434
DB_NAME=knowflow
DB_USER=your_database_user
DB_PASSWORD=your_database_password
```

Use credentials and a database name matching your PostgreSQL configuration.

### 4. Start PostgreSQL with pgvector

```bash
docker compose up -d db
```

Check the database container:

```bash
docker compose ps
```

### 5. Initialize the Database

Apply the database schema to your configured database. On Windows PowerShell, use:

```powershell
Get-Content backend/app/db/schema.sql -Raw |
docker compose exec -T db psql -U your_database_user -d your_database_name
```

Replace the placeholders with the corresponding values from your `.env`.

### 6. Set Up the Language Model

Start Ollama and download the configured model:

```bash
ollama pull qwen2.5:3b
```

The application uses `qwen2.5:3b` by default.

### 7. Start the API Server

```bash
uv run uvicorn backend.app.main:app --reload
```

The API will be available at:

- API: http://127.0.0.1:8000
- Swagger documentation: http://127.0.0.1:8000/docs
- Health endpoint: http://127.0.0.1:8000/health

## API Endpoints

The application exposes the following REST endpoints:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check API health |
| POST | `/api/v1/documents/upload` | Upload and ingest a PDF |
| GET | `/api/v1/documents` | List indexed documents |
| GET | `/api/v1/documents/{id}` | Retrieve document details |
| DELETE | `/api/v1/documents/{id}` | Delete a document and its chunks |
| POST | `/api/v1/ask` | Ask questions about indexed documents |

Interactive API testing is available through FastAPI Swagger UI at `/docs`.

## Retrieval Evaluation

KnowFlow AI includes an evaluation framework to compare semantic and hybrid retrieval strategies against a manually curated ground-truth dataset.

### Evaluation Metrics

- **Precision@K:** Fraction of retrieved chunks that are relevant.
- **Recall@K:** Fraction of relevant chunks successfully retrieved.
- **MRR@K:** Measures how highly the first relevant result is ranked.

### Benchmark Results

Evaluation was conducted using 20 questions and a top-K value of 5.

| Retrieval Method | Precision@5 | Recall@5 | MRR@5 |
|---|---:|---:|---:|
| Semantic Search 250/50 | 0.270 | 0.917 | 0.760 |
| Hybrid OR 5:1 | 0.260 | 0.892 | 0.783 |
| Hybrid OR 3:1 | 0.260 | 0.892 | 0.783 |
| Hybrid OR 1:1 | 0.250 | 0.875 | 0.833 |

### Observations

- Semantic search achieved the highest Precision@5 and Recall@5 in this evaluation.
- Hybrid OR 1:1 achieved the highest MRR@5.
- Hybrid retrieval demonstrated a different relevance-ranking trade-off compared with the semantic baseline.

The current evaluation dataset is relatively small, so these results should be interpreted as initial experimental benchmarks rather than general performance guarantees.

### Running Evaluation

```bash
uv run python -m backend.app.evaluation.evaluate_retrieval
```

The evaluation script loads questions and relevant chunk mappings from PostgreSQL and saves individual evaluation results in the `evaluation_runs` table.

## Database Design

The database uses PostgreSQL with the pgvector extension.

| Table | Purpose |
|---|---|
| `documents` | Stores document metadata, processing status, and SHA-256 fingerprints |
| `chunks` | Stores extracted text, metadata, and vector embeddings |
| `evaluation_questions` | Stores evaluation questions and expected answers |
| `evaluation_relevant_chunks` | Maps questions to ground-truth relevant chunks |
| `evaluation_runs` | Stores retrieval evaluation results |

### Database Indexing

- **HNSW index:** Accelerates vector similarity search using cosine distance.
- **GIN index:** Supports PostgreSQL full-text search.
- **B-tree indexes:** Support document lookup and chunk retrieval.
- **Unique constraints:** Prevent duplicate document chunks and duplicate document fingerprints.

## Current Limitations

- The current ingestion pipeline supports PDF documents.
- The evaluation dataset is limited in size and document diversity.
- Inline citation generation requires further validation, although source metadata is returned with answers.
- The frontend is not yet implemented.
- Retrieval performance and answer quality require further evaluation on larger engineering document collections.

## Future Improvements

- Expand support for DOCX, HTML, and other engineering document formats.
- Implement a user-friendly interactive frontend.
- Improve citation accuracy and source attribution.
- Introduce advanced reranking strategies.
- Expand the evaluation dataset and add answer-quality evaluation.
- Improve ingestion scalability and document processing workflows.

## License

This project is intended as an open-source engineering knowledge intelligence platform. A formal license can be added before public distribution.