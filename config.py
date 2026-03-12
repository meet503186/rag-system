from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

load_dotenv()

# ==============================
# CONFIGURATION
# ==============================

EMBED_MODEL = "sentence-transformers/all-mpnet-base-v2"
DENSE_K = 8
SPARSE_K = 8
FUSION_TOP_K = 20
RERANK_TOP_K = 3
RRF_K = 60
QUERY_VARIATIONS = 5
LLM_MODEL = "openai/gpt-oss-120b"
VECTOR_DB_DIRECTORY = "app/db/chroma_db"

# Max score threshold -> relevant docs will have less than this
SIMILARITY_THRESHOLD = 1.2 
FALLBACK_ANSWER="The answer cannot be determined from the provided information."

# ==============================
# INITIALIZE MODELS
# ==============================

embedding_model = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
client = InferenceClient()
