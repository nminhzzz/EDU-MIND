"""Lazy generation of lecture content and a quiz for one requested study plan."""

import asyncio
import json

from app.core.logging import get_logger
from app.database.mongodb import make_mongodb_db
from app.database.mysql import SessionLocal
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

_LECTURE_MIN_WORD_COUNT = 800
_RAG_TOP_K = 3

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
    from app.infrastructure.ai.safety import wrap_untrusted_context

    raw = "\n\n".join(m["content"] for m in materials if "content" in m)
    return wrap_untrusted_context(raw, max_chars=10_000)


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


async def _generate_and_save_rag_content(
    db, db_mongo, plan, subject_id: int, sys_instruction: str
) -> None:
    """
    Retrieve RAG materials for *plan*, generate a lecture document, and
    persist it to the database.

    When no uploaded materials are found (e.g. vector search unavailable or
    no documents indexed for this subject), the AI generates the lecture from
    its own academic knowledge so every plan always gets rag_content.
    """
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

    from app.infrastructure.ai.content import capture_ai_usage
    from app.infrastructure.ai import generate_content_deepseek
    from app.schemas.learning_bundle import LearningBundle
    from app.services.ai_usage_service import build_usage_recorder

    context_str = _build_rag_context(materials) if materials else None
    try:
        with capture_ai_usage(
            build_usage_recorder("learning_bundle", goal_id=plan.goal_id, plan_id=plan.id)
        ):
            raw_bundle = await asyncio.to_thread(
                generate_content_deepseek,
                messages=[{
                    "role": "user",
                    "content": (
                        f"Táº¡o gÃ³i há»c táº­p cho chá»§ Ä‘á»: {plan.title}. "
                        "BÃ i há»c 700-900 tá»«, tá»‘i Ä‘a 6 pháº§n Markdown. "
                        "Táº¡o Ä‘ÃšNG 10 cÃ¢u há»i: CHÃNH XÃC 7 cÃ¢u tráº¯c nghiá»‡m "
                        "4 lá»±a chá»n A-D vÃ  CHÃNH XÃC 3 cÃ¢u tá»± luáº­n. "
                        "Má»i cÃ¢u pháº£i cÃ³ Ä‘Ã¡p Ã¡n vÃ  giáº£i thÃ­ch hoáº·c hÆ°á»›ng dáº«n cháº¥m ngáº¯n."
                        + (f"\nTÃ i liá»‡u tham kháº£o:\n{context_str}" if context_str else "")
                    ),
                }],
                system_instruction=sys_instruction,
                response_schema=LearningBundle,
                temperature=0.2,
                max_tokens=4500,
                request_timeout=120,
            )
        start = raw_bundle.find("{")
        end = raw_bundle.rfind("}")
        bundle = LearningBundle.model_validate(json.loads(raw_bundle[start : end + 1]))

        # Enforce a storage/display budget even if the provider ignores max_tokens.
        lesson = bundle.lesson_markdown[:20_000]
        plan_repository.save_rag_content(db, plan, lesson)
        plan.lesson_summary = bundle.lesson_summary[:6000]
        if not quiz_repository.get_by_study_plan_id(db, plan.id):
            questions = [question.model_dump() for question in bundle.questions]
            quiz_repository.stage_ai_generated(
                db,
                student_id=plan.student_id,
                subject_id=subject_id,
                study_plan_id=plan.id,
                title=bundle.quiz_title,
                difficulty="medium",
                questions=questions,
            )
        db.commit()
        db.refresh(plan)
        logger.info(
            "[BG] Learning bundle with 10 quiz questions committed for plan %d: %s",
            plan.id,
            plan.title,
        )
    except Exception as exc:
        plan_id = plan.id
        db.rollback()
        logger.error("[BG] RAG content generation failed for plan %d: %s", plan_id, exc)
        raise


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def generate_single_plan_material_bg(plan_id: int) -> None:
    """
    Background task: generate lecture content (rag_content) and quiz for a SINGLE plan on-demand.
    Triggered when a student clicks on a daily task whose material or quiz is not yet ready.
    """
    db = SessionLocal()
    mongo_client, db_mongo = make_mongodb_db()
    try:
        if not plan_repository.claim_generation(db, plan_id):
            db.rollback()
            return
        db.commit()

        plan = plan_repository.get(db, plan_id)
        if not plan:
            return

        subject_id = plan.subject_id
        subject_obj = subject_repository.get(db, subject_id) if subject_id else None
        subject_name = subject_obj.name if subject_obj else ""
        sys_instruction = _lecture_system_instruction(_is_theory_subject(subject_name))

        if not plan.rag_content:
            logger.info("[BG] On-demand generating material for plan %d: %s", plan.id, plan.title)
            await _generate_and_save_rag_content(
                db, db_mongo, plan, subject_id or 0, sys_instruction
            )
            db.refresh(plan)

        logger.info("[BG] Learning bundle generation completed for plan %d", plan.id)
        plan_repository.finish_generation(db, plan)
        db.commit()
    except Exception as exc:
        db.rollback()
        plan = plan_repository.get(db, plan_id)
        if plan:
            plan_repository.fail_generation(db, plan, str(exc))
            db.commit()
        logger.exception("[BG] Error in on-demand generation for plan %d: %s", plan_id, exc)
        raise
    finally:
        mongo_client.close()
        db.close()

