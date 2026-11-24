
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.environ["DB_HOST"],
    "port": os.environ.get("DB_PORT", "5434"),
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
}

# Read questions from the original baseline database.
with psycopg.connect(dbname="knowflow", **DB_CONFIG) as source:
    with source.cursor() as cur:
        cur.execute("""
            SELECT question, expected_answer, difficulty
            FROM evaluation_questions
            ORDER BY id;
        """)
        questions = cur.fetchall()

# Insert the same questions into the experimental database.
with psycopg.connect(dbname="knowflow_250", **DB_CONFIG) as target:
    with target.cursor() as cur:
        cur.executemany("""
            INSERT INTO evaluation_questions
                (question, expected_answer, difficulty)
            VALUES (%s, %s, %s);
        """, questions)

print(f"Successfully copied {len(questions)} evaluation questions.")
