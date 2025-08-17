from mem0 import Memory
from groq import Groq
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()
# Constants
NEO4J_URL = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "atom-william-carter-vibrate-press-9029"
GROQ_API_KEY =os.getenv("GROQ_API_KEY")
USER_ID = "local-user-1"

# Set embedding model
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Init Qdrant
qdrant = QdrantClient(host="localhost", port=6333)

# 1️⃣ Auto-detect embedding dimension
model = SentenceTransformer(EMBED_MODEL)
embedding_dim = model.get_sentence_embedding_dimension()
print(f"Embedding dimension detected: {embedding_dim}")

# 2️⃣ Wipe & recreate collection
if qdrant.collection_exists("memories"):
    qdrant.delete_collection("memories")
    print("Old Qdrant collection deleted.")
qdrant.create_collection(
    collection_name="memories",
    vectors_config=models.VectorParams(size=embedding_dim, distance=models.Distance.COSINE)
)
print(f"New Qdrant collection created with size={embedding_dim}")

# 4️⃣ Config
config = {
    "version": "v1.1",
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": EMBED_MODEL
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "memories",
            "embedding_model_dims": embedding_dim
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": NEO4J_URL,
            "username": NEO4J_USERNAME,
            "password": NEO4J_PASSWORD
        }
    },
    "llm": {
        "provider": "groq",
        "config": {
            "api_key": GROQ_API_KEY,
            "model": "llama-3.3-70b-versatile"
        }
    }
}

# 5️⃣ Create clients
mem_client = Memory.from_config(config)
groq_client = Groq(api_key=GROQ_API_KEY)

def chat_with_groq(message):
    # Retrieve past memories
    past_context = mem_client.search(message, user_id=USER_ID, limit=3)
    context_text = "\n".join([m['memory'] for m in past_context if isinstance(m, dict) and 'memory' in m]) if past_context else ""
    
    messages = []
    if context_text:
        messages.append({"role": "system", "content": f"Previous conversation:\n{context_text}"})
    messages.append({"role": "user", "content": message})
    
    result = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    
    reply = result.choices[0].message.content
    
    # Save memory
    mem_client.add(message, user_id=USER_ID, metadata={"role": "user"})
    mem_client.add(reply, user_id=USER_ID, metadata={"role": "assistant"})
    
    return reply

# 6️⃣ Chat loop
while True:
    msg = input(">> ")
    print("BOT:", chat_with_groq(msg))