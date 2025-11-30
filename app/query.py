import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.llms.ollama import Ollama

# Load .env vars
load_dotenv()

# Reuse same embedding logic
from ingest import get_pg_store, get_embed_model

def main():
    # Connect to PGVector
    pg_store = get_pg_store()
    storage_context = StorageContext.from_defaults(vector_store=pg_store)
    model, dim = get_embed_model()
    index = VectorStoreIndex.from_vector_store(pg_store, storage_context=storage_context, embed_model=model)

    # Use Ollama model (local LLM)
    llm = Ollama(model="llama3")

    query_engine = index.as_query_engine(llm=llm)

    print("🧠 Connected. Type a question or 'exit' to quit.")
    while True:
        question = input("\n> ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        response = query_engine.query(question)

        print("\n--- ANSWER ---")
        print(response.response)

        print("\n--- SOURCES ---")
        for source in response.source_nodes:
            print(f"- {source.metadata.get('file_name', 'unknown')} (score: {source.score:.3f})")
            preview = source.text[:250].replace("\n", " ")
            print(f"  {preview}...\n")


if __name__ == "__main__":
    main()
