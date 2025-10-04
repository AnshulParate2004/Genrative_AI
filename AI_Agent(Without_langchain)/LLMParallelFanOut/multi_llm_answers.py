# multi_llm_answers_with_system.py
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import os

# === CONFIG ===
load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

SYSTEM_PROMPT_TEMPLATE = """

You are a disciplined, multi-stage reasoning assistant. For every user question — whether it is typed directly or loaded from a file path provided by the system — you must strictly follow the workflow below and return ONLY a valid JSON object. 

### REQUIRED JSON KEYS
- "model": The model name you are using.
- "user_question": Exact question received from the user (as provided in input, regardless of source).
- "draft": A short initial attempt at answering (1–2 sentences).
- "analysis": A concise (≤40 words) list of main assumptions, uncertainties, or weaknesses in the draft. Do NOT include internal step-by-step reasoning; this is a short summary of limitations.
- "revision": An improved/corrected answer (2–4 sentences) that addresses issues found in the analysis.
- "final": A clear, concise final answer for the user (≤150 words).
- "confidence": One of ["high", "medium", "low"] — your self-assessed confidence in the final answer.
- "sources": A short list of sources used OR "common knowledge" if none.

### RULES
1. The question may be loaded from a file path — treat it the same as any direct user question.
2. All values must be plain text (no formatting, no markdown).
3. Output exactly one JSON object — no extra characters before or after {{{{}}}}.
4. Keep "analysis" brief and factual — no hidden reasoning or speculative chains-of-thought.
5. If any part of the answer is uncertain, explicitly say so in "analysis" and adjust "confidence".
6. Ensure the JSON is syntactically valid and can be parsed without errors.

The user's question is: "{user_query}"

Follow the workflow: create "draft" → identify issues in "analysis" → fix in "revision" → produce the concise "final".


Example JSON output:
{{
  "model": "llama3-8b",
  "user_question": "What is inline function in Java?",
  "thinking": "This seems related to Java method inlining and compiler optimization.",
  "analysis": "Inline functions in Java are not like C++; Java relies on the JIT compiler for inlining.",
  "draft": "An inline function in Java is a request to the JVM to replace a method call with the method body.",
  "revision": "Java does not have explicit inline functions; the JIT compiler automatically inlines methods at runtime to improve performance.",
  "final": "In Java, there is no explicit 'inline' keyword like C++. Instead, the JVM's Just-In-Time (JIT) compiler decides at runtime whether to inline a method call, enhancing performance without programmer intervention.",
  "confidence": "high",
  "sources": "common knowledge"
}}

The user's question is: "{user_query}"

Follow the workflow: create "draft" → identify issues in "analysis" → fix in "revision" → produce the concise "final".



User query will be provided as the user message. Use the workflow: produce a quick "draft", then a concise "analysis", then a "revision" that fixes issues, then a short "final" answer.
"""

MODELS = [
    "llama3-70b-8192",
    "llama-3.3-70b-versatile",
    "gemma2-9b-it"
]

# === Helpers ===
def call_model(model, question, temperature=0.2, max_tokens=800):
    prompt = SYSTEM_PROMPT_TEMPLATE.format(user_query=question)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": question}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    resp = requests.post(BASE_URL, headers=HEADERS, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    text = data["choices"][0]["message"]["content"]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end+1])
            except Exception:
                pass
        return {
            "draft": "",
            "analysis": "",
            "revision": "",
            "final": text.strip(),
            "confidence": "low",
            "parse_error": True
        }

def ask_all_models_for_question(question, models):
    results = {}
    with ThreadPoolExecutor(max_workers=min(6, len(models))) as ex:
        futures = {ex.submit(call_model, m, question): m for m in models}
        for fut in as_completed(futures):
            model = futures[fut]
            try:
                results[model] = fut.result()
            except Exception as e:
                results[model] = {"error": str(e)}
    return results

# === Main ===
if __name__ == "__main__":
    input_file = r"D:\Genrative_AI\LLMParallelFanOut\questions.json"
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            variants = json.load(f)
    except Exception as e:
        print(f"Error reading file: {e}")
        raise SystemExit(1)

    print("\nQUESTION VARIANTS LOADED:")
    print(json.dumps(variants, indent=2, ensure_ascii=False))

    overall = {}
    for vtype, qtext in variants.items():
        print(f"\nAsking models for variant: {vtype} -> {qtext}")
        answers = ask_all_models_for_question(qtext, MODELS)
        overall[vtype] = answers
        for m, out in answers.items():
            if isinstance(out, dict):
                final = out.get("final") or out.get("draft") or str(out)
                parse_err = out.get("parse_error", False)
                print(f"\n[{m}] final (conf={out.get('confidence')} parse_err={parse_err}):\n{final}\n")
            else:
                print(f"\n[{m}] raw:\n{out}\n")

    with open("multillm_results.json", "w", encoding="utf-8") as f:
        json.dump({"variants": variants, "responses": overall}, f, ensure_ascii=False, indent=2)

    print("\nSaved results to multillm_results.json")
