from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
import os

# === CONFIG ===
PDF_PATH = "your_kotlin_book.pdf"         # <--- replace with your actual file
COLLECTION_NAME = "kotlin_docs"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

def main():
    # Step 1: Load PDF
    print("📄 Loading PDF...")
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()

    # Step 2: Split into chunks
    print("✂️ Splitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)

    # Step 3: Create Embeddings
    print("🧠 Creating embeddings...")
    embeddings = OpenAIEmbeddings()

    # Step 4: Connect to Qdrant
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    # Step 5: Store in Qdrant
    print("📦 Storing in Qdrant...")
    Qdrant.from_documents(
        documents=chunks,
        embedding=embeddings,
        client=client,
        collection_name=COLLECTION_NAME
    )

    print(f"✅ Done! Stored {len(chunks)} chunks in Qdrant collection: '{COLLECTION_NAME}'")

if __name__ == "__main__":
    main()
