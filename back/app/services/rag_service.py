import glob
import os
import re

from app.gateway import fetch_advisor_completion, fetch_embedding

_KB_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")

# In-memory cache: each entry is {"text": ..., "source": ..., "embedding": [...]}
_index: list[dict] = []


def _chunk_text(text: str, source: str) -> list[dict]:
    """Split a knowledge file into smaller paragraphs for better retrieval."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if len(paragraphs) <= 1:
        # Also split long single blocks into ~2–3 sentence chunks
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        paragraphs = []
        buf: list[str] = []
        for sentence in sentences:
            buf.append(sentence)
            if len(buf) >= 2:
                paragraphs.append(" ".join(buf))
                buf = []
        if buf:
            paragraphs.append(" ".join(buf))

    return [{"text": chunk, "source": source} for chunk in paragraphs if chunk]


def build_index() -> None:
    """Read every .txt file in knowledge_base/, chunk it, embed, and cache."""
    global _index
    _index = []
    for filepath in glob.glob(os.path.join(_KB_DIR, "*.txt")):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read().strip()
        if not text:
            continue
        source = os.path.basename(filepath)
        for chunk in _chunk_text(text, source):
            _index.append({
                "text": chunk["text"],
                "source": chunk["source"],
                "embedding": fetch_embedding(f"search_document: {chunk['text']}"),
            })


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Measure how close two vectors point in the same direction — 1 = identical
    meaning, 0 = unrelated, -1 = opposite. This is the standard way to compare embeddings."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def retrieve_relevant(question: str, top_k: int = 4) -> list[dict]:
    """Find the top_k knowledge base chunks closest in meaning to the question."""
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
    context_blocks = [
        f"[Source: {entry['source']}]\n{entry['text']}"
        for entry in relevant
    ]
    context = "\n\n---\n\n".join(context_blocks)
    # Preserve source order, unique
    sources: list[str] = []
    for entry in relevant:
        if entry["source"] not in sources:
            sources.append(entry["source"])

    prompt = f"""You are a helpful aviation assistant for Flight Assistant.
Answer ONLY using the context below. Do not invent airline policies or facts.
If the context does not contain enough information, say clearly what is missing.
Be concise: 2–5 short sentences, plain language, no fluff.

Context:
{context}

Question: {question}

Answer:"""

    answer = fetch_advisor_completion(prompt)
    return answer.strip(), sources
