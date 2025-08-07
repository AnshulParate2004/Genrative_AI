# fanout_rag.py

from langchain.vectorstores import FAISS, Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from typing import List, Set
import threading

# Abstract retriever interface
class BaseRetriever:
    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        raise NotImplementedError()

# FAISS retriever
class FAISSRetriever(BaseRetriever):
    def __init__(self, faiss_index: FAISS):
        self.index = faiss_index

    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        return self.index.similarity_search(query, k=k)

# Chroma retriever
class ChromaRetriever(BaseRetriever):
    def __init__(self, chroma_index: Chroma):
        self.index = chroma_index

    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        return self.index.similarity_search(query, k=k)

# Fan-out retriever
class FanOutRetriever:
    def __init__(self, retrievers: List[BaseRetriever]):
        self.retrievers = retrievers

    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        results = []
        threads = []
        lock = threading.Lock()

        def fetch(r):
            docs = r.retrieve(query, k)
            with lock:
                results.extend(docs)

        for retriever in self.retrievers:
            t = threading.Thread(target=fetch, args=(retriever,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        return self.filter_unique(results)

    def filter_unique(self, docs: List[Document]) -> List[Document]:
        seen: Set[str] = set()
        unique_docs = []
        for doc in docs:
            content = doc.page_content.strip()
            if content not in seen:
                unique_docs.append(doc)
                seen.add(content)
        return unique_docs

# Main execution
def main():
    # Init embedding model
    embedding = OpenAIEmbeddings()

    # Load your vector stores
    faiss_index = FAISS.load_local("faiss_index", embeddings=embedding)
    chroma_index = Chroma(persist_directory="chroma_index", embedding_function=embedding)

    # Create retrievers
    retrievers = [
        FAISSRetriever(faiss_index),
        ChromaRetriever(chroma_index),
    ]

    fanout = FanOutRetriever(retrievers)

    # Example query
    query = "What are the benefits of parallel computing?"
    results = fanout.retrieve(query, k=5)

    # Print output
    for i, doc in enumerate(results):
        print(f"Doc {i+1}:\n{doc.page_content}\n{'-'*40}")

if __name__ == "__main__":
    main()
