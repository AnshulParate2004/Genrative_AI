from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",  # Replace securely!
)

system_prompt = """
You are an AI Assistant that answers all questions — math, factual, philosophical, or otherwise — using this 5-step method. For each step, include an emoji:



Examples:

Example 1 (Math):
Input: What is 2 + 2?
Output:
Analyze: The question asks to add 2 and 2.
Thinking: 2 + 2 = 4.
Output: The answer is 4.
Validate: Addition is straightforward; 4 is correct.
Result: Therefore, 2 + 2 = 4.

Example 2 (Factual):
Input: Why is the sky blue?
Output:
Analyze: The question asks about the reason behind the sky's blue color.
Thinking: Blue light has a shorter wavelength and is scattered more by Earth's atmosphere (Rayleigh scattering).
Output: The sky appears blue due to Rayleigh scattering of sunlight by the atmosphere.
Validate: This explanation is consistent with scientific understanding.
Result: Therefore, the sky is blue because of atmospheric scattering of blue light.

Example 3 (Philosophical/Emotional):
Input: What is love?
Output:
Analyze: The question seeks to understand the concept or nature of love.
Thinking: Love is a deep emotional state involving affection, attachment, and care, expressed in different forms.
Output: Love is a complex emotional experience that includes romantic, familial, platonic, and self-love.
Validate: This view is supported by psychology, literature, and human experience.
Result: Therefore, love is a multifaceted emotion expressed through connection and care.
"""


def ask_question(question: str) -> str:
    messages = [
    {"role": "system", "content": "You are an AI assistant that answers all questions using a 5-step method."},

    {"role": "assistant", "content": "🧠 Analyze: Understand what the question is asking."},
    {"role": "assistant", "content": "🧩 Thinking: Consider relevant facts, concepts, or reasoning."},
    {"role": "assistant", "content": "🤖 Output: Provide a clear and concise answer."},
    {"role": "assistant", "content": "🔍 Validate: Check that the answer is logical or supported by reasoning or evidence."},
    {"role": "assistant", "content": "✅ Result: Summarize the final answer clearly."},

    {"role": "user", "content": question},
    ]

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=1000,
        temperature=0.4
    )
    return completion.choices[0].message.content.strip()


if __name__ == "__main__":
    print("Smart AI Assistant (5-Step Methodology)")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("Your question: ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

    
        print(f"\nUser Question: {user_input}\n")

        response = ask_question(user_input)
        print("AI Response:\n" + response)
        print("\n" + "=" * 60 + "\n")
