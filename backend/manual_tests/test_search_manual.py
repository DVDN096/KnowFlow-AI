from backend.app.retrieval.search import SemanticSearch


search_engine = SemanticSearch()

query = input("Ask a question about your PDF: ").strip()

results = search_engine.search(query, top_k=3)

if not results:
    print("No matching chunks found.")
else:
    for rank, result in enumerate(results, start=1):
        print("\n" + "=" * 70)
        print(f"Result #{rank}")
        print(f"Source: {result['source']}")
        print(f"Page: {result['page_number']}")
        print(f"Chunk index: {result['chunk_index']}")
        print(f"Similarity: {result['similarity']:.4f}")
        print(f"\n{result['text'][:800]}")