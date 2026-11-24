
from backend.app.generation.answer import AnswerService

service = AnswerService()

while True:
    question = input("\nAsk KnowFlow (or type 'exit'): ").strip()

    if question.lower() == "exit":
        break

    try:
        result = service.answer_question(question)

        print("\n" + "=" * 70)
        print("ANSWER\n")
        print(result["answer"])

        print("\nRETRIEVED SOURCES")
        for source in result["sources"]:
            print(
                f"- {source['source']}, "
                f"page {source['page_number']}, "
                f"chunk {source['chunk_index']}"
            )

        timings = result["timings"]

        print("\nPERFORMANCE")
        print(f"Retrieval:   {timings['retrieval_seconds']:.4f} seconds")
        print(f"Generation:  {timings['generation_seconds']:.4f} seconds")
        print(f"Total:       {timings['total_seconds']:.4f} seconds")

    except Exception as exc:
        print(f"Error: {exc}")
