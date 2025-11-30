import os
from dotenv import load_dotenv
import psycopg2
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Document
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core.node_parser import SimpleNodeParser


# --- Toggle here ---
USE_OPENAI = False  # set True when using OpenAI embeddings


def get_embed_model():
    """Return embedding model and dimension."""
    if USE_OPENAI:
        from llama_index.embeddings.openai import OpenAIEmbedding
        import openai

        openai.api_type = "azure"
        openai.api_key = os.getenv("AZURE_OPENAI_KEY")
        openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
        openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")

        model = OpenAIEmbedding(model="text-embedding-3-small")
        vector_dim = 1536
    else:
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vector_dim = 384
    return model, vector_dim

def get_pg_store():
    """Return a vector store, creating the table if it doesn't exist."""
    embed, dim =get_embed_model()
    pg_store = PGVectorStore.from_params(
        database=os.getenv("PGDATABASE", "vectordb"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "password"),
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", 5432),
        table_name=os.getenv("TABLE_NAME", "documents"),
        embed_dim=dim
    )

    return pg_store


def main():
    load_dotenv()
    embed_model, vector_dim = get_embed_model()

    pg_store = get_pg_store()
    storage_context = StorageContext.from_defaults(vector_store=pg_store)
    node_parser = SimpleNodeParser.from_defaults(chunk_size=200, chunk_overlap=20)

    raw_docs = SimpleDirectoryReader("docs").load_data()
    docs = [Document(text=clean_text(d.text), metadata=d.metadata) for d in raw_docs]

    index = VectorStoreIndex.from_documents(
        docs,
        embed_model=embed_model,
        node_parser=node_parser,
        storage_context=storage_context
    )

    print(f"✅ Ingested {len(docs)} documents into Postgres vector store.")


def clean_text(s: str) -> str:
    """Remove null bytes and other unsafe characters."""
    if not s:
        return ""
    return s.replace("\x00", "")

if __name__ == "__main__":
    main()
