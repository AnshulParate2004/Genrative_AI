from mem0 import Memory
from groq import Groq
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
import os


load_dotenv()

# Constants
GROQ_API_KEY = os.getenv("GROQ_API_KEY") # Replace with your key
USER_ID = "local-user-1"

# Embedding model
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Init Qdrant
qdrant = QdrantClient(host="localhost", port=6333)

# Auto-detect embedding dimension
model = SentenceTransformer(EMBED_MODEL)
embedding_dim = model.get_sentence_embedding_dimension()
print(f"Embedding dimension detected: {embedding_dim}")

# Recreate Qdrant collection
if qdrant.collection_exists("memories"):
    qdrant.delete_collection("memories")
    print("Old Qdrant collection deleted.")
qdrant.create_collection(
    collection_name="memories",
    vectors_config=models.VectorParams(size=embedding_dim, distance=models.Distance.COSINE)
)
print(f"New Qdrant collection created with size={embedding_dim}")

# mem0 config — Qdrant only
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
    "llm": {
        "provider": "groq",
        "config": {
            "api_key": GROQ_API_KEY,
            "model": "llama-3.3-70b-versatile"
        }
    }
}

# Create clients
mem_client = Memory.from_config(config)
groq_client = Groq(api_key=GROQ_API_KEY)

def chat_with_groq(message):
    # Retrieve top 3 relevant memories
    past_context = mem_client.search(message, user_id=USER_ID, limit=3)
    context_text = "\n".join([m['memory'] for m in past_context if isinstance(m, dict) and 'memory' in m]) if past_context else ""
    
    # Build prompt
    messages = []
    if context_text:
        messages.append({"role": "system", "content": f"Previous conversation:\n{context_text}"})
    messages.append({"role": "user", "content": message})
    
    # Get LLM response
    result = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    reply = result.choices[0].message.content
    
    # Save memory
    mem_client.add(message, user_id=USER_ID, metadata={"role": "user"})
    mem_client.add(reply, user_id=USER_ID, metadata={"role": "assistant"})
    
    return reply

# Chat loop
while True:
    msg = input(">> ")
    print("BOT:", chat_with_groq(msg))
