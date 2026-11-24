
from backend.app.db.connection import get_connection
from backend.app.retrieval.search import SemanticSearch
from backend.app.retrieval.hybrid_search import HybridSearch


# Evaluation configuration
TOP_K = 5


def load_dataset() -> list[dict]:
    """
    Load evaluation questions and relevant chunk IDs
    directly from PostgreSQL.
    """

    sql = """
        SELECT
            q.id,
            q.question,
            q.expected_answer,
            q.difficulty,
            COALESCE(
                ARRAY_AGG(erc.chunk_id)
                    FILTER (WHERE erc.chunk_id IS NOT NULL),
                ARRAY[]::BIGINT[]
            ) AS relevant_chunk_ids
        FROM evaluation_questions q
        LEFT JOIN evaluation_relevant_chunks erc
            ON erc.question_id = q.id
        GROUP BY q.id
        ORDER BY q.id;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()

    dataset = []

    for row in rows:
        dataset.append({
            "id": row[0],
            "question": row[1],
            "expected_answer": row[2],
            "difficulty": row[3],
            "relevant_chunk_ids": row[4],
        })

    return dataset


def calculate_metrics(retrieved_ids, relevant_ids, k=5):
    """
    Calculate Precision@K, Recall@K and MRR@K.
    """

    retrieved_ids = retrieved_ids[:k]
    relevant_ids = set(relevant_ids)

    retrieved_relevant = [
        chunk_id
        for chunk_id in retrieved_ids
        if chunk_id in relevant_ids
    ]

    precision = len(retrieved_relevant) / k

    recall = (
        len(set(retrieved_relevant)) / len(relevant_ids)
        if relevant_ids
        else 0.0
    )

    reciprocal_rank = 0.0

    for rank, chunk_id in enumerate(retrieved_ids, start=1):
        if chunk_id in relevant_ids:
            reciprocal_rank = 1 / rank
            break

    return {
        "precision": precision,
        "recall": recall,
        "mrr": reciprocal_rank,
    }


def save_evaluation_runs(records: list[tuple]):
    """
    Save individual question evaluation results
    into the evaluation_runs table.
    """

    if not records:
        return

    sql = """
        INSERT INTO evaluation_runs (
            question_id,
            retrieval_method,
            top_k,
            retrieved_chunk_ids,
            precision_score,
            recall_score,
            mrr_score
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.executemany(sql, records)


def evaluate_search(search_name, search_engine, dataset):
    """
    Evaluate one retrieval system against the dataset
    and save individual results in PostgreSQL.
    """

    print(f"\n{'=' * 65}")
    print(f"Evaluating: {search_name}")
    print("=" * 65)

    all_metrics = []
    evaluation_records = []

    for index, item in enumerate(dataset, start=1):

        question_id = item["id"]
        question = item["question"]
        relevant_ids = item["relevant_chunk_ids"]

        results = search_engine.search(
            question,
            top_k=TOP_K
        )

        retrieved_ids = [
            result["chunk_id"]
            for result in results
        ]

        metrics = calculate_metrics(
            retrieved_ids,
            relevant_ids,
            TOP_K
        )

        all_metrics.append(metrics)

        print(f"\nQuestion {index}: {question}")
        print(f"Relevant chunks: {relevant_ids}")
        print(f"Retrieved chunks: {retrieved_ids}")

        print(
            f"Precision@{TOP_K}: {metrics['precision']:.3f}"
        )
        print(
            f"Recall@{TOP_K}:    {metrics['recall']:.3f}"
        )
        print(
            f"MRR@{TOP_K}:       {metrics['mrr']:.3f}"
        )

        # Prepare database record
        evaluation_records.append((
            question_id,
            search_name,
            TOP_K,
            retrieved_ids,
            metrics["precision"],
            metrics["recall"],
            metrics["mrr"],
        ))

    # Calculate average metrics
    average_metrics = {
        metric: sum(item[metric] for item in all_metrics)
        / len(all_metrics)
        for metric in ("precision", "recall", "mrr")
    }

    # Save individual evaluation results
    save_evaluation_runs(evaluation_records)

    print(f"\n{'-' * 65}")
    print(f"AVERAGE RESULTS — {search_name}")
    print("-" * 65)

    print(
        f"Average Precision@{TOP_K}: "
        f"{average_metrics['precision']:.3f}"
    )
    print(
        f"Average Recall@{TOP_K}: "
        f"{average_metrics['recall']:.3f}"
    )
    print(
        f"Average MRR@{TOP_K}: "
        f"{average_metrics['mrr']:.3f}"
    )

    print(
        f"\nSaved {len(evaluation_records)} evaluation records "
        f"for {search_name}."
    )

    return average_metrics
def main():

    # Load evaluation dataset from PostgreSQL
    dataset = load_dataset()

    if not dataset:
        print("No evaluation questions found in the database.")
        return

    print(f"Loaded {len(dataset)} evaluation questions from PostgreSQL.")

    # Evaluate Semantic Search baseline
    semantic_search = SemanticSearch()

    semantic_results = evaluate_search(
        "Semantic Search 250/50",
        semantic_search,
        dataset
    )

    # Define Hybrid Search experiments
    experiments = [
        {
            "name": "Hybrid OR 5:1",
            "vector_weight": 5.0,
            "lexical_weight": 1.0
        },
        {
            "name": "Hybrid OR 3:1",
            "vector_weight": 3.0,
            "lexical_weight": 1.0
        },
        {
            "name": "Hybrid OR 1:1",
            "vector_weight": 1.0,
            "lexical_weight": 1.0
        }
    ]

    experiment_results = {}

    # Run each Hybrid Search experiment
    for experiment in experiments:

        print("\n" + "#" * 65)
        print(f"RRF EXPERIMENT: {experiment['name']}")
        print("#" * 65)

        hybrid_search = HybridSearch(
            vector_weight=experiment["vector_weight"],
            lexical_weight=experiment["lexical_weight"],
            rrf_k=60
        )

        results = evaluate_search(
            experiment["name"],
            hybrid_search,
            dataset
        )

        experiment_results[experiment["name"]] = results

    # Final comparison
    print("\n" + "=" * 85)
    print("FINAL RRF WEIGHT COMPARISON")
    print("=" * 85)

    headers = [
        "Retrieval Method",
        "Precision@5",
        "Recall@5",
        "MRR@5"
    ]

    print(
        f"{headers[0]:<25}"
        f"{headers[1]:<18}"
        f"{headers[2]:<18}"
        f"{headers[3]:<18}"
    )

    print("-" * 79)

    all_results = {
        "Semantic Search 250/50": semantic_results,
        **experiment_results
    }

    for name, metrics in all_results.items():
        print(
            f"{name:<25}"
            f"{metrics['precision']:<18.3f}"
            f"{metrics['recall']:<18.3f}"
            f"{metrics['mrr']:<18.3f}"
        )


if __name__ == "__main__":
    main()