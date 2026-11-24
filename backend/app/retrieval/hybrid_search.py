from backend.app.db.connection import get_connection
from backend.app.ingestion.embedder import Embedder
from pgvector import Vector


class HybridSearch:
    def __init__(
        self,
        vector_weight: float = 1.0,
        lexical_weight: float = 1.0,
        rrf_k: int = 60
        ):
        if vector_weight < 0 or lexical_weight < 0:
            raise ValueError("RRF weights cannot be negative.")

        if vector_weight == 0 and lexical_weight == 0:
            raise ValueError("At least one RRF weight must be positive.")

        if rrf_k < 0:
            raise ValueError("RRF constant cannot be negative.")

        self.embedder = Embedder()
        self.vector_weight = vector_weight
        self.lexical_weight = lexical_weight
        self.rrf_k = rrf_k

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        query_embedding = self.embedder.embed_query(query)
        candidate_k = max(top_k * 5, 20)

        sql = """
            WITH query_embedding AS (
                SELECT %s::vector AS embedding
            ),
            query_text AS (
                SELECT
                    to_tsquery(
                        'english',
                        array_to_string(
                            tsvector_to_array(
                                to_tsvector('english', %s)
                            ),
                            ' | '
                        )
                    ) AS tsquery
            ),
            vector_results AS (
                SELECT
                    c.id,
                    1 - (c.embedding <=> qe.embedding) AS similarity,
                    ROW_NUMBER() OVER (
                        ORDER BY c.embedding <=> qe.embedding
                    ) AS rank
                FROM chunks c
                JOIN documents d ON d.id = c.document_id
                CROSS JOIN query_embedding qe
                WHERE d.status = 'completed'
                ORDER BY c.embedding <=> qe.embedding
                LIMIT %s
            ),
            lexical_results AS (
                SELECT
                    c.id,
                    ROW_NUMBER() OVER (
                        ORDER BY ts_rank_cd(
                            c.search_vector, qt.tsquery
                        ) DESC
                    ) AS rank
                FROM chunks c
                JOIN documents d ON d.id = c.document_id
                CROSS JOIN query_text qt
                WHERE d.status = 'completed'
                  AND c.search_vector @@ qt.tsquery
                ORDER BY ts_rank_cd(
                    c.search_vector, qt.tsquery
                ) DESC
                LIMIT %s
            ),
            combined AS (
                SELECT
                    id,
                    %s / (%s + rank) AS rrf_score
                FROM vector_results

                UNION ALL

                SELECT
                    id,
                    %s / (%s + rank) AS rrf_score
                FROM lexical_results
            ),
            fused AS (
                SELECT id, SUM(rrf_score) AS rrf_score
                FROM combined
                GROUP BY id
            )
            SELECT
                c.id AS chunk_id,
                d.filename,
                c.content,
                c.page_number,
                c.chunk_index,
                c.metadata,
                f.rrf_score,
                vr.similarity,
                vr.rank AS vector_rank,
                lr.rank AS lexical_rank
            FROM fused f
            JOIN chunks c ON c.id = f.id
            JOIN documents d ON d.id = c.document_id
            LEFT JOIN vector_results vr ON vr.id = c.id
            LEFT JOIN lexical_results lr ON lr.id = c.id
            ORDER BY f.rrf_score DESC
            LIMIT %s;
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    sql,
                    (
                        Vector(query_embedding),
                        query,
                        candidate_k,
                        candidate_k,
                        self.vector_weight,
                        self.rrf_k,
                        self.lexical_weight,
                        self.rrf_k,
                        top_k,
                    ),
                )
                rows = cursor.fetchall()

        return [
            {
                "chunk_id": row[0],
                "source": row[1],
                "text": row[2],
                "page_number": row[3],
                "chunk_index": row[4],
                "metadata": row[5],
                "rrf_score": float(row[6]),
                "similarity": (
                    float(row[7]) if row[7] is not None else None
                ),
                "vector_rank": row[8],
                "lexical_rank": row[9],
            }
            for row in rows
        ]