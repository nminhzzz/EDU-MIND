"""
Service xử lý Embeddings và RAG Pipeline — Giai đoạn 3.
Sử dụng model `nvidia/embeddings-nv-embed-qa-4` của NVIDIA NIM để sinh vector 4096 chiều.
Thực hiện Vector Search bằng Cosine Similarity thuần trên Python đối với MongoDB.
"""

import math
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.agents.base import get_nvidia_client

EMBEDDING_MODEL = "nvidia/nv-embed-v1"


def get_embedding(text: str) -> List[float]:
    """
    Sinh vector embedding từ API NVIDIA NIM cho đoạn văn bản đầu vào.
    """
    if not text.strip():
        return [0.0] * 4096

    client = get_nvidia_client()
    try:
        response = client.embeddings.create(input=[text], model=EMBEDDING_MODEL)
        return response.data[0].embedding
    except Exception as e:
        raise RuntimeError(f"Lỗi khi sinh vector embedding từ NVIDIA NIM: {e}")


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """
    Tính độ tương đồng Cosine giữa hai vector.
    """
    if len(v1) != len(v2):
        return 0.0

    dot_product = sum(x * y for x, y in zip(v1, v2))
    norm_v1 = math.sqrt(sum(x * x for x in v1))
    norm_v2 = math.sqrt(sum(x * x for x in v2))

    if not norm_v1 or not norm_v2:
        return 0.0

    return dot_product / (norm_v1 * norm_v2)


async def save_study_material(
    db_mongo: Any,
    subject_id: int,
    topic: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Sinh embedding và lưu tài liệu học tập vào MongoDB collection `study_material_embeddings`.
    """
    embedding_vector = await asyncio.to_thread(get_embedding, content)

    document = {
        "subject_id": subject_id,
        "topic": topic,
        "content": content,
        "embedding": embedding_vector,
        "metadata": metadata or {},
        "created_at": datetime.utcnow(),
    }

    result = await db_mongo.study_material_embeddings.insert_one(document)
    return str(result.inserted_id)


async def vector_search_materials(
    db_mongo: Any,
    query_text: str,
    subject_id: int,
    top_k: int = 3,
    min_score: float = 0.55,
) -> List[Dict[str, Any]]:
    """
    Tìm kiếm tài liệu học tập liên quan nhất bằng Vector Search kết hợp Cosine Similarity.
    """
    # 1. Sinh vector embedding cho câu hỏi truy vấn
    query_vector = await asyncio.to_thread(get_embedding, query_text)

    # 2. Truy vấn tất cả tài liệu có cùng môn học (subject_id)
    cursor = db_mongo.study_material_embeddings.find({"subject_id": subject_id})
    materials = await cursor.to_list(length=1000)

    if not materials:
        return []

    # 3. Tính tương đồng cosine giữa truy vấn và từng tài liệu
    scored_materials = []
    for doc in materials:
        doc_vector = doc.get("embedding", [])
        if not doc_vector:
            continue

        sim = cosine_similarity(query_vector, doc_vector)
        if sim >= min_score:
            scored_materials.append(
                {
                    "id": str(doc["_id"]),
                    "subject_id": doc["subject_id"],
                    "topic": doc["topic"],
                    "content": doc["content"],
                    "score": sim,
                    "metadata": doc.get("metadata", {}),
                }
            )

    # 4. Sắp xếp giảm dần theo điểm tương đồng
    scored_materials.sort(key=lambda x: x["score"], reverse=True)

    # 5. Trả về top k kết quả tốt nhất
    return scored_materials[:top_k]
