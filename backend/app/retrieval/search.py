from backend.app.db.connection import get_connection
from backend.app.ingestion.embedder import Embedder
from pgvector import Vector


class SemanticSearch:
    def __init__(self):
        self.embedder = Embedder()

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        # 1. Convert the question into an embedding.
        query_embedding = self.embedder.embed_query(query)

        # 2. Retrieve the closest vectors from PostgreSQL.
        sql = """
            SELECT
                c.id AS chunk_id,
                d.filename,
                c.content,
                c.page_number,
                c.chunk_index,
                c.metadata,
                1 - (c.embedding <=> %s) AS similarity
            FROM chunks AS c
            JOIN documents AS d
                ON d.id = c.document_id
            WHERE d.status = 'completed'
            ORDER BY c.embedding <=> %s
            LIMIT %s;
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    sql,
                    (
                        Vector(query_embedding),
                        Vector(query_embedding),
                        top_k,
                    ),
                )
                rows = cursor.fetchall()

        # 3. Convert database rows into readable Python dictionaries.
        return [
            {
                "chunk_id": row[0],
                "source": row[1],
                "text": row[2],
                "page_number": row[3],
                "chunk_index": row[4],
                "metadata": row[5],
                "similarity": float(row[6]),
            }
            for row in rows
        ]