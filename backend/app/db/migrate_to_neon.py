
import os

import psycopg
from dotenv import load_dotenv
from psycopg.types.json import Jsonb

from backend.app.db.connection import get_connection


load_dotenv()

TABLES = [
    "documents",
    "chunks",
    "evaluation_questions",
    "evaluation_relevant_chunks",
    "evaluation_runs",
]

COLUMNS = {
    "documents": [
        "id", "filename", "file_type", "status", "created_at", "sha256"
    ],
    "chunks": [
        "id", "document_id", "chunk_index", "content",
        "page_number", "metadata", "embedding", "created_at"
    ],
    "evaluation_questions": [
        "id", "question", "expected_answer", "difficulty", "created_at"
    ],
    "evaluation_relevant_chunks": [
        "question_id", "chunk_id"
    ],
    "evaluation_runs": [
        "id", "question_id", "retrieval_method", "top_k",
        "retrieved_chunk_ids", "precision_score", "recall_score",
        "mrr_score", "created_at"
    ],
}


def main():
    local = psycopg.connect(
        host=os.environ["DB_HOST"],
        port=os.getenv("DB_PORT", "5434"),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )

    neon = get_connection()

    try:
        # Check that all destination tables are empty.
        with neon.cursor() as cursor:
            for table in TABLES:
                count = cursor.execute(
                    f"SELECT COUNT(*) FROM {table}"
                ).fetchone()[0]

                if count != 0:
                    raise RuntimeError(
                        f"Neon table '{table}' is not empty. "
                        "Migration stopped."
                    )

        # End the preflight read transaction before migration.
        neon.commit()

        # Read source data before starting the destination transaction.
        source_data = {}

        for table in TABLES:
            columns = COLUMNS[table]
            column_list = ", ".join(columns)

            rows = local.execute(
                f"SELECT {column_list} FROM {table}"
            ).fetchall()

            source_data[table] = rows

        # Migrate everything in one atomic transaction.
        with neon.transaction():
            for table in TABLES:
                columns = COLUMNS[table]
                column_list = ", ".join(columns)
                placeholders = ", ".join(["%s"] * len(columns))

                rows = source_data[table]

                if not rows:
                    print(f"{table}: 0 records")
                    continue

                prepared_rows = []

                for row in rows:
                    values = list(row)

                    if table == "chunks":
                        metadata_index = columns.index("metadata")
                        values[metadata_index] = Jsonb(
                            values[metadata_index]
                        )

                    prepared_rows.append(tuple(values))

                with neon.cursor() as cursor:
                    cursor.executemany(
                        f"""
                        INSERT INTO {table} ({column_list})
                        VALUES ({placeholders})
                        """,
                        prepared_rows,
                    )

                print(
                    f"{table}: {len(rows)} records migrated"
                )

            # Synchronize auto-increment sequences.
            for table in [
                "documents",
                "chunks",
                "evaluation_questions",
                "evaluation_runs",
            ]:
                with neon.cursor() as cursor:
                    cursor.execute(
                        f"""
                        SELECT setval(
                            pg_get_serial_sequence('{table}', 'id'),
                            COALESCE(MAX(id), 1),
                            MAX(id) IS NOT NULL
                        )
                        FROM {table}
                        """
                    )

        # Verify destination counts after commit.
        print("\nVerifying Neon records...")

        for table in TABLES:
            expected = len(source_data[table])

            actual = neon.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            if actual != expected:
                raise RuntimeError(
                    f"Verification failed for {table}: "
                    f"expected {expected}, found {actual}"
                )

            print(f"{table}: {actual}/{expected} verified")

        print("\nMigration completed and committed successfully!")

    finally:
        local.close()
        neon.close()


if __name__ == "__main__":
    main()
