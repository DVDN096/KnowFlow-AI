
from backend.app.retrieval.search import SemanticSearch
from backend.app.retrieval.hybrid_search import HybridSearch

questions = {
    "Q1": "Why did the authors introduce the Transformer instead of relying on recurrent networks?",
    "Q9": "Why does the Transformer require positional encodings, and how are they generated?",
    "Q17": "How does R-CNN use selective search and region proposals?",
}

semantic = SemanticSearch()
hybrid = HybridSearch()

for label, question in questions.items():
    print("\n" + "=" * 80)
    print(f"{label}: {question}")
    print("=" * 80)

    print("\n--- SEMANTIC SEARCH ---")
    semantic_results = semantic.search(question, top_k=5)

    for rank, result in enumerate(semantic_results, 1):
        print(
            f"\nRank: {rank} | "
            f"Chunk: {result['chunk_id']} | "
            f"Similarity: {result['similarity']:.4f}"
        )
        print(result["text"][:400].replace("\n", " "))

    print("\n--- HYBRID SEARCH ---")
    hybrid_results = hybrid.search(question, top_k=5)

    for rank, result in enumerate(hybrid_results, 1):
        print(
            f"\nRank: {rank} | "
            f"Chunk: {result['chunk_id']} | "
            f"RRF: {result['rrf_score']:.5f} | "
            f"Vector Rank: {result['vector_rank']} | "
            f"Lexical Rank: {result['lexical_rank']} | "
            f"Similarity: {result['similarity']}"
        )
        print(result["text"][:400].replace("\n", " "))
