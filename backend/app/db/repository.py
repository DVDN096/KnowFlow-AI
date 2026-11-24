
import hashlib
from pathlib import Path

from pgvector import Vector
from psycopg.types.json import Jsonb

from backend.app.db.connection import get_connection


class DuplicateDocumentError(Exception):
    def __init__(self, document_id: int):
        self.document_id = document_id
        super().__init__(
            f"Document already exists with ID {document_id}."
        )


def calculate_sha256(file_path: str | Path) -> str:
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(block)

    return sha256.hexdigest()


def save_document(
    file_path: str | Path,
    chunks: list[dict],
    original_filename: str | None = None,
) -> int:
    """Save a document and its chunks. Return the document ID."""

    pdf_path = Path(file_path)
    file_hash = calculate_sha256(pdf_path)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO documents (
                    filename, file_type, status, sha256
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (sha256) DO NOTHING
                RETURNING id
                """,
                (
                    original_filename or pdf_path.name,
                    pdf_path.suffix.lower(),
                    "processing",
                    file_hash,
                ),
            )

            result = cursor.fetchone()

            # Handle duplicate documents
            if result is None:
                cursor.execute(
                    "SELECT id FROM documents WHERE sha256 = %s",
                    (file_hash,),
                )
                existing = cursor.fetchone()

                if existing is None:
                    raise RuntimeError(
                        "Document conflict detected, but existing record was not found."
                    )

                raise DuplicateDocumentError(existing[0])

            document_id = result[0]

            for chunk in chunks:
                metadata = chunk["metadata"]

                cursor.execute(
                    """
                    INSERT INTO chunks (
                        document_id,
                        chunk_index,
                        content,
                        page_number,
                        metadata,
                        embedding
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        document_id,
                        metadata["chunk_index"],
                        chunk["text"],
                        metadata["page_number"],
                        Jsonb(metadata),
                        Vector(chunk["embedding"]),
                    ),
                )

            cursor.execute(
                """
                UPDATE documents
                SET status = %s
                WHERE id = %s
                """,
                ("completed", document_id),
            )

            return document_id


def list_documents() -> list[dict]:
    """Return all documents, newest first."""

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    d.id,
                    d.filename,
                    d.file_type,
                    d.status,
                    d.created_at,
                    COUNT(c.id) AS chunk_count
                FROM documents d
                LEFT JOIN chunks c ON c.document_id = d.id
                GROUP BY d.id
                ORDER BY d.created_at DESC
                """
            )

            rows = cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "filename": row[1],
                    "file_type": row[2],
                    "status": row[3],
                    "created_at": row[4],
                    "chunk_count": row[5],
                }
                for row in rows
            ]


def get_document(document_id: int) -> dict | None:
    """Return details of one document."""

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    d.id,
                    d.filename,
                    d.file_type,
                    d.status,
                    d.created_at,
                    COUNT(c.id) AS chunk_count
                FROM documents d
                LEFT JOIN chunks c ON c.document_id = d.id
                WHERE d.id = %s
                GROUP BY d.id
                """,
                (document_id,),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return {
                "id": row[0],
                "filename": row[1],
                "file_type": row[2],
                "status": row[3],
                "created_at": row[4],
                "chunk_count": row[5],
            }


def delete_document(document_id: int) -> bool:
    """Delete a document and its associated chunks."""

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM documents WHERE id = %s RETURNING id",
                (document_id,),
            )

            return cursor.fetchone() is not None
