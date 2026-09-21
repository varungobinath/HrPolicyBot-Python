from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_OVERLAP, CHUNK_SIZE, PDF_PATH

BATCH_SIZE = 64


def load_and_split_pdf():
    """Load company_policy.pdf and split it into chunks."""
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

    pages = PyPDFLoader(str(PDF_PATH)).load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_documents(pages)


def clear_collection(vectorstore):
    """Remove every stored chunk from the ChromaDB collection."""
    ids = vectorstore.get()["ids"]
    for i in range(0, len(ids), 500):
        vectorstore.delete(ids=ids[i : i + 500])


def index_documents(chunks, vectorstore, replace=False):
    """
    Add chunks to ChromaDB.
    - replace=False: only index if the collection is empty (normal app start).
    - replace=True : wipe the old chunks first, then index (used after a new upload).
    """
    if replace:
        clear_collection(vectorstore)
    elif len(vectorstore.get(limit=1)["ids"]) > 0:
        return

    for i in range(0, len(chunks), BATCH_SIZE):
        vectorstore.add_documents(chunks[i : i + BATCH_SIZE])