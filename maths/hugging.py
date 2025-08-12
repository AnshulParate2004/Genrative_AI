import os
import json
import requests
from dotenv import load_dotenv

# Load HF token from .env
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found in .env file")

# Working small model (math + reasoning capable)
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# Math problem
problem = "Solve 2x + 5 = 15"

# Make request
response = requests.post(API_URL, headers=headers, json={"inputs": problem})

if response.status_code == 200:
    result = response.json()

    # Save result to JSON file
    with open("math_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print("✅ Response saved to math_result.json")
else:
    print(f"❌ Error {response.status_code}: {response.text}")
