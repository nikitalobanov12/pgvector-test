"""Utilities for working with embedding models."""

from __future__ import annotations

from typing import Sequence

import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Thin wrapper around SentenceTransformer with convenience helpers."""

    def __init__(self, model_name: str) -> None:
        self._model = SentenceTransformer(model_name)

    def encode(self, texts: Sequence[str] | str) -> np.ndarray:
        if isinstance(texts, str):
            return self._model.encode([texts])[0]
        return self._model.encode(list(texts))
