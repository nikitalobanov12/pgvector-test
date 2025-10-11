"""Database access layer for vector operations."""

from __future__ import annotations

from typing import Iterable, List, Sequence

import numpy as np
from pgvector.psycopg import register_vector
from psycopg_pool import ConnectionPool


class VectorRepository:
    """Persistence layer backed by PostgreSQL + pgvector."""

    def __init__(self, dsn: str, embedding_dimensions: int, *, pool_size: int = 5) -> None:
        self._embedding_dimensions = embedding_dimensions

        def configure(connection):
            register_vector(connection)

        self._pool = ConnectionPool(
            conninfo=dsn,
            max_size=pool_size,
            configure=configure,
        )

    def _coerce_embedding(self, embedding: Sequence[float] | np.ndarray) -> List[float]:
        vector = embedding.tolist() if isinstance(embedding, np.ndarray) else list(embedding)
        if len(vector) != self._embedding_dimensions:
            raise ValueError(
                f"Embedding has {len(vector)} dimensions, expected {self._embedding_dimensions}."
            )
        return vector

    def add_document(self, content: str, embedding: Sequence[float] | np.ndarray) -> int:
        vector = self._coerce_embedding(embedding)
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO documents (content, embedding) VALUES (%s, %s) RETURNING id",
                    (content, vector),
                )
                doc_id = cur.fetchone()[0]
                conn.commit()
                return int(doc_id)

    def batch_add(
        self, contents: Sequence[str], embeddings: Iterable[Sequence[float] | np.ndarray]
    ) -> List[int]:
        vectors = [self._coerce_embedding(embedding) for embedding in embeddings]
        ids: List[int] = []
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                for content, vector in zip(contents, vectors):
                    cur.execute(
                        "INSERT INTO documents (content, embedding) VALUES (%s, %s) RETURNING id",
                        (content, vector),
                    )
                    ids.append(int(cur.fetchone()[0]))
                conn.commit()
        return ids

    def search_similar(
        self, query_embedding: Sequence[float] | np.ndarray, limit: int
    ) -> List[dict]:
        vector = self._coerce_embedding(query_embedding)
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, content, 1 - (embedding <=> %s) AS similarity
                    FROM documents
                    ORDER BY embedding <=> %s
                    LIMIT %s
                    """,
                    (vector, vector, limit),
                )
                rows = cur.fetchall()
        return [
            {"id": int(row[0]), "content": row[1], "score": float(row[2])}
            for row in rows
        ]

    def clear(self) -> None:
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM documents")
                conn.commit()

    def list_documents(self, limit: int = 20) -> List[dict]:
        with self._pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, content FROM documents ORDER BY id DESC LIMIT %s",
                    (limit,),
                )
                rows = cur.fetchall()
        return [{"id": int(row[0]), "content": row[1]} for row in rows]

    def close(self) -> None:
        self._pool.close()
