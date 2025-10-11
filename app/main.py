from __future__ import annotations

from contextlib import asynccontextmanager
from typing import List

import numpy as np
from fastapi import Depends, FastAPI, Query, status
from pydantic import BaseModel, Field

from .config import Settings, get_settings
from .db import VectorRepository
from .embeddings import EmbeddingService

_cached_embedding_service: EmbeddingService | None = None
_cached_repository: VectorRepository | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        yield
    finally:
        global _cached_repository
        if _cached_repository is not None:
            _cached_repository.close()
            _cached_repository = None


app = FastAPI(title="Embedding Service", version="0.1.0", lifespan=lifespan)


class DocumentRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10_000)


class BatchDocumentRequest(BaseModel):
    contents: List[str] = Field(..., min_length=1)


class DocumentSummary(BaseModel):
    id: int
    content: str


class SearchResult(BaseModel):
    id: int
    content: str
    score: float


class SearchResponse(BaseModel):
    results: List[SearchResult]


class DocumentIdsResponse(BaseModel):
    ids: List[int]
    count: int


class DocumentIdResponse(BaseModel):
    id: int


def get_embedding_service(settings: Settings = Depends(get_settings)) -> EmbeddingService:
    global _cached_embedding_service
    if _cached_embedding_service is None:
        _cached_embedding_service = EmbeddingService(settings.model_name)
    return _cached_embedding_service


def get_repository(settings: Settings = Depends(get_settings)) -> VectorRepository:
    global _cached_repository
    if _cached_repository is None:
        _cached_repository = VectorRepository(
            settings.database_url, settings.embedding_dimensions
        )
    return _cached_repository


@app.get("/healthz")
async def healthcheck() -> dict:
    return {"status": "ok"}


@app.post("/documents", status_code=status.HTTP_201_CREATED, response_model=DocumentIdResponse)
async def add_document(
    request: DocumentRequest,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    repository: VectorRepository = Depends(get_repository),
) -> DocumentIdResponse:
    embedding = embedding_service.encode(request.content)
    doc_id = repository.add_document(request.content, embedding)
    return DocumentIdResponse(id=doc_id)


@app.post(
    "/documents/batch",
    status_code=status.HTTP_201_CREATED,
    response_model=DocumentIdsResponse,
)
async def batch_add(
    request: BatchDocumentRequest,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    repository: VectorRepository = Depends(get_repository),
) -> DocumentIdsResponse:
    embeddings = embedding_service.encode(request.contents)
    vectors = embeddings if isinstance(embeddings, np.ndarray) else np.asarray(embeddings)
    ids = repository.batch_add(request.contents, vectors)
    return DocumentIdsResponse(ids=ids, count=len(ids))


@app.get("/documents", response_model=List[DocumentSummary])
async def list_documents(
    limit: int = Query(20, ge=1, le=100),
    repository: VectorRepository = Depends(get_repository),
) -> List[DocumentSummary]:
    documents = repository.list_documents(limit)
    return [DocumentSummary(**doc) for doc in documents]


@app.get("/search", response_model=SearchResponse)
async def search(
    query: str = Query(..., min_length=1, max_length=1000),
    limit: int = Query(5, ge=1, le=50),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    repository: VectorRepository = Depends(get_repository),
) -> SearchResponse:
    query_embedding = embedding_service.encode(query)
    results = repository.search_similar(query_embedding, limit)
    formatted = [SearchResult(**result) for result in results]
    return SearchResponse(results=formatted)


@app.post("/documents/clear", status_code=status.HTTP_202_ACCEPTED)
async def clear_documents(
    repository: VectorRepository = Depends(get_repository),
) -> dict:
    repository.clear()
    return {"status": "cleared"}
