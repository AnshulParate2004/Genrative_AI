from langchain_experimental.text_splitter import SemanticChunker
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
########### How SemanticChunker is used ############

# How it works:
# Step 1 Create embeddings:
# Each sentence is converted into a vector embedding
# Step 2- Calculate similarity scores:
# Similarity between sentences 1-2: 0.85 (both about financial results)
# Similarity between sentences 2-3: 78 (both about revenue performance)
# Similarity between sentences 3-4: 8.42 (topic shift: zevenue vehicle sales)
# Similarity between sentences 4-5: 0.71 (both about Model Y performance)
# Step 3- Detect breakpoints:
# The most common breakpoint criteria to decide semantic splitting with SemanticChunker is with "percentiles"
    
# Same Tesla text but structured to show semantic grouping

tesla_text = """Tesla's Q3 Results
Tesla reported record revenue of $25.2B in Q3 2024.
The company exceeded analyst expectations by 15%.
Revenue growth was driven by strong vehicle deliveries.

Model Y Performance  
The Model Y became the best-selling vehicle globally, with 350,000 units sold.
Customer satisfaction ratings reached an all-time high of 96%.
Model Y now represents 60% of Tesla's total vehicle sales.

Production Challenges
Supply chain issues caused a 12% increase in production costs.
Tesla is working to diversify its supplier base.
New manufacturing techniques are being implemented to reduce costs."""

# Semantic Chunker - groups by meaning, not structure
semantic_splitter = SemanticChunker(
    embeddings=GoogleGenerativeAIEmbeddings(model="gemini-embedding-001"),
    breakpoint_threshold_type="percentile",  # or "standard_deviation"
    breakpoint_threshold_amount=70
)

chunks = semantic_splitter.split_text(tesla_text)

print("SEMANTIC CHUNKING RESULTS:")
print("=" * 50)
for i, chunk in enumerate(chunks, 1):
    print(f"Chunk {i}: ({len(chunk)} chars)")
    print(f'"{chunk}"')
    print()