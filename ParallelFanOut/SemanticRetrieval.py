# 1. Install required packages:
# pip install qdrant-client sentence-transformers
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import uuid

# 2. Connect to Qdrant running locally or on cloud
client = QdrantClient(host="localhost", port=6333)  # use your actual host/port

# 3. Define collection name (a collection = a group of vectors)
collection_name = "my_documents"

# 4. Load a pretrained SentenceTransformer model for semantic embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")

# 5. Sample documents (can be chunks of larger files)
documents = [
    "Python is a high-level programming language.",
    "Dogs are loyal animals and good pets.",
    "Qdrant is a vector database used for semantic search.",
    "The Eiffel Tower is located in Paris.",
    "Cats and dogs are both common household animals."
]

# 6. Convert each document into a semantic vector (dense embedding)
embeddings = model.encode(documents).tolist()

# 7. Create a Qdrant collection (if not exists)
client.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=len(embeddings[0]), distance=Distance.COSINE)
)

# 8. Upload document vectors to Qdrant
points = [
    PointStruct(id=i, vector=embeddings[i], payload={"text": documents[i]})
    for i in range(len(documents))
]

client.upsert(collection_name=collection_name, points=points)

# 9. Input a query and encode it semantically
query = "What is a vector database?"
query_vector = model.encode(query).tolist()

# 10. Perform semantic search using cosine similarity
results = client.search(
    collection_name=collection_name,
    query_vector=query_vector,
    limit=3  # Top 3 most semantically similar results
)

# 11. Show retrieved results
print("\n🔍 Query:", query)
print("📚 Top semantic matches:")
for hit in results:
    print(f"→ {hit.payload['text']} (Score: {hit.score:.4f})")
