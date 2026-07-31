import glob
import os

from app.gateway import fetch_advisor_completion, fetch_embedding

_KB_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")

# In-memory cache: each entry is {"text": ..., "source": ..., "embedding": [...]}
_index: list[dict] = []


def build_index() -> None:
    """Read every .txt file in knowledge_base/, compute its embedding, and cache it."""
    global _index
    _index = []
    for filepath in glob.glob(os.path.join(_KB_DIR, "*.txt")):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read().strip()
        _index.append({
            "text": text,
            "source": os.path.basename(filepath),
            "embedding": fetch_embedding(f"search_document: {text}"),
        })


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Measure how close two vectors point in the same direction — 1 = identical
    meaning, 0 = unrelated, -1 = opposite. This is the standard way to compare embeddings."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    return dot / (norm_a * norm_b)


def retrieve_relevant(question: str, top_k: int = 3) -> list[dict]:
    """Find the top_k knowledge base entries closest in meaning to the question."""
    if not _index:
        build_index()

    question_embedding = fetch_embedding(f"search_query: {question}")
    scored = [
        (entry, _cosine_similarity(question_embedding, entry["embedding"]))
        for entry in _index
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return [entry for entry, _ in scored[:top_k]]


def answer_question(question: str) -> tuple[str, list[str]]:
    """The RAG pipeline: retrieve relevant knowledge, inject it into the prompt,
    ask the LLM to answer using that context."""
    relevant = retrieve_relevant(question)
    context = "\n\n".join(entry["text"] for entry in relevant)
    sources = [entry["source"] for entry in relevant]

    prompt = f"""You are an aviation domain expert assistant. Use the following context to answer the user's question. If the context doesn't contain the answer, say so honestly rather than making things up.

Context:
{context}

Question: {question}

Answer:"""

    answer = fetch_advisor_completion(prompt)
    return answer, sources