from mem0 import Memory
from groq import Groq
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from neo4j import GraphDatabase
import time
import backoff
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY =  os.getenv("GROQ_API_KEY")
QUADRANT_HOST = "localhost"
NEO4J_URL = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "atom-william-carter-vibrate-press-9029"

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "huggingface",
        "config": {"model": "sentence-transformers/all-MiniLM-L6-v2"},
    },
    "llm": {"provider": "groq", "config": {"api_key": GROQ_API_KEY, "model": "llama3-70b-8192"}},
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": QUADRANT_HOST,
            "port": 6333,
        },
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {"url": NEO4J_URL, "username": NEO4J_USERNAME, "password": NEO4J_PASSWORD},
    },
}

mem_client = Memory.from_config(config)

# Initialize Qdrant client
client = QdrantClient(host=QUADRANT_HOST, port=6333)
collection_name = "mem0"  # Default collection name in Mem0

# Check and delete existing collections to avoid dimension mismatch
try:
    collections = client.get_collections().collections
    print("Existing collections:", [c.name for c in collections])
    for collection in collections:
        if collection.name.startswith("mem0"):
            client.delete_collection(collection.name)
            print(f"Deleted collection: {collection.name}")
except Exception as e:
    print(f"No existing collections found or error checking collections: {e}")

# Explicitly create the mem0 collection with correct vector dimension (384 for all-MiniLM-L6-v2)
try:
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )
    print(f"Created Qdrant collection: {collection_name}")
except Exception as e:
    print(f"Error creating Qdrant collection: {e}")

# Initialize the collection by adding a dummy memory
try:
    mem_client.add([{"role": "system", "content": "Initialize collection"}], user_id="p123")
    print("Initialized Qdrant collection with dummy memory")
except Exception as e:
    print(f"Error initializing Qdrant collection: {e}")

# Verify collection creation
try:
    collections = client.get_collections().collections
    print("Collections after initialization:", [c.name for c in collections])
except Exception as e:
    print(f"Error listing collections: {e}")

# Initialize Neo4j driver for verification
neo4j_driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

groq_client = Groq(api_key=GROQ_API_KEY)

# Retry decorator for handling Groq rate limit errors
@backoff.on_exception(backoff.expo, Exception, max_tries=3, max_time=60)
def call_groq_api(messages):
    return groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages
    )

@backoff.on_exception(backoff.expo, Exception, max_tries=3, max_time=60)
def add_memory(messages, user_id):
    mem_client.add(messages, user_id=user_id)
    print("Successfully added conversation to memory")

def verify_stored_memories():
    """Verify stored memories in Qdrant and Neo4j."""
    try:
        # Check Qdrant points
        points = client.scroll(collection_name=collection_name, limit=10)[0]
        print("Qdrant points:", [p.payload for p in points] if points else "No points found")
    except Exception as e:
        print(f"Error checking Qdrant points: {e}")

    try:
        # Check Neo4j nodes
        with neo4j_driver.session() as session:
            result = session.run("MATCH (n) WHERE n.user_id = $user_id RETURN n LIMIT 10", user_id="p123")
            nodes = [record["n"] for record in result]
            print("Neo4j nodes:", [dict(node) for node in nodes] if nodes else "No nodes found")
    except Exception as e:
        print(f"Error checking Neo4j nodes: {e}")

def chat(message):
    try:
        mem_result = mem_client.search(query=message, user_id="p123")
        print("mem_result:", mem_result)
        memories = "\n".join([m["memory"] for m in mem_result.get("results", [])])
    except Exception as e:
        print(f"Error searching memories: {e}")
        memories = ""

    print(f"\n\nMEMORY:\n\n{memories}\n\n")
    
    SYSTEM_PROMPT = f"""
        You are a Memory-Aware Fact Extraction Agent, an advanced AI designed to
        systematically analyze input content, extract structured knowledge, and maintain an
        optimized memory store. Your primary function is information distillation
        and knowledge preservation with contextual awareness.

        Tone: Professional analytical, precision-focused, with clear uncertainty signaling
        
        Memory and Score:
        {memories}
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message}
    ]

    try:
        result = call_groq_api(messages)
        response_content = result.choices[0].message.content
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        response_content = "Error: Unable to generate response"
        if "rate_limit_exceeded" in str(e):
            print("Rate limit exceeded. Waiting 15 seconds before continuing...")
            time.sleep(15)

    messages.append(
        {"role": "assistant", "content": response_content}
    )

    try:
        add_memory(messages, user_id="p123")
    except Exception as e:
        print(f"Error adding memory: {e}")
        if "rate_limit_exceeded" in str(e):
            print("Rate limit exceeded for memory addition. Waiting 15 seconds before continuing...")
            time.sleep(15)
            try:
                add_memory(messages, user_id="p123")
            except Exception as e:
                print(f"Retry failed for memory addition: {e}")

    # Verify stored memories after adding
    verify_stored_memories()

    return response_content

while True:
    try:
        message = input(">> ")
        print("BOT: ", chat(message=message))
    except KeyboardInterrupt:
        print("\nExiting program...")
        neo4j_driver.close()
        break