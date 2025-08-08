from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

# Loaoding Data source
# 📝 Load PDF document
# If this is inside a script file, use __file__ to locate sibling PDF:
print("📄 Loading PDF...")
pdf_path = Path(__file__).parent / "KotlinNotesForProfessionals.pdf"  # 🧾 Use your 1500-page Kotlin notes PDF here
loader = PyPDFLoader(file_path=str(pdf_path))
docs = loader.load()
print(f"✅ Loaded {len(docs)} pages from PDF.")

# Chunking Data
# ✂️ Split into chunks
print("✂️ Splitting documents into chunks...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # 📦 Maximum characters per chunk
    chunk_overlap=200     # 🔁 Overlap to maintain context
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
    model_name="sentence-transformers/all-MiniLM-L6-v2"  # 🧠 Small but good-quality transformer
)
print("✅ HuggingFace embeddings initialized.")

# Vectore storage
# 🧱 Vector Store (Qdrant)
# ✅ Convert chunked documents to plain text
# ✅ Clean chunk text thoroughly
print("🧹 Cleaning chunk text...")
texts = []
for doc in split_docs:
    if hasattr(doc, "page_content"):
        content = doc.page_content
        if isinstance(content, str):
            clean_text = content.strip()
            if clean_text:
                texts.append(clean_text)

print(f"📝 Prepared {len(texts)} clean text chunks.")

# ✅ Store embeddings in Qdrant
print("📦 Connecting to Qdrant and storing vectors...")
vector_store = QdrantVectorStore.from_texts(
    texts=texts,
    embedding=embedder,
    url="http://localhost:6333",
    collection_name="kotlin_big_notes"
)
print("✅ Stored embeddings in Qdrant.")

# Making database for retriver
print("🔍 Initializing retriever from Qdrant collection...")
retriever_big = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="kotlin_big_notes",
    embedding=embedder,
)
print("✅ Retriever ready.")

# Perform search
print("🔎 Performing similarity search...")
relevant_chunks = retriever_big.similarity_search(
    query="What is Inline Functions?"
)

print("✅ Search complete.")
print("Relevant Chunks:")
for i, chunk in enumerate(relevant_chunks):
    print(f"\n--- Chunk {i+1} ---")
    print(chunk.page_content)
