from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter




####################### How CharacterTextSplitter works #############
"""
In this approch ,same as CharacterTextSplitter, we split text based on specified character limits.
However, RecursiveCharacterTextSplitter improves upon this by using a hierarchy of separators to find optimal split points.
It first attempts to split using larger separators (like double newlines) before falling back to smaller ones (like spaces or no separator).
This ensures that chunks are more semantically coherent and reduces the chances of splitting in the middle of sentences or important phrases.
"""







tesla_text = """Tesla's Q3 Results

Tesla reported record revenue of $25.2B in Q3 2024.

Model Y Performance

The Model Y became the best-selling vehicle globally, with 350,000 units sold.

Production Challenges

Supply chain issues caused a 12% increase in production costs.

This is one very long paragraph that definitely exceeds our 100 character limit and has no double newlines inside it whatsoever making it impossible to split properly."""


# splitter1 = CharacterTextSplitter(
#     separator=" ",  # Default separator. Other options include ["\n\n", "\n", ". ", " ", ""]
#     chunk_size=100,
#     chunk_overlap=0
# )

# chunks1 = splitter1.split_text(tesla_text)
# for i, chunk in enumerate(chunks1, 1):
#     print(f"Chunk {i}: ({len(chunk)} chars)")
#     print(f'"{chunk}"')
#     print()



# Example 2: RecursiveCharacterTextSplitter fixes this
print("\n" + "=" * 60)
print("2. RECURSIVE CHARACTER TEXT SPLITTER SOLUTION")
print("=" * 60)

recursive_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", ". ", " ", ""],  # Multiple separators
    chunk_size=100,
    chunk_overlap=0
)

chunks2 = recursive_splitter.split_text(tesla_text)
print(f"Same problem text, but with RecursiveCharacterTextSplitter:")
for i, chunk in enumerate(chunks2, 1):
    print(f"Chunk {i}: ({len(chunk)} chars)")
    print(f'"{chunk}"')
    print()