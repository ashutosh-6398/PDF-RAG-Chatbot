import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

from config import EMBEDDING_MODEL, HF_LLM_MODEL


# Global cache for sentence transformer model
_embedding_model_instance = None


def get_embedding_model():
    """
    Returns cached SentenceTransformer model instance.
    """
    global _embedding_model_instance
    if _embedding_model_instance is None:
        _embedding_model_instance = SentenceTransformer(EMBEDDING_MODEL)
    return _embedding_model_instance


def load_pdf(pdf_path):
    """
    Reads a PDF file and returns all its text as a single string.
    """
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text


def create_chunks(text, chunk_size=1000, chunk_overlap=200):
    """
    Splits the given text into smaller overlapping chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return text_splitter.split_text(text)


def get_hf_client():
    """
    Creates and returns a Hugging Face InferenceClient.
    """
    load_dotenv()
    token = os.getenv("HUGGINGFACEHUB_API_TOKEN") or os.getenv("HUGGINGFACE_API_TOKEN") or os.getenv("HF_TOKEN")
    return InferenceClient(model=HF_LLM_MODEL, token=token)


# For backward compatibility
get_gemini_client = get_hf_client


def create_embeddings(client, chunks):
    """
    Generates embeddings for all chunks using SentenceTransformers.
    """
    model = get_embedding_model()
    embeddings = model.encode(chunks, convert_to_numpy=True).tolist()
    return embeddings


def create_query_embedding(client, question):
    """
    Generates an embedding for the user's question.
    """
    model = get_embedding_model()
    embedding = model.encode(question, convert_to_numpy=True).tolist()
    return embedding


def generate_llm_response(client, prompt):
    """
    Generates text answer using Hugging Face model inference.
    """
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512
        )
        return response.choices[0].message.content
    except Exception:
        response = client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512
        )
        return response.choices[0].message.content