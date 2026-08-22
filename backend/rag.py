import chromadb

from utils import (
    get_hf_client,
    create_query_embedding,
    generate_llm_response
)

from config import (
    CHROMA_PATH,
    COLLECTION_NAME,
    TOP_K
)


# Hugging Face Client
client = get_hf_client()


def get_collection():
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    return chroma_client.get_collection(name=COLLECTION_NAME)


def ask_question(question: str):
    collection = get_collection()

    # Generate Query Embedding
    query_embedding = create_query_embedding(
        client,
        question
    )

    # Search Similar Chunks
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K
    )

    # Extract Retrieved Chunks
    retrieved_chunks = results["documents"][0] if results and results.get("documents") else []

    # Build Context
    context = "\n\n".join(retrieved_chunks)

    # Build Prompt
    prompt = f"""You are a helpful AI assistant.

Answer the user's question ONLY using the provided context.

If the answer is not available in the context, say:
"I couldn't find the answer in the provided document."

Context:
{context}

Question:
{question}

Answer:"""

    # Generate Answer
    answer = generate_llm_response(client, prompt)

    return answer