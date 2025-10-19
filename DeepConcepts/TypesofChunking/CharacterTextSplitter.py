import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

"""
Step 1: Chunking Text Documents after \n\n operator 
Piece 1: "Tesla's Q3 Results" (18 chars)
Piece 2: "Tesla reported record revenue of $25.28 in Q3 2024." (51 chars)
Piece 3: "Model Y Performance" (19 chars)
Piece 4: "The Model Y became the best-selling vehicle globally, with 350,000 units sold." (78 chars)
Piece 5: "Production Challenges" (21 chars)
Piece 6: "Supply chain issues caused a 12% increase in production costs." (62 chars)

Step 2 Merge until chunk_size (let's say 100 chars):
Final Chunk 1 "Tesla's Q3 Results Tesla reported record revenue of 525.28 in Q3 2024 Podel X Performance" (92 chars)
Chunk 2: "The nodel Y became the best-selling vehicle globally, with 350,000 units sold." (70 chars)
Chunk 3: "Production Challengeset Supply chain issues caused a 12% increase in production costs." (85 chazs)
"""

def split_documents(documents, chunk_size=100, chunk_overlap=0):
    """Split documents into smaller chunks with overlap"""
    print("Splitting documents into chunks...")
    
    text_splitter = CharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap,
        separator="\n\n"
    )
    
    chunks = text_splitter.split_documents(documents)
    
    if chunks:
    
        for i, chunk in enumerate(chunks[:5]):
            print(f"\n--- Chunk {i+1} ---")
            print(f"Source: {chunk.metadata['source']}")
            print(f"Length: {len(chunk.page_content)} characters")
            print(f"Content:")
            print(chunk.page_content)
            print("-" * 50)
        
        if len(chunks) > 5:
            print(f"\n... and {len(chunks) - 5} more chunks")
    
    return chunks
