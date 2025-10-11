import numpy as np
from fastapi.testclient import TestClient

from app.main import app, get_embedding_service, get_repository


class FakeEmbeddingService:
    def __init__(self):
        self.records = []

    def encode(self, texts):
        # produce deterministic vectors based on text length
        if isinstance(texts, str):
            texts = [texts]
        embeddings = []
        for text in texts:
            base = len(text)
            embeddings.append(np.full((4,), base / 10.0))
            self.records.append(text)
        return embeddings if len(embeddings) > 1 else embeddings[0]


class FakeRepository:
    def __init__(self):
        self.stored = []
        self.cleared = False

    def add_document(self, content, embedding):
        doc_id = len(self.stored) + 1
        self.stored.append((content, embedding))
        return doc_id

    def batch_add(self, contents, embeddings):
        ids = []
        for content, embedding in zip(contents, embeddings):
            ids.append(self.add_document(content, embedding))
        return ids

    def search_similar(self, query_embedding, limit):
        results = []
        for idx, (content, embedding) in enumerate(self.stored, start=1):
            similarity = float(1 - np.linalg.norm(query_embedding - embedding))
            results.append({"id": idx, "content": content, "score": similarity})
        return results[:limit]

    def clear(self):
        self.stored.clear()
        self.cleared = True


client = TestClient(app)


def setup_function(_):
    fake_embedding = FakeEmbeddingService()
    fake_repo = FakeRepository()
    app.dependency_overrides[get_embedding_service] = lambda: fake_embedding
    app.dependency_overrides[get_repository] = lambda: fake_repo


def teardown_function(_):
    app.dependency_overrides = {}


def test_add_document_creates_single_entry():
    response = client.post("/documents", json={"content": "hello world"})
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1


def test_batch_add_creates_multiple_entries():
    payload = {"contents": ["alpha", "beta"]}
    response = client.post("/documents/batch", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["ids"] == [1, 2]


def test_search_returns_ranked_results():
    # prime repository
    client.post("/documents/batch", json={"contents": ["apple", "banana"]})
    response = client.get("/search", params={"query": "fruit", "limit": 1})
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["content"] in {"apple", "banana"}


def test_clear_removes_documents():
    client.post("/documents", json={"content": "temp"})
    response = client.post("/documents/clear")
    assert response.status_code == 202
    response = client.get("/search", params={"query": "temp"})
    assert response.json()["results"] == []
