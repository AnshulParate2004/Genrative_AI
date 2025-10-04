from mem0 import Memory
from groq import Groq
from qdrant_client import QdrantClient
import time
import backoff
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
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
    "llm": {
        "provider": "groq",
        "config": {"api_key": GROQ_API_KEY, "model": "llama3-70b-8192"}
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {"host": QUADRANT_HOST, "port": 6333},
    },
}

# Just connect — don't delete/create
mem_client = Memory.from_config(config)
client = QdrantClient(host=QUADRANT_HOST, port=6333)
collection_name = "mem0"

groq_client = Groq(api_key=GROQ_API_KEY)

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
    try:
        points = client.scroll(collection_name=collection_name, limit=10)[0]
    except Exception as e:
        print(f"Error checking Qdrant points: {e}")

def chat(message):
    try:
        mem_result = mem_client.search(query=message, user_id="p123")
        memories = "\n".join([m["memory"] for m in mem_result.get("results", [])])
    except Exception as e:
        print(f"Error searching memories: {e}")
        memories = ""

    print(f"\n\nMEMORY:\n\n{memories}\n\n")
    
    SYSTEM_PROMPT = f"""
        You are a Memory-Aware Fact Extraction Agent.
        Tone: Professional analytical, precision-focused.
        
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

    messages.append({"role": "assistant", "content": response_content})

    try:
        add_memory(messages, user_id="p123")
    except Exception as e:
        print(f"Error adding memory: {e}")

    verify_stored_memories()
    return response_content

if __name__ == "__main__":
    while True:
        try:
            message = input(">> ")
            print("BOT: ", chat(message=message))
        except KeyboardInterrupt:
            print("\nExiting program...")
            break
