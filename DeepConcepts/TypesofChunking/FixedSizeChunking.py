sample_text = """
Introduction

Data Science is an interdisciplinary field that uses scientific methods, processes,
 algorithms, and systems to extract knowledge and insights from structured and 
 unstructured data. It draws from statistics, computer science, machine learning, 
 and various data analysis techniques to discover patterns, make predictions, and 
 derive actionable insights.

Data Science can be applied across many industries, including healthcare, finance,
 marketing, and education, where it helps organizations make data-driven decisions,
  optimize processes, and understand customer behaviors.

Overview of Big Data

Big data refers to large, diverse sets of information that grow at ever-increasing 
rates. It encompasses the volume of information, the velocity or speed at which it 
is created and collected, and the variety or scope of the data points being 
covered.

Data Science Methods

There are several important methods used in Data Science:

1. Regression Analysis
2. Classification
3. Clustering
4. Neural Networks

Challenges in Data Science

- Data Quality: Poor data quality can lead to incorrect conclusions.
- Data Privacy: Ensuring the privacy of sensitive information.
- Scalability: Handling massive datasets efficiently.

Conclusion

Data Science continues to be a driving force in many industries, offering insights 
that can lead to better decisions and optimized outcomes. It remains an evolving 
field that incorporates the latest technological advancements.
"""
def fixed_size_chunk(text, max_words=100):
    words = text.split()
    return [' '.join(words[i:i + max_words]) for i in range(0, len(words), 
    max_words)]

# Applying Fixed-Size Chunking
fixed_chunks = fixed_size_chunk(sample_text)
for i,chunk in enumerate(fixed_chunks, 1)  :
    print(f"Chunk {i}: ({len(chunk)} chars)")
    print(chunk, '\n---\n')