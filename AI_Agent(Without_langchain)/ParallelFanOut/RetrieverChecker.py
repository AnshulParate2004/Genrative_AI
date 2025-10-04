from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

# 🧠 Load same embedder model
print("🧠 Loading embedding model...")
embedder = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# 🔍 Load retriever from existing Qdrant collection
print("🔌 Connecting to Qdrant and initializing retriever...")
retriever_short = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="kotlin_short_notes",
    embedding=embedder,
)

# ❓ Ask a question
query = "What are inline functions in Kotlin?"
print(f"\n🔎 Asking: {query}")
results = retriever.similarity_search(query=query)

# 📄 Show results
print("\n✅ Results:")
for i, doc in enumerate(results):
    print(f"\n--- Result {i+1} ---")
    print(doc.page_content)
