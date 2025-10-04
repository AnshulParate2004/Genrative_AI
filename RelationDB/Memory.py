import os
from mem0 import Memory
from groq import Groq
from dotenv import load_dotenv

# ------------------------------
# 0. Load environment variables
# ------------------------------
load_dotenv()

# ------------------------------
# 1. API key for Groq
# ------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("❌ Missing GROQ_API_KEY. Please set it with: setx GROQ_API_KEY 'your_key'")

# ------------------------------
# 2. Database configs
# ------------------------------
QUADRANT_HOST = "localhost"

NEO4J_URL = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "system123"

# ------------------------------
# 3. Memory pipeline config
# ------------------------------
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
        "config": {
            "api_key": GROQ_API_KEY,
            "model": "llama3-70b-8192",
        },
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {"host": QUADRANT_HOST, "port": 6333},
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": NEO4J_URL,
            "username": NEO4J_USERNAME,
            "password": NEO4J_PASSWORD,
            "database": "memorygraph"
        },
    },
}

# ------------------------------
# 4. Initialize clients
# ------------------------------
mem_client = Memory.from_config(config)
groq_client = Groq(api_key=GROQ_API_KEY)

# ------------------------------
# 5. Chat function
# ------------------------------
def chat(message: str):
    # Attempt to search memory safely
    try:
        mem_result = mem_client.search(query=message, user_id="p123")
        memories = "\n".join([m.get("memory", "") for m in mem_result.get("results", [])])
    except Exception as e:
        print(f"⚠️ Memory search failed: {e}")
        memories = ""

    print(f"\n\nMEMORY:\n{memories}\n\n")

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
        {"role": "user", "content": message},
    ]

    # Call Groq LLM safely
    try:
        result = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
        )
        reply = result.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
    except Exception as e:
        print(f"⚠️ LLM call failed: {e}")
        reply = "⚠️ Sorry, I cannot process your request right now."

    # Add conversation to memory safely
    try:
        mem_client.add(messages, user_id="p123")
    except Exception as e:
        print(f"⚠️ Failed to save conversation to memory: {e}")

    return reply

# ------------------------------
# 6. CLI loop
# ------------------------------
if __name__ == "__main__":
    print("Memory-Aware Chat Bot started. Press Ctrl+C to exit.")
    while True:
        try:
            message = input(">> ")
            if message.strip() == "":
                continue
            print("BOT:", chat(message=message))
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
