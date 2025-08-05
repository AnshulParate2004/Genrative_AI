from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings


from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

# Loaoding Data source
# 📝 Load PDF document
# If this is inside a script file, use __file__ to locate sibling PDF:
pdf_path = Path(__file__).parent / "node-handbook.pdf"

loader = PyPDFLoader(file_path=str(pdf_path))
docs = loader.load()
   


# Chunking Data
# ✂️ Split into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

split_docs = text_splitter.split_documents(documents=docs)

print(f"Loaded {len(docs)} document chunks.")
print("DOCS",len(docs)) # number of pages
print("SPLIT",len(split_docs)) # number of chunks pages are divied into 


# Embedding Data ( Vectorization of data )
# 🧠 Embedding using Hugging Face (no API key needed)
from langchain_community.embeddings import HuggingFaceEmbeddings
#Embedder
embedder = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Vectore storage
# 🧱 Vector Store (Qdrant)
vector_store = QdrantVectorStore.from_documents(
    documents=split_docs,
    embedding=embedder,
    url="http://localhost:6333",
    collection_name="learning_langchain"
)
# Adding docs
vector_store.add_documents(documents=split_docs)
print("Injection Done")


# Making database for retriver
retriver =QdrantVectorStore.from_existing_collection(
    url = "http://localhost:6333",
    collection_name="learning_langchain",
    embedding=embedder,
)

relevant_chunks = retriver.similarity_search(
    query="What is FS Module?"
)

print("Relevant Chunks",search_result)

SYSTEM_PROMPT = f"""
You are a helpful AI assistant. Answer the user's question based **only** on the context provided below. 
If the answer cannot be found in the context, respond with: "I couldn't find relevant information in the provided context."

Use clear, concise, and accurate language. Do not make up information.

Context:
{relevant_chunks}
"""
