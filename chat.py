# Imports
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


# Connect to Persistent ChromaDB
chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


# Open Existing Collection
try:
    collection = chroma_client.get_collection(
        name=COLLECTION_NAME
    )
except Exception:
    print("Vector database not found.")
    print("Please run 'python index.py' first.")
    exit()

print("=" * 50)
print("📄 PDF RAG Chatbot (Hugging Face)")
print("Type 'exit' to quit")
print("=" * 50)


while True:
    # -----------------------
    # User Input
    # -----------------------
    question = input("\nAsk your question: ")

    if question.lower() == "exit":
        print("\n👋 Goodbye!")
        break

    if not question.strip():
        print("Please enter a valid question.")
        continue

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
    retrieved_chunks = results["documents"][0]

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

    # Generate Answer using Hugging Face Model
    answer = generate_llm_response(client, prompt)

    # Display Answer
    print("\nAnswer:\n")
    print("=" * 50)
    print(answer)