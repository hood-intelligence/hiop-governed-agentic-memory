"""Lightweight deterministic embeddings for CRDB vector memory demos.

Production would use Bedrock Titan / SageMaker. This keeps offline demos
repeatable while still exercising FLOAT8[] storage + cosine recall in SQL.
"""

from __future__ import annotations

import hashlib
import math
import re


DIM = 8


def embed_text(text: str, dim: int = DIM) -> list[float]:
    tokens = re.findall(r"[a-z0-9]+", (text or "").lower())
    vec = [0.0] * dim
    if not tokens:
        return vec
    for tok in tokens:
        h = hashlib.sha256(tok.encode("utf-8")).digest()
        for i in range(dim):
            vec[i] += (h[i % len(h)] - 128) / 128.0
    # L2 normalize
    n = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / n for v in vec]


def cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b))
