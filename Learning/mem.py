from mem0 import Memory

GROQ_API_KEY = "your-groq-api-key"

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "sentence-transformers/all-MiniLM-L6-v2",
        },
    },
    "llm": {
        "provider": "groq",
        "config": {
            "api_key": GROQ_API_KEY,
            "model": "llama3-70b-8192",
        },
    },
    "graph_store": {
        "provider": "memgraph",
        "config": {
            "url": "bolt://localhost:7687",
            "username": "memgraph",
            "password": "yourStrongPassword",
        },
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "url": "http://localhost:6333",
        },
    },
}

memory = Memory.from_config(config)

# Example:
memory.add("The Eiffel Tower is in Paris.", user_id="default")
print(memory.search("Where is the Eiffel Tower?", user_id="default"))
