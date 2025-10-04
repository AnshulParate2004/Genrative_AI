from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

# Loaoding Data source
# 📝 Load PDF document
# If this is inside a script file, use __file__ to locate sibling PDF:
print("📄 Loading PDF...")
pdf_path = Path(__file__).parent / "KotlinNotesForProfessionals.pdf"
loader = PyPDFLoader(file_path=str(pdf_path))
docs = loader.load()
print(f"✅ Loaded {len(docs)} pages from PDF.")

# Chunking Data
# ✂️ Split into chunks
print("✂️ Splitting documents into chunks...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
split_docs = text_splitter.split_documents(documents=docs)
print(f"✅ Split into {len(split_docs)} chunks.")

print(f"Loaded {len(docs)} document chunks.")
print("DOCS", len(docs))  # number of pages
print("SPLIT", len(split_docs))  # number of chunks pages are divided into

# Embedding Data ( Vectorization of data )
# 🧠 Embedding using Hugging Face (no API key needed)
print("🧠 Creating embeddings (HuggingFace)...")
from langchain_community.embeddings import HuggingFaceEmbeddings

# Embedder
embedder = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
print("✅ HuggingFace embeddings initialized.")

# Vectore storage
# 🧱 Vector Store (Qdrant)
print("📦 Connecting to Qdrant and storing vectors...")
vector_store = QdrantVectorStore.from_documents(
    documents=split_docs,
    embedding=embedder,
    url="http://localhost:6333",
    collection_name="kotlin_short_notes"
)
print("✅ Documents stored in Qdrant.")

# Adding docs
print("➕ Adding documents again (if needed)...")
vector_store.add_documents(documents=split_docs)
print("✅ Injection Done")

# Making database for retriver
print("🔍 Initializing retriever from Qdrant collection...")
retriever_short = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="kotlin_short_notes",
    embedding=embedder,
)
print("✅ Retriever ready.")

# Perform search
print("🔎 Performing similarity search...")
relevant_chunks = retriver.similarity_search(
    query="What is Inline Functions?"
)

print("✅ Search complete.")
print("Relevant Chunks:")
for i, chunk in enumerate(relevant_chunks):
    print(f"\n--- Chunk {i+1} ---")
    print(chunk.page_content)
