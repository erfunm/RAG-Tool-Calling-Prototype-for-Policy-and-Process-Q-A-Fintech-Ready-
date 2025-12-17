"""Simple document store with TF-IDF retrieval for policy/process content."""
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class DocumentChunk:
    """Represents a chunked document unit."""

    doc_id: str
    text: str
    metadata: dict


class DocumentStore:
    """Loads, chunks, embeds, and retrieves documents."""

    def __init__(self, config_path: str = "configs/default.yaml") -> None:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        retrieval_cfg = config.get("retrieval", {})
        self.data_path = Path(retrieval_cfg.get("data_path", "data/documents"))
        self.chunk_size = int(retrieval_cfg.get("chunk_size", 120))
        self.similarity_threshold = float(retrieval_cfg.get("similarity_threshold", 0.1))
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.matrix = None
        self.chunks: List[DocumentChunk] = []
        self._load()

    def _load(self) -> None:
        documents = []
        for file_path in sorted(self.data_path.glob("*.txt")):
            text = file_path.read_text(encoding="utf-8")
            documents.append((file_path.stem, text))
        for doc_id, text in documents:
            for chunk_text in self._chunk_text(text):
                self.chunks.append(
                    DocumentChunk(doc_id=doc_id, text=chunk_text, metadata={"source": doc_id})
                )
        corpus = [chunk.text for chunk in self.chunks]
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(corpus)

    def _chunk_text(self, text: str) -> List[str]:
        words = text.split()
        return [" ".join(words[i : i + self.chunk_size]) for i in range(0, len(words), self.chunk_size)]

    def search(self, query: str, k: int = 3) -> List[Tuple[DocumentChunk, float]]:
        if not self.vectorizer or self.matrix is None:
            return []
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix)[0]
        scored = list(zip(self.chunks, scores))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]

    def has_sufficient_evidence(self, scored_chunks: List[Tuple[DocumentChunk, float]]) -> bool:
        if not scored_chunks:
            return False
        top_score = scored_chunks[0][1]
        return top_score >= self.similarity_threshold
