from mem0 import Memory
from groq import Groq
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
import time
import backoff
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# client = QdrantClient(host="localhost", port=6333)
# client.delete_collection("mem0")
# client.delete_collection("mem0migrations")  # optional if unused
# print("Deleted mem0 and mem0migrations")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
QUADRANT_HOST = "localhost"
NEO4J_URL = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "atom-william-carter-vibrate-press-9029"

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "sentence-transformers/all-MiniLM-L6-v2"
        },
    },
    "llm": {
        "provider": "groq",
        "config": {"api_key": GROQ_API_KEY, "model": "llama3-70b-8192"}
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": QUADRANT_HOST,
            "port": 6333,
            "collection_name": "mem0",  # force name
            "embedding_model_dims": 384
        },
    },
}


mem_client = Memory.from_config(config)

# Initialize Qdrant client
client = QdrantClient(host=QUADRANT_HOST, port=6333)
collection_name = "mem0"  

# Check if collection exists, create only if missing
try:
    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]
    print("Existing collections:", collection_names)

    if collection_name not in collection_names:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        print(f"Created new Qdrant collection: {collection_name}")
    else:
        print(f"Using existing Qdrant collection: {collection_name}")

except Exception as e:
    print(f"Error checking/creating Qdrant collection: {e}")


groq_client = Groq(api_key=GROQ_API_KEY)

# Retry decorator for handling Groq rate limit errors
#@backoff.on_exception(backoff.expo, Exception, max_tries=3, max_time=60)
def call_groq_api(messages):
    return groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages
    )

#@backoff.on_exception(backoff.expo, Exception, max_tries=3, max_time=60)
def add_memory(messages, user_id):
    mem_client.add(messages, user_id=user_id)
    print("Successfully added conversation to memory")

def chat(message):
    # Search for relevant past memories
    try:
        mem_result = mem_client.search(query=message, user_id="p123")
        memories = "\n".join([m["memory"] for m in mem_result.get("results", [])])
    except Exception as e:
        print(f"Error searching memories: {e}")
        memories = ""

    print(f"\n\nMEMORY:\n\n{memories}\n\n")

    # Prepare system prompt with current memory context
    SYSTEM_PROMPT = f"""
    You are a Memory-Aware Fact Extraction Agent, designed to
    systematically analyze input content, extract structured knowledge, 
    and maintain an optimized memory store.

    Tone: Professional analytical, precision-focused, with clear uncertainty signaling

    Memory and Score:
    {memories}
    """

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message}
    ]

    # Call Groq LLM API
    try:
        result = call_groq_api(messages)
        response_content = result.choices[0].message.content
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        response_content = "Error: Unable to generate response"
        if "rate_limit_exceeded" in str(e):
            time.sleep(15)

    # Add assistant response to messages
    messages.append({"role": "assistant", "content": response_content})

    # Add conversation to memory
    try:
        add_memory(messages, user_id="p123")
    except Exception as e:
        print(f"Error adding memory: {e}")

    return response_content


while True:
    try:
        message = input(">> ")
        print("BOT: ", chat(message=message))
    except KeyboardInterrupt:
        print("\nExiting program...")
        break
        