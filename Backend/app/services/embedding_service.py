"""
Embedding Service — RAG Pipeline for study material vector search.

Vector search strategy (two-tier with automatic fallback):

  PRIMARY (MongoDB Atlas / MongoDB 7.0+ with $vectorSearch):
    O(log n) — uses HNSW index on the `embedding` field.
    Requires a Vector Search index named "study_material_vector_index" on the
    `study_material_embeddings` collection.
    See: https://www.mongodb.com/docs/atlas/atlas-vector-search/create-index/

  FALLBACK (self-hosted MongoDB, local dev):
    Fetches all documents for the subject and computes cosine similarity using
    NumPy matrix operations — a single (N, D) @ (D,) multiply scores all
    documents in one pass.  Acceptable for ≤ 5 000 documents per subject.

Cache layer:
  Results for the same (subject_id, query_text) are cached in Redis for 1 hour.
  Cache is invalidated when a new study material is uploaded (call
  `invalidate_rag_cache(subject_id)` from the upload endpoint).
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np

from app.infrastructure.ai import get_nvidia_client
from app.core.cache import get_cached, invalidate_pattern, rag_search_key, set_cached
from app.core.logging import get_logger

logger = get_logger(__name__)

EMBEDDING_MODEL = "nvidia/nv-embed-v1"
_ATLAS_INDEX_NAME = "study_material_vector_index"
# NVIDIA nv-embed-v1 giới hạn 4096 token; PDF tiếng Việt ~1.5 ký tự/token → chunk ~4000 ký tự
_MAX_EMBED_CHARS = 4_000


def _chunk_text_for_embedding(text: str, max_chars: int = _MAX_EMBED_CHARS) -> List[str]:
    """Chia văn bản dài thành các đoạn nhỏ hơn giới hạn embedding API."""
    import re

    cleaned = text.strip()
    if not cleaned:
        return []
    if len(cleaned) <= max_chars:
        return [cleaned]

    chunks: List[str] = []
    paragraphs = re.split(r"\n\s*\n", cleaned)
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(para) > max_chars:
            if current.strip():
                chunks.append(current.strip())
                current = ""
            for i in range(0, len(para), max_chars):
                chunks.append(para[i : i + max_chars])
            continue
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) > max_chars:
            if current.strip():
                chunks.append(current.strip())
            current = para
        else:
            current = candidate

    if current.strip():
        chunks.append(current.strip())
    return chunks or [cleaned[:max_chars]]


# ── Embedding generation ───────────────────────────────────────────────────────

def get_embedding(text: str) -> List[float]:
    """Generate a vector embedding via NVIDIA NIM (synchronous)."""
    if not text.strip():
        return [0.0] * 4096

    client = get_nvidia_client()
    try:
        response = client.embeddings.create(input=[text], model=EMBEDDING_MODEL)
        return response.data[0].embedding
    except Exception as exc:
        raise RuntimeError(f"Lỗi khi sinh vector embedding từ NVIDIA NIM: {exc}") from exc


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """
    Compute cosine similarity between two vectors using NumPy.
    Returns 0.0 if either vector has zero norm or mismatched dimensions.
    """
    if len(v1) != len(v2):
        return 0.0
    a = np.asarray(v1, dtype=np.float32)
    b = np.asarray(v2, dtype=np.float32)
    norm_a = float(np.linalg.norm(a))
    norm_b = float(np.linalg.norm(b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


from langchain_core.embeddings import Embeddings

class NVIDIAEmbeddings(Embeddings):
    """LangChain Embeddings wrapper using our existing get_embedding function."""

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [get_embedding(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return get_embedding(text)


async def _atlas_vector_search(
    db_mongo: Any,
    query_text: str,
    subject_id: int,
    top_k: int,
    min_score: float,
) -> Optional[List[Dict[str, Any]]]:
    """
    Attempt MongoDB Atlas Vector Search using LangChain MongoDBAtlasVectorSearch.
    """
    try:
        from langchain_mongodb import MongoDBAtlasVectorSearch

        # Get synchronous collection from Motor's delegate
        sync_collection = db_mongo.study_material_embeddings.delegate

        # Initialize vector store
        vector_store = MongoDBAtlasVectorSearch(
            collection=sync_collection,
            embedding=NVIDIAEmbeddings(),
            index_name=_ATLAS_INDEX_NAME,
            text_key="content",
            embedding_key="embedding",
        )

        # Define search options (filter by subject_id)
        pre_filter = {"subject_id": {"$eq": subject_id}}

        def _run_search():
            return vector_store.similarity_search_with_score(
                query=query_text,
                k=top_k,
                pre_filter=pre_filter
            )

        docs_with_scores = await asyncio.to_thread(_run_search)

        results = []
        for doc, score in docs_with_scores:
            if score >= min_score:
                results.append({
                    "id": str(doc.metadata.get("_id", "")),
                    "subject_id": doc.metadata.get("subject_id", subject_id),
                    "topic": doc.metadata.get("topic", ""),
                    "content": doc.page_content,
                    "score": float(score),
                    "metadata": doc.metadata.get("metadata", {}),
                })
        return results
    except Exception as exc:
        logger.warning("Atlas Vector Search via LangChain failed, falling back: %s", exc)
        return None



# ── NumPy-accelerated cosine fallback ─────────────────────────────────────────

async def _python_cosine_search(
    db_mongo: Any,
    query_vector: List[float],
    subject_id: int,
    top_k: int,
    min_score: float,
) -> List[Dict[str, Any]]:
    """
    Fallback: fetch all documents for the subject and rank by cosine similarity.

    Uses a single NumPy matrix multiply to score all documents in one pass
    instead of looping and calling cosine_similarity() per document.
    For 5 000 documents at 4 096 dimensions this is ~50-100x faster than
    the pure-Python per-document loop.
    """
    cursor = db_mongo.study_material_embeddings.find(
        {"subject_id": subject_id},
        {"_id": 1, "subject_id": 1, "topic": 1, "content": 1, "embedding": 1, "metadata": 1},
    )
    materials = await cursor.to_list(length=5000)

    if not materials:
        return []

    # Keep only documents that have a valid embedding vector
    valid_docs = [doc for doc in materials if doc.get("embedding")]
    if not valid_docs:
        return []

    query_np = np.asarray(query_vector, dtype=np.float32)
    query_norm = float(np.linalg.norm(query_np))
    if query_norm == 0.0:
        return []

    # Stack all document vectors into a single (N, D) matrix
    doc_matrix = np.asarray([doc["embedding"] for doc in valid_docs], dtype=np.float32)

    # Compute all dot products in one BLAS call: (N, D) @ (D,) → (N,)
    dots = doc_matrix @ query_np

    # Per-document norms: (N,)
    doc_norms = np.linalg.norm(doc_matrix, axis=1)

    # Cosine similarities — guard against zero-norm document vectors
    with np.errstate(invalid="ignore"):
        similarities = np.where(doc_norms > 0.0, dots / (doc_norms * query_norm), 0.0)

    # Filter, build result dicts, sort descending by score
    scored = [
        {
            "id": str(doc["_id"]),
            "subject_id": doc["subject_id"],
            "topic": doc["topic"],
            "content": doc["content"],
            "score": float(sim),
            "metadata": doc.get("metadata", {}),
        }
        for doc, sim in zip(valid_docs, similarities)
        if sim >= min_score
    ]

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


# ── Public API ─────────────────────────────────────────────────────────────────

async def save_study_material(
    db_mongo: Any,
    subject_id: int,
    topic: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """Embed and persist study material chunk(s); invalidates the RAG cache for the subject."""
    chunks = _chunk_text_for_embedding(content)
    if not chunks:
        raise ValueError("Nội dung tài liệu trống, không thể tạo embedding.")

    last_id = ""
    base_meta = metadata or {}
    for i, chunk in enumerate(chunks):
        embedding_vector = await asyncio.to_thread(get_embedding, chunk)
        chunk_meta = {
            **base_meta,
            "chunk_index": i,
            "chunk_total": len(chunks),
        }
        document = {
            "subject_id": subject_id,
            "topic": topic if len(chunks) == 1 else f"{topic} (phần {i + 1}/{len(chunks)})",
            "content": chunk,
            "embedding": embedding_vector,
            "metadata": chunk_meta,
            "created_at": datetime.now(timezone.utc),
        }
        result = await db_mongo.study_material_embeddings.insert_one(document)
        last_id = str(result.inserted_id)

    await invalidate_rag_cache(subject_id)
    logger.info(
        "Indexed %d chunk(s) for subject=%d topic='%s'",
        len(chunks),
        subject_id,
        topic,
    )
    return last_id


async def vector_search_materials(
    db_mongo: Any,
    query_text: str,
    subject_id: int,
    top_k: int = 3,
    min_score: float = 0.55,
) -> List[Dict[str, Any]]:
    """
    Find the most relevant study materials for *query_text* within *subject_id*.

    Flow:
      1. Check Redis cache → return immediately on hit.
      2. Generate query embedding (async, offloaded to thread pool).
      3. Try Atlas $vectorSearch (O(log n)).
      4. If Atlas unavailable → NumPy cosine fallback.
      5. Store result in Redis (TTL 1 h).
    """
    cache_key = rag_search_key(subject_id, query_text)
    cached = await get_cached(cache_key)
    if cached is not None:
        logger.debug("RAG cache hit: subject=%d query_hash=%s", subject_id, cache_key)
        return cached

    # Generate query embedding in thread pool (blocking I/O)
    query_vector = await asyncio.to_thread(get_embedding, query_text)

    # Try Atlas first, fall back to NumPy cosine
    results = await _atlas_vector_search(db_mongo, query_text, subject_id, top_k, min_score)
    if results is None:
        results = await _python_cosine_search(db_mongo, query_vector, subject_id, top_k, min_score)

    await set_cached(cache_key, results, ttl_seconds=3600)
    return results


async def invalidate_rag_cache(subject_id: int) -> None:
    """Remove all cached RAG search results for *subject_id*."""
    await invalidate_pattern(f"rag:{subject_id}:*")
