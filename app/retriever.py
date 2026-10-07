"""Tiny keyword retriever over the markdown knowledge base."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path

KB_DIR = Path(__file__).resolve().parent.parent / "knowledge_base"

STOPWORDS = {
    "a", "an", "the", "is", "are", "am", "was", "were", "be", "been", "do", "does",
    "did", "i", "you", "your", "my", "me", "we", "our", "it", "its", "to", "of",
    "in", "on", "for", "with", "and", "or", "can", "could", "how", "what", "when",
    "which", "who", "where", "why", "there", "this", "that", "if", "at", "by",
    "from", "as", "any", "much", "many", "have", "has", "will", "would", "should",
    "per", "each", "about", "need", "get", "use", "not", "no", "so", "than",
}


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    out = []
    for t in tokens:
        if t in STOPWORDS:
            continue
        if len(t) > 3 and t.endswith("s") and not t.endswith("ss"):
            t = t[:-1]  # naive plural stripping: fees -> fee
        out.append(t)
    return out


@dataclass(frozen=True)
class Chunk:
    source: str
    text: str


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float


class Retriever:
    def __init__(self, kb_dir: Path = KB_DIR):
        self.chunks: list[Chunk] = []
        for path in sorted(kb_dir.glob("*.md")):
            for para in path.read_text(encoding="utf-8").split("\n\n"):
                para = para.strip()
                if para and not para.startswith("#"):
                    self.chunks.append(Chunk(source=path.name, text=para))

        self._tokens = [set(tokenize(c.text)) for c in self.chunks]

        n = len(self.chunks)
        df: dict[str, int] = {}
        for toks in self._tokens:
            for t in toks:
                df[t] = df.get(t, 0) + 1
        self._idf = {t: math.log((n + 1) / (d + 0.5)) for t, d in df.items()}

    def search(self, question: str, k: int = 3) -> list[Hit]:
        q = set(tokenize(question))
        hits = []
        for chunk, toks in zip(self.chunks, self._tokens):
            score = sum(self._idf.get(t, 0.0) for t in q & toks)
            if score > 0:
                hits.append(Hit(chunk, round(score, 3)))
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:k]