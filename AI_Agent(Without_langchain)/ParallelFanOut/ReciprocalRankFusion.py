from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

# 🧠 Embedding model
embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 🔌 Load both vector stores
short_notes = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="kotlin_short_notes",
    embedding=embedder,
)

big_notes = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="kotlin_big_notes",
    embedding=embedder,
)

# ❓ Your query
query = "What are inline functions in Kotlin?"
k = 60  # RRF constant
top_n = 5  # How many final results you want

# 🔍 Retrieve from both
def search_with_scores(store, query, limit=10):
    return store.similarity_search_with_score(query, k=limit)

with ThreadPoolExecutor() as executor:
    future_short = executor.submit(search_with_scores, short_notes, query)
    future_big = executor.submit(search_with_scores, big_notes, query)

    results_short = future_short.result()
    results_big = future_big.result()

# 🧠 RRF Score Aggregation
rrf_scores = defaultdict(float)
doc_map = {}

def apply_rrf(results, source_name):
    for rank, (doc, score) in enumerate(results):
        doc_id = hash(doc.page_content)  # crude deduplication
        rrf_scores[doc_id] += 1 / (k + rank)
        if doc_id not in doc_map:
            doc_map[doc_id] = doc

apply_rrf(results_short, "short_notes")
apply_rrf(results_big, "big_notes")

# 📊 Sort and show top N
ranked_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
print(f"\n✅ Top {top_n} Results using Reciprocal Rank Fusion:\n")

for i, (doc_id, score) in enumerate(ranked_docs[:top_n]):
    print(f"--- Result {i+1} (Score: {score:.4f}) ---")
    print(doc_map[doc_id].page_content)
    print()
