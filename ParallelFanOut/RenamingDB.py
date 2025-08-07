from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

OLD_COLLECTION = "learning_langchain"
NEW_COLLECTION = "kotlin_short_notes"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

# Connect to Qdrant
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# Step 1: Fetch all points from the old collection
print(f"📥 Fetching points from '{OLD_COLLECTION}'...")
scroll_result, _ = client.scroll(
    collection_name=OLD_COLLECTION,
    limit=10_000,  # increase if you have more
    with_payload=True,
    with_vectors=True
)
points = [PointStruct(id=point.id, vector=point.vector, payload=point.payload) for point in scroll_result]
print(f"✅ Retrieved {len(points)} points.")

# Step 2: Create the new collection
print(f"📦 Creating new collection '{NEW_COLLECTION}'...")
client.recreate_collection(
    collection_name=NEW_COLLECTION,
    vectors_config=VectorParams(size=len(points[0].vector), distance=Distance.COSINE),
)
print("✅ New collection created.")

# Step 3: Upload points to new collection
print(f"🚀 Uploading points to '{NEW_COLLECTION}'...")
client.upsert(
    collection_name=NEW_COLLECTION,
    points=points
)
print("✅ Points inserted into new collection.")

# Step 4: (Optional) Delete old collection
print(f"🗑️ Deleting old collection '{OLD_COLLECTION}'...")
client.delete_collection(collection_name=OLD_COLLECTION)
print("✅ Old collection deleted.")

print("🎉 Renaming completed successfully!")
