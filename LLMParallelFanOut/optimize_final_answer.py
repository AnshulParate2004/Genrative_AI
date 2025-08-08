import json
import requests

# === CONFIG ===
load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

MODEL_NAME = "llama3-70b-8192"
JSON_PATH = r"D:\Genrative_AI\LLMParallelFanOut\multillm_results.json"

def synthesize_final_answer(variant_key, question, all_answers):
    combined_finals = ""
    for model, info in all_answers.items():
        final = info.get("final", "").strip()
        confidence = info.get("confidence", "unknown")
        combined_finals += f"[{model} | Confidence: {confidence}]: {final}\n\n"

    system_prompt = f"""
You are a reasoning engine designed to synthesize the best possible answer to a user's question using outputs from multiple language models.

You will be given:
- A user question
- An array of final answers from various LLMs
- Each answer has an associated confidence score: "high", "medium", or "low"

Your task:
1. Understand the question fully.
2. Read all final answers and analyze them carefully.
3. Weigh answers with "high" confidence more heavily, but don't ignore useful insights from others.
4. Create ONE optimized final answer that combines the most accurate, complete, and relevant points.
5. Remove any contradictions or redundancy.
6. Your output must be a JSON object, containing only one key called "final_answer".

Output format:
{{
  "final_answer": "Your optimized final answer goes here."
}}

Do NOT include:
- Confidence ratings
- Model names
- Any bullet points or explanation about how you chose the answer
Only return the JSON object with your best final answer.
"""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Synthesize a final answer for: {question}\n\n{combined_finals}"}
        ],
        "temperature": 0.3,
        "max_tokens": 500
    }

    resp = requests.post(BASE_URL, headers=HEADERS, json=payload)
    resp.raise_for_status()
    reply = resp.json()["choices"][0]["message"]["content"].strip()
    return reply

# === Run for all questions ===
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

optimized_results = {}

for variant_type, question in data["variants"].items():
    print(f"\n--- Optimizing for: {variant_type} ---")
    answers = data["responses"].get(variant_type, {})
    final_output = synthesize_final_answer(variant_type, question, answers)
    print(f"✅ Final Answer:\n{final_output}")
    optimized_results[variant_type] = {
        "question": question,
        "optimized_final": final_output
    }

# Save the new file
with open("optimized_llm_final_answers.json", "w", encoding="utf-8") as f:
    json.dump(optimized_results, f, indent=2, ensure_ascii=False)

print("\n📁 Saved synthesized results to optimized_llm_final_answers.json")
