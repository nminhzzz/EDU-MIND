"""
Background generation of RAG lecture content and quizzes for unified goals.

Generates lecture materials (rag_content) for the first five study plans of a
learning goal, then creates one quiz per plan using the freshly generated content.
Both phases run sequentially inside a single background task to stay within LLM
rate limits and keep the database session consistent.
"""

import asyncio

from app.core.logging import get_logger
from app.database.mongodb import get_mongodb_db
from app.database.mysql import SessionLocal
from app.infrastructure.ai import generate_content_deepseek
from app.repositories.plan_repository import plan_repository
from app.repositories.quiz_repository import quiz_repository
from app.repositories.subject_repository import subject_repository
from app.services.embedding_service import vector_search_materials

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_THEORY_SUBJECT_KEYWORDS = (
    "triết học",
    "pháp luật",
    "lý luận",
    "chính trị",
    "lịch sử",
    "mác",
)

_PLANS_TO_GENERATE = 5
_LECTURE_MIN_WORD_COUNT = 1500
_BATCH_SLEEP_SECONDS = 0.05
_RAG_TOP_K = 5

_SYSTEM_INSTRUCTION_THEORY = (
    "Bạn là một giáo sư đại học có thâm niên giảng dạy. Hãy viết tài liệu bài học bằng tiếng Việt "
    "cực kỳ chi tiết, khoa học, phân tích cặn kẽ bản chất và đưa ra các liên hệ thực tiễn sinh động.\n"
    "CẤU TRÚC TÀI LIỆU (BẮT BUỘC):\n"
    "I. KHÁI NIỆM CỐT LÕI & CƠ SỞ LÝ LUẬN\n"
    "II. PHÂN TÍCH CHI TIẾT & BẢN CHẤT LÝ LUẬN (Phân tích sâu sắc, đa chiều)\n"
    "III. VÍ DỤ THỰC TIỄN & MINH HỌA SINH ĐỘNG (Liên hệ ví dụ cụ thể đời sống)\n"
    "IV. KẾT LUẬN & BÀI HỌC RÚT RA\n"
    "Hãy đi trực tiếp vào nội dung tài liệu, không viết lời dẫn mở đầu hay lời chào của AI."
)

_SYSTEM_INSTRUCTION_APPLIED = (
    "Bạn là một chuyên gia và giảng viên giàu kinh nghiệm thực tiễn. Hãy viết tài liệu bài học bằng "
    "tiếng Việt cực kỳ chi tiết, rõ ràng, dễ hiểu và giàu tính ứng dụng.\n"
    "CẤU TRÚC TÀI LIỆU (BẮT BUỘC):\n"
    "I. TỔNG QUAN & KIẾN THỨC NỀN TẢNG (Khái niệm cơ bản, định nghĩa hoặc quy tắc cốt lõi)\n"
    "II. PHÂN TÍCH CHI TIẾT & HƯỚNG DẪN KỸ THUẬT (Quy tắc phát âm, giải thuật hoặc cách vận dụng cụ thể)\n"
    "III. VÍ DỤ THỰC HÀNH & KỊCH BẢN THỰC TẾ "
    "(Đoạn code mẫu, câu giao tiếp thực tiễn hoặc bài toán minh họa kèm lời giải)\n"
    "IV. TỔNG KẾT & CÁC LƯU Ý QUAN TRỌNG\n"
    "Hãy đi trực tiếp vào nội dung tài liệu, không viết lời dẫn mở đầu hay lời chào của AI."
)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _is_theory_subject(subject_name: str) -> bool:
    """Return True when *subject_name* matches a known theory-heavy discipline."""
    name = subject_name.lower()
    return any(keyword in name for keyword in _THEORY_SUBJECT_KEYWORDS)


def _lecture_system_instruction(is_theory: bool) -> str:
    """Select the appropriate system instruction based on the subject type."""
    return _SYSTEM_INSTRUCTION_THEORY if is_theory else _SYSTEM_INSTRUCTION_APPLIED


def _build_rag_context(materials: list) -> str:
    """Join RAG material content strings into a single context block."""
    return "\n\n".join(m["content"] for m in materials if "content" in m)


def _build_lecture_user_message(plan_title: str, context_str: str) -> str:
    """Build the user-turn prompt for lecture content generation (with RAG context)."""
    return (
        f"Dựa trên tài liệu tham khảo giáo trình sau, hãy biên soạn một tài liệu bài giảng lý thuyết "
        f"cực kỳ chi tiết, chuyên sâu và đầy đủ (độ dài tối thiểu {_LECTURE_MIN_WORD_COUNT} từ) "
        f"về chủ đề '{plan_title}'.\n\nTài liệu tham khảo:\n{context_str}"
    )


def _build_lecture_user_message_no_rag(plan_title: str) -> str:
    """Build the user-turn prompt when no RAG materials are available.

    Instructs the AI to rely entirely on its own academic knowledge
    to produce a complete, high-quality lecture document.
    """
    return (
        f"Hãy biên soạn một tài liệu bài giảng lý thuyết cực kỳ chi tiết, chuyên sâu và đầy đủ "
        f"(độ dài tối thiểu {_LECTURE_MIN_WORD_COUNT} từ) về chủ đề '{plan_title}'.\n\n"
        f"Yêu cầu: Sử dụng kiến thức học thuật chuẩn, chính xác và phong phú của bạn để soạn thảo "
        f"nội dung bài giảng chất lượng cao, phù hợp với sinh viên đại học."
    )


async def _generate_and_save_rag_content(db, plan, subject_id: int, sys_instruction: str) -> None:
    """
    Retrieve RAG materials for *plan*, generate a lecture document, and
    persist it to the database.

    When no uploaded materials are found (e.g. vector search unavailable or
    no documents indexed for this subject), the AI generates the lecture from
    its own academic knowledge so every plan always gets rag_content.
    """
    db_mongo = get_mongodb_db()

    try:
        materials = await vector_search_materials(
            db_mongo=db_mongo,
            query_text=plan.title,
            subject_id=subject_id,
            top_k=_RAG_TOP_K,
        )
    except Exception as exc:
        logger.error("[BG] RAG search failed for plan %d: %s", plan.id, exc)
        materials = []

    if materials:
        context_str = _build_rag_context(materials)
        user_message = _build_lecture_user_message(plan.title, context_str)
        logger.info(
            "[BG] Generating lecture for plan %d from %d RAG chunk(s).",
            plan.id,
            len(materials),
        )
    else:
        logger.warning(
            "[BG] No RAG materials found for plan %d (subject=%d) — "
            "falling back to AI knowledge-based generation.",
            plan.id,
            subject_id,
        )
        user_message = _build_lecture_user_message_no_rag(plan.title)

    try:
        rag_content = await asyncio.to_thread(
            generate_content_deepseek,
            messages=[{"role": "user", "content": user_message}],
            system_instruction=sys_instruction,
            temperature=0.3,
        )
        plan_repository.save_rag_content(db, plan, rag_content)
        db.commit()
        db.refresh(plan)
        logger.info(
            "[BG] RAG content generated and committed for plan %d: %s",
            plan.id,
            plan.title,
        )
    except Exception as exc:
        logger.error("[BG] RAG content generation failed for plan %d: %s", plan.id, exc)


async def _generate_quiz_for_plan(db, db_mongo, plan, student_id: int, subject_id: int) -> None:
    """
    Generate and persist a quiz for *plan* if one does not already exist.

    Skips silently when a quiz is already present; logs on generation failure
    without propagating the exception so other plans are not blocked.
    """
    # Deferred to avoid a circular import between unified.materials and quiz_service.
    from app.services.quiz_service import generate_and_save_quiz  # noqa: PLC0415

    db.refresh(plan)
    if quiz_repository.get_by_study_plan_id(db, plan.id):
        return

    try:
        await generate_and_save_quiz(
            db=db,
            db_mongo=db_mongo,
            student_id=student_id,
            subject_id=subject_id,
            topic=plan.title,
            difficulty="medium",
            total_questions=5,
            study_plan_id=plan.id,
        )
        logger.info("[BG] Quiz generated for plan %d using its rag_content", plan.id)
    except Exception as exc:
        logger.error("[BG] Quiz generation failed for plan %d: %s", plan.id, exc)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def generate_materials_and_quizzes_for_plans_bg(
    goal_id: int, student_id: int, subject_id: int
) -> None:
    """
    Background task: generate lecture content and quizzes for the first
    ``_PLANS_TO_GENERATE`` study plans of a learning goal.

    Phase 1 — Lecture content: for each plan, retrieve RAG source materials,
    generate a detailed lecture document, and save it to the plan record.

    Phase 2 — Quizzes: after all lecture documents are ready, generate one
    quiz per plan using the freshly saved rag_content as context.

    A small sleep between items (``_BATCH_SLEEP_SECONDS``) prevents hitting
    rate limits when many plans are processed in rapid succession.
    """
    db = SessionLocal()
    db_mongo = get_mongodb_db()

    try:
        plans = plan_repository.get_by_goal_and_student(db, goal_id, student_id)

        subject_obj = subject_repository.get(db, subject_id)
        subject_name = subject_obj.name if subject_obj else ""
        sys_instruction = _lecture_system_instruction(_is_theory_subject(subject_name))

        plans_to_generate = sorted(plans, key=lambda p: p.study_date)[:_PLANS_TO_GENERATE]

        logger.info(
            "[BG] Generating materials for goal %d — first %d of %d plans",
            goal_id,
            len(plans_to_generate),
            len(plans),
        )

        # Phase 1: generate lecture content for all plans first.
        for plan in plans_to_generate:
            await _generate_and_save_rag_content(db, plan, subject_id, sys_instruction)
            await asyncio.sleep(_BATCH_SLEEP_SECONDS)

        # Phase 2: generate quizzes once all lecture content is ready.
        logger.info("[BG] All RAG materials generated. Starting quiz generation phase...")
        for plan in plans_to_generate:
            await _generate_quiz_for_plan(db, db_mongo, plan, student_id, subject_id)
            await asyncio.sleep(_BATCH_SLEEP_SECONDS)

        logger.info("[BG] Finished background generation for goal %d", goal_id)

    except Exception as exc:
        logger.exception(
            "[BG] Critical error in background task for goal %d: %s", goal_id, exc
        )
    finally:
        db.close()
