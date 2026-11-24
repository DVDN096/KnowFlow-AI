from backend.app.retrieval.hybrid_search import HybridSearch

search = HybridSearch()

question = "How does YOLO perform object detection?"

results = search.search(question, top_k=10)

print(f"\nQuestion: {question}\n")

for result in results:
    print(
        f"Chunk ID: {result['chunk_id']} | "
        f"Vector rank: {result['vector_rank']} | "
        f"Lexical rank: {result['lexical_rank']} | "
        f"RRF: {result['rrf_score']:.5f}"
    )