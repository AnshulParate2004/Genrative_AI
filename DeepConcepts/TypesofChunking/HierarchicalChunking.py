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
def hierarchical_chunk(text, section_keywords):
    sections = []
    current_section = []
    for line in text.splitlines():
        if any(keyword in line for keyword in section_keywords):
            if current_section:
                sections.append("\n".join(current_section))
            current_section = [line]
        else:
            current_section.append(line)
    if current_section:
        sections.append("\n".join(current_section))
    return sections

# Applying Hierarchical Chunking
section_keywords = ["Introduction", "Overview", "Methods", "Conclusion"]
for i, chunk in enumerate(section_keywords, 1):
    print(f"Chunk {i}: ({len(chunk)} chars)")
    print(f'"{chunk}"')
    print()
    