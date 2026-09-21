import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent

# Paths
DATA_DIR = BASE_DIR / "data"
PDF_PATH = DATA_DIR / "company_policy.pdf"
CHROMA_DIR = BASE_DIR / "chroma_db"
SQLITE_PATH = BASE_DIR / "history.db"
COLLECTION_NAME = "company_policy"

# Admin (leave empty in .env to disable the password)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

# LM Studio (OpenAI-compatible server)
LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY", "lm-studio")
CHAT_MODEL = os.getenv("CHAT_MODEL", "qwen2.5-7b-instruct")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-nomic-embed-text-v1.5")

# Chunking
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# Retrieval
TOP_K = 4
BM25_WEIGHT = 0.5
VECTOR_WEIGHT = 0.5