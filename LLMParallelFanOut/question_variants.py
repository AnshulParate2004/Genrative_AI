import requests
import json
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")

def generate_question_variants(user_query):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    SYSTEM_PROMPT = f"""

    You are a specialized Question Transformation AI.

    Your task is to take the input question from the user and produce THREE variations:

    1. ORIGINAL QUESTION (Normal):
       - Keep the question as given but fix grammar, spelling, and capitalization errors.
       - Do not change the meaning or rephrase beyond minor corrections.

    2. MORE ABSTRACT QUESTION:
       - Make the question more general.
       - Remove unnecessary specifics and details.
       - Widen the scope so it could apply to more situations.
       - Keep the core meaning, but avoid overly niche references.

    3. LESS ABSTRACT QUESTION (More Detailed):
       - Make the question more specific and concrete.
       - Add relevant context, examples, or constraints that narrow its scope.
       - Replace vague terms with precise, descriptive phrases.
       - Keep the original intent but make it harder to apply to unrelated topics.

    Formatting rules:
       - Return the output strictly as valid JSON with keys: "original", "abstract", "detailed".
       - Each value must be a single, clear question ending with a question mark.
       - Do not include any extra text, explanations, or notes outside of the JSON.

    Example JSON output:
    {{
        "original": "What is machine learning?",
        "abstract": "How does machine learning work?",
        "detailed": "What are the main types of machine learning algorithms and how are they applied in real-world scenarios?"
    }}

    The user's question is: "{user_query}"
    """

    payload = {
        "model": "llama-3.3-70b-versatile",  # Best reasoning & language quality
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"}
    }

    response = requests.post(url, headers=headers, json=payload)
    result = response.json()

    try:
        return json.loads(result["choices"][0]["message"]["content"])
    except (KeyError, json.JSONDecodeError):
        return {"error": "Failed to parse response", "raw": result}

if __name__ == "__main__":
    user_input = input("Enter your question: ")
    variants = generate_question_variants(user_input)

    print("\nGenerated Question Variants:")
    print(json.dumps(variants, indent=4))

    # Save to file
    file_path = "questions.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(variants, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Questions saved to {os.path.abspath(file_path)}")
