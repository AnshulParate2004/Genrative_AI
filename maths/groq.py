import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")  # Your Groq API key

def solve_math_problem(user_problem):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    SYSTEM_PROMPT = f"""
    You are a highly skilled math problem solver.
    Given a math problem, provide:
    1. A clear, logical step-by-step solution (human-readable).
    2. The final numeric or symbolic answer.

    Output format:
    {{
        "problem": "Original math problem",
        "solution_steps": "Step-by-step explanation",
        "final_answer": "Answer only"
    }}

    Rules:
    - Always return valid JSON only, no extra commentary.
    - Ensure mathematical correctness.
    - Show steps clearly.
    """

    payload = {
        "model": "DeepSeek-R1-Distill-Llama-70B",  # Good free reasoning model
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_problem}
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"}
    }

    response = requests.post(url, headers=headers, json=payload)
    result = response.json()

    try:
        return json.loads(result["choices"][0]["message"]["content"])
    except (KeyError, json.JSONDecodeError):
        return {"error": "Failed to parse response", "raw": result}

if __name__ == "__main__":
    user_input = input("Enter your math problem: ")
    result = solve_math_problem(user_input)

    print("\nMath Solution:")
    print(json.dumps(result, indent=4))

    file_path = "math_solution.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Solution saved to {os.path.abspath(file_path)}")
