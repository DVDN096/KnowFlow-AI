
import asyncio
import csv
import json
import statistics
from pathlib import Path

import ollama

from backend.app.evaluation.evaluate_retrieval import load_dataset
from backend.app.generation.answer import AnswerService


# =========================================================
# Configuration
# =========================================================

TOP_K = 5
BATCH_SIZE = 5

GENERATION_MODEL = "qwen2.5:3b"
JUDGE_MODEL = "qwen2.5:3b"

OUTPUT_DIR = Path("backend/app/evaluation/results")
OUTPUT_FILE = OUTPUT_DIR / "generation_evaluation.csv"


# =========================================================
# LLM-as-Judge
# =========================================================

def evaluate_answer(
    question: str,
    expected_answer: str,
    generated_answer: str,
    retrieved_context: str,
) -> dict:

    prompt = f"""
Evaluate this RAG-generated answer on three criteria.

QUESTION:
{question}

EXPECTED ANSWER:
{expected_answer}

RETRIEVED CONTEXT:
{retrieved_context}

GENERATED ANSWER:
{generated_answer}

Evaluate independently:

1. correctness:
Does the answer communicate the information in the expected answer?

2. faithfulness:
Are the answer's claims supported by the retrieved context?
Do not use the expected answer as evidence.

3. relevancy:
Does the answer directly address the question?

Score each criterion from 1 to 5:
1 = Very poor
2 = Poor
3 = Partially satisfactory
4 = Good
5 = Excellent

Return only JSON in this format:

{{
    "correctness": {{"score": 1, "reason": "Explanation"}},
    "faithfulness": {{"score": 1, "reason": "Explanation"}},
    "relevancy": {{"score": 1, "reason": "Explanation"}}
}}
"""

    response = ollama.chat(
        model=JUDGE_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an objective RAG evaluation judge. "
                    "Return valid JSON only."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        format="json",
        options={"temperature": 0},
    )

    result = json.loads(response["message"]["content"])

    for metric in ("correctness", "faithfulness", "relevancy"):

        score = float(result[metric]["score"])

        if not 1 <= score <= 5:
            raise ValueError(f"Invalid {metric} score: {score}")

        result[metric]["score"] = score

    return result


# =========================================================
# Context Preparation
# =========================================================

def prepare_context(results: list[dict]) -> str:

    context_parts = []

    for result in results:
        context_parts.append(
            f"[Source: {result['source']}, "
            f"page {result['page_number']}]\n"
            f"{result['text']}"
        )

    return "\n\n---\n\n".join(context_parts)


# =========================================================
# Abstention Detection
# =========================================================

def is_abstention(answer: str, sources: list) -> bool:

    if not sources:
        return True

    phrases = [
        "couldn't find sufficient relevant information",
        "couldn't find relevant information",
        "unavailable in the provided documents",
        "not available in the provided documents",
        "insufficient information",
    ]

    return any(
        phrase in answer.lower()
        for phrase in phrases
    )


# =========================================================
# Resume Support
# =========================================================

def load_completed_ids() -> set:

    if not OUTPUT_FILE.exists():
        return set()

    with OUTPUT_FILE.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        reader = csv.DictReader(file)

        return {
            int(row["question_id"])
            for row in reader
            if row.get("question_id")
        }


# =========================================================
# Save Each Result Immediately
# =========================================================

FIELDNAMES = [
    "question_id",
    "question",
    "expected_answer",
    "generated_answer",
    "correctness",
    "correctness_reason",
    "faithfulness",
    "faithfulness_reason",
    "relevancy",
    "relevancy_reason",
    "generation_seconds",
    "abstention",
    "sources",
]


def save_result(record: dict):

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    file_exists = OUTPUT_FILE.exists()

    with OUTPUT_FILE.open(
        "a",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDNAMES,
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(record)

        # Ensure the row is written before moving on.
        file.flush()


# =========================================================
# Main Evaluation
# =========================================================

async def main():

    print("\n" + "=" * 70)
    print("KNOWFLOW AI - ANSWER GENERATION EVALUATION")
    print("=" * 70)

    dataset = load_dataset()

    dataset = [
        item for item in dataset
        if item["expected_answer"]
        and item["expected_answer"].strip()
    ]

    if not dataset:
        print("No valid evaluation questions found.")
        return

    completed_ids = load_completed_ids()

    remaining_questions = [
        item for item in dataset
        if item["id"] not in completed_ids
    ]

    if not remaining_questions:
        print("\nAll evaluation questions are already completed.")
        print(f"Results: {OUTPUT_FILE}")
        return

    batch = remaining_questions[:BATCH_SIZE]

    print(f"\nTotal questions: {len(dataset)}")
    print(f"Previously completed: {len(completed_ids)}")
    print(f"Remaining questions: {len(remaining_questions)}")
    print(f"Questions in this run: {len(batch)}")

    print(f"\nGeneration model: {GENERATION_MODEL}")
    print(f"Judge model: {JUDGE_MODEL}")

    answer_service = AnswerService(
        model=GENERATION_MODEL
    )

    correctness_scores = []
    faithfulness_scores = []
    relevancy_scores = []
    generation_times = []

    successful_answers = 0
    abstentions = 0
    failed_evaluations = 0

    for index, item in enumerate(batch, start=1):

        question_id = item["id"]
        question = item["question"]
        expected_answer = item["expected_answer"]

        print("\n" + "-" * 70)
        print(f"Batch question {index}/{len(batch)}")
        print(f"Database question ID: {question_id}")
        print("-" * 70)

        print(f"Question: {question}")

        try:
            # Retrieve context for faithfulness evaluation.
            retrieved_results = (
                answer_service.search_engine.search(
                    question,
                    top_k=TOP_K,
                )
            )

            retrieved_context = prepare_context(
                retrieved_results
            )

            # Generate answer using existing RAG pipeline.
            response = await answer_service.answer_question(
                question,
                top_k=TOP_K,
            )

            generated_answer = response["answer"]
            sources = response["sources"]

            generation_time = response["timings"][
                "generation_seconds"
            ]

            print(f"\nGenerated answer:\n{generated_answer}")
            print(f"\nGeneration time: {generation_time:.2f}s")

            abstained = is_abstention(
                generated_answer,
                sources,
            )

            if abstained:
                abstentions += 1
                print("Status: ABSTENTION")
            else:
                successful_answers += 1
                print("Status: ANSWER GENERATED")

            # Evaluate generated answer.
            print("\nRunning evaluation judge...")

            judge_result = evaluate_answer(
                question=question,
                expected_answer=expected_answer,
                generated_answer=generated_answer,
                retrieved_context=retrieved_context,
            )

            correctness = judge_result["correctness"]["score"]
            faithfulness = judge_result["faithfulness"]["score"]
            relevancy = judge_result["relevancy"]["score"]

            # Save results immediately.
            record = {
                "question_id": question_id,
                "question": question,
                "expected_answer": expected_answer,
                "generated_answer": generated_answer,
                "correctness": correctness,
                "correctness_reason": (
                    judge_result["correctness"]["reason"]
                ),
                "faithfulness": faithfulness,
                "faithfulness_reason": (
                    judge_result["faithfulness"]["reason"]
                ),
                "relevancy": relevancy,
                "relevancy_reason": (
                    judge_result["relevancy"]["reason"]
                ),
                "generation_seconds": generation_time,
                "abstention": abstained,
                "sources": json.dumps(sources),
            }

            save_result(record)

            correctness_scores.append(correctness)
            faithfulness_scores.append(faithfulness)
            relevancy_scores.append(relevancy)
            generation_times.append(generation_time)

            print("\nEvaluation scores:")
            print(f"Correctness:  {correctness}/5")
            print(f"Faithfulness: {faithfulness}/5")
            print(f"Relevancy:    {relevancy}/5")

            print("<Saved successfully>")

        except Exception as error:

            failed_evaluations += 1

            print(
                f"\nEvaluation failed for question "
                f"{question_id}: {error}"
            )

            print("This question will be retried in the next run.")

    # =====================================================
    # Current Batch Summary
    # =====================================================

    print("\n" + "=" * 70)
    print("BATCH EVALUATION SUMMARY")
    print("=" * 70)

    print(f"Questions processed: {len(batch)}")
    print(f"Successful answers: {successful_answers}")
    print(f"Abstentions: {abstentions}")
    print(f"Failed evaluations: {failed_evaluations}")

    if correctness_scores:

        print("\nAVERAGE SCORES (OUT OF 5)")
        print("-" * 40)

        print(
            f"Correctness: "
            f"{statistics.mean(correctness_scores):.2f}/5"
        )

        print(
            f"Faithfulness: "
            f"{statistics.mean(faithfulness_scores):.2f}/5"
        )

        print(
            f"Relevancy: "
            f"{statistics.mean(relevancy_scores):.2f}/5"
        )

        print(
            f"Average generation time: "
            f"{statistics.mean(generation_times):.2f}s"
        )

    remaining_after_batch = (
        len(dataset) - len(load_completed_ids())
    )

    print("\n" + "=" * 70)
    print(f"Questions still remaining: {remaining_after_batch}")
    print(f"Results saved to: {OUTPUT_FILE}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
