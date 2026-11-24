
-- =========================================================
-- KnowFlow AI - Database Schema
-- PostgreSQL 16 + pgvector
-- =========================================================

CREATE EXTENSION IF NOT EXISTS vector;

-- ---------------------------------------------------------
-- Documents
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sha256 CHAR(64)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_documents_sha256
    ON documents(sha256);

-- ---------------------------------------------------------
-- Document chunks
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL
        REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL CHECK (chunk_index >= 0),
    content TEXT NOT NULL,
    page_number INTEGER,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    embedding VECTOR(384),
    search_vector TSVECTOR
        GENERATED ALWAYS AS (
            to_tsvector('english', content)
        ) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_document_chunk
        UNIQUE (document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_chunks_document_id
    ON chunks(document_id);

CREATE INDEX IF NOT EXISTS idx_chunks_embedding
    ON chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_chunks_search_vector
    ON chunks USING gin(search_vector);

-- ---------------------------------------------------------
-- Evaluation questions
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS evaluation_questions (
    id BIGSERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    expected_answer TEXT,
    difficulty VARCHAR(20) DEFAULT 'medium',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------------
-- Ground-truth relevant chunks
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS evaluation_relevant_chunks (
    question_id BIGINT NOT NULL
        REFERENCES evaluation_questions(id) ON DELETE CASCADE,
    chunk_id BIGINT NOT NULL
        REFERENCES chunks(id) ON DELETE CASCADE,

    PRIMARY KEY (question_id, chunk_id)
);

-- ---------------------------------------------------------
-- Retrieval evaluation runs
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS evaluation_runs (
    id BIGSERIAL PRIMARY KEY,
    question_id BIGINT
        REFERENCES evaluation_questions(id) ON DELETE CASCADE,
    retrieval_method VARCHAR(50) NOT NULL,
    top_k INTEGER NOT NULL,
    retrieved_chunk_ids BIGINT[] NOT NULL,
    precision_score DOUBLE PRECISION,
    recall_score DOUBLE PRECISION,
    mrr_score DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
