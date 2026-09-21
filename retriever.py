import re
from functools import lru_cache

from langchain_chroma import Chroma
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_openai import OpenAIEmbeddings

from config import (
    BM25_WEIGHT,
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    LM_STUDIO_API_KEY,
    LM_STUDIO_BASE_URL,
    TOP_K,
    VECTOR_WEIGHT,
)
from ingest import index_documents, load_and_split_pdf


# Embedding model
embeddings = OpenAIEmbeddings(
    model=EMBEDDING_MODEL,
    base_url=LM_STUDIO_BASE_URL,
    api_key=LM_STUDIO_API_KEY,
    check_embedding_ctx_length=False,
)


# ChromaDB
def get_vectorstore():
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )


# Convert text into words for BM25
def preprocess(text):
    return re.findall(r"\w+", text.lower())


# Build BM25 + Vector retriever
@lru_cache(maxsize=1)
def build_hybrid_retriever():
    # Load PDF and create chunks
    chunks = load_and_split_pdf()

    # Store chunks in ChromaDB
    vectorstore = get_vectorstore()
    index_documents(chunks, vectorstore)

    # Vector search
    vector_retriever = vectorstore.as_retriever(
        search_kwargs={"k": TOP_K}
    )

    # BM25 keyword search
    bm25_retriever = BM25Retriever.from_documents(
        chunks,
        k=TOP_K,
        preprocess_func=preprocess,
    )

    # Combine both searches
    return EnsembleRetriever(
        retrievers=[bm25_retriever, vector_retriever],
        weights=[BM25_WEIGHT, VECTOR_WEIGHT],
    )


# Search function used by graph.py
def hybrid_search(query):
    retriever = build_hybrid_retriever()
    return retriever.invoke(query)