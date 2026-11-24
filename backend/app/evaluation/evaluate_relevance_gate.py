
from backend.app.retrieval.hybrid_search import HybridSearch


# Evaluation configuration
TOP_K = 5
SIMILARITY_THRESHOLD = 0.30

# Questions answerable from the currently indexed PDFs
ANSWERABLE_QUESTIONS = [
    "What is self-attention in Transformers?",
    "Why does the Transformer use positional encodings?",
    "How is scaled dot-product attention calculated?",
    "What is the purpose of multi-head attention?",
    "Why does the Transformer decoder use masking?",
    "What is object detection?",
    "How does YOLO make predictions?",
    "What is the difference between object localization and object detection?",
    "How does Faster R-CNN use a Region Proposal Network?",
    "How does SSD predict objects using feature maps?",
]

# Questions not answerable from the currently indexed PDFs
UNANSWERABLE_QUESTIONS = [
    "What is the capital of Japan?",
    "Explain Kubernetes pod scheduling.",
    "How does TCP congestion control work?",
    "What is the difference between SQL and NoSQL?",
    "How does blockchain mining work?",
    "What is the normal operating temperature of a lithium-ion battery?",
    "Explain the working of a relational database index.",
    "How does OAuth 2.0 authentication work?",
    "What is the difference between Docker and virtual machines?",
    "Explain the working of the Raft consensus algorithm.",
]


def get_max_similarity(search_engine, question):
    results = search_engine.search(question, top_k=TOP_K)

    return max(
        (
            result["similarity"]
            for result in results
            if result["similarity"] is not None
        ),
        default=0.0,
    )


def main():
    search_engine = HybridSearch()

    true_accepts = 0
    false_rejects = 0
    true_rejects = 0
    false_accepts = 0

    print("\nRELEVANCE GATE EVALUATION")
    print("=" * 80)
    print(f"Similarity threshold: {SIMILARITY_THRESHOLD}")
    print(f"Top K: {TOP_K}")

    print("\nANSWERABLE QUESTIONS")
    print("-" * 80)

    for question in ANSWERABLE_QUESTIONS:
        similarity = get_max_similarity(search_engine, question)
        accepted = similarity >= SIMILARITY_THRESHOLD

        if accepted:
            true_accepts += 1
        else:
            false_rejects += 1

        print(
            f"{'ACCEPT' if accepted else 'REJECT'} | "
            f"{similarity:.4f} | {question}"
        )

    print("\nUNANSWERABLE QUESTIONS")
    print("-" * 80)

    for question in UNANSWERABLE_QUESTIONS:
        similarity = get_max_similarity(search_engine, question)
        accepted = similarity >= SIMILARITY_THRESHOLD

        if accepted:
            false_accepts += 1
        else:
            true_rejects += 1

        print(
            f"{'ACCEPT' if accepted else 'REJECT'} | "
            f"{similarity:.4f} | {question}"
        )

    total = (
        true_accepts + false_rejects
        + true_rejects + false_accepts
    )

    accuracy = (true_accepts + true_rejects) / total

    precision = (
        true_accepts / (true_accepts + false_accepts)
        if true_accepts + false_accepts else 0.0
    )

    recall = (
        true_accepts / (true_accepts + false_rejects)
        if true_accepts + false_rejects else 0.0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )

    false_acceptance_rate = (
        false_accepts / (false_accepts + true_rejects)
        if false_accepts + true_rejects else 0.0
    )

    print("\n" + "=" * 80)
    print("CONFUSION MATRIX")
    print("=" * 80)

    print(f"True Accepts:  {true_accepts}")
    print(f"False Rejects: {false_rejects}")
    print(f"True Rejects:  {true_rejects}")
    print(f"False Accepts: {false_accepts}")

    print("\nMETRICS")
    print("-" * 80)
    print(f"Accuracy:               {accuracy:.4f}")
    print(f"Precision:              {precision:.4f}")
    print(f"Recall:                 {recall:.4f}")
    print(f"F1 Score:               {f1:.4f}")
    print(f"False Acceptance Rate:  {false_acceptance_rate:.4f}")


if __name__ == "__main__":
    main()
