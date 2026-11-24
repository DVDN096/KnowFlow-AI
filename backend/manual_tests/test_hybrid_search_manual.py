from backend.app.retrieval.hybrid_search import HybridSearch

search_engine = HybridSearch()

query = input("Ask a question about your engineering documents: ").strip()
results = search_engine.search(query, top_k=5)

if not results:
    print("No matching chunks found.")
else:
    for rank, result in enumerate(results, start=1):
        print("\n" + "=" * 70)
        print(f"Result #{rank}")
        print(f"Source: {result['source']}")
        print(f"Page: {result['page_number']}")
        print(f"Chunk index: {result['chunk_index']}")
        print(f"RRF score: {result['rrf_score']:.5f}")

        if result["similarity"] is not None:
            print(f"Vector similarity: {result['similarity']:.4f}")

        print(f"\n{result['text'][:800]}")