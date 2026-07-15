"""
Background generation of RAG lecture content and quizzes for unified goals.
"""

import asyncio

from app.infrastructure.ai import generate_content_nvidia
from app.core.logging import get_logger
from app.database.mongodb import get_mongodb_db
from app.database.mysql import SessionLocal
from app.repositories.plan_repository import plan_repository
from app.repositories.quiz_repository import quiz_repository
from app.repositories.subject_repository import subject_repository
from app.services.embedding_service import vector_search_materials

logger = get_logger(__name__)

_THEORY_SUBJECT_KEYWORDS = (
    "triết học",
    "pháp luật",
    "lý luận",
    "chính trị",
    "lịch sử",
    "mác",
)


def _is_theory_subject(subject_name: str) -> bool:
    name = subject_name.lower()
    return any(keyword in name for keyword in _THEORY_SUBJECT_KEYWORDS)


def _lecture_system_instruction(is_theory_subject: bool) -> str:
    if is_theory_subject:
        return (
            "Bạn là một giáo sư đại học có thâm niên giảng dạy. Hãy viết tài liệu bài học bằng tiếng Việt cực kỳ chi tiết, khoa học, phân tích cặn kẽ bản chất và đưa ra các liên hệ thực tiễn sinh động.\n"
            "CẤU TRÚC TÀI LIỆU (BẮT BUỘC):\n"
            "I. KHÁI NIỆM CỐT LÕI & CƠ SỞ LÝ LUẬN\n"
            "II. PHÂN TÍCH CHI TIẾT & BẢN CHẤT LÝ LUẬN (Phân tích sâu sắc, đa chiều)\n"
            "III. VÍ DỤ THỰC TIỄN & MINH HỌA SINH ĐỘNG (Liên hệ ví dụ cụ thể đời sống)\n"
            "IV. KẾT LUẬN & BÀI HỌC RÚT RA\n"
            "Hãy đi trực tiếp vào nội dung tài liệu, không viết lời dẫn mở đầu hay lời chào của AI."
        )

    return (
        "Bạn là một chuyên gia và giảng viên giàu kinh nghiệm thực tiễn. Hãy viết tài liệu bài học bằng tiếng Việt cực kỳ chi tiết, rõ ràng, dễ hiểu và giàu tính ứng dụng.\n"
        "CẤU TRÚC TÀI LIỆU (BẮT BUỘC):\n"
        "I. TỔNG QUAN & KIẾN THỨC NỀN TẢNG (Khái niệm cơ bản, định nghĩa hoặc quy tắc cốt lõi)\n"
        "II. PHÂN TÍCH CHI TIẾT & HƯỚNG DẪN KỸ THUẬT (Quy tắc phát âm, giải thuật hoặc cách vận dụng cụ thể)\n"
        "III. VÍ DỤ THỰC HÀNH & KỊCH BẢN THỰC TẾ (Đoạn code mẫu, câu giao tiếp thực tiễn hoặc bài toán minh họa kèm lời giải)\n"
        "IV. TỔNG KẾT & CÁC LƯU Ý QUAN TRỌNG\n"
        "Hãy đi trực tiếp vào nội dung tài liệu, không viết lời dẫn mở đầu hay lời chào của AI."
    )


async def generate_materials_and_quizzes_for_plans_bg(
    goal_id: int, student_id: int, subject_id: int
) -> None:
    from app.services.quiz_service import generate_and_save_quiz  # noqa: PLC0415

    db = SessionLocal()
    db_mongo = get_mongodb_db()
    try:
        plans = plan_repository.get_by_goal_and_student(db, goal_id, student_id)

        subject_obj = subject_repository.get(db, subject_id)
        subject_name = subject_obj.name if subject_obj else ""
        is_theory_subject = _is_theory_subject(subject_name)

        plans = sorted(plans, key=lambda x: x.study_date)
        plans_to_generate = plans[:5]

        logger.info(
            "[BG] Generating materials for goal %d — first 5 of %d plans",
            goal_id,
            len(plans),
        )

        sys_instruction = _lecture_system_instruction(is_theory_subject)

        # 1. Sinh tài liệu lý thuyết (rag_content) cho tất cả các kế hoạch trước
        for plan in plans_to_generate:
            try:
                materials = await vector_search_materials(
                    db_mongo=db_mongo,
                    query_text=plan.title,
                    subject_id=subject_id,
                    top_k=5,
                )
            except Exception as exc:
                logger.error("[BG] RAG search failed for plan %d: %s", plan.id, exc)
                materials = []

            if materials:
                context_str = "\n\n".join(
                    [m["content"] for m in materials if "content" in m]
                )

                messages = [
                    {
                        "role": "user",
                        "content": (
                            f"Dựa trên tài liệu tham khảo giáo trình sau, hãy biên soạn một tài liệu bài giảng lý thuyết cực kỳ chi tiết, chuyên sâu và đầy đủ (độ dài tối thiểu 1500 từ) về chủ đề '{plan.title}'.\n\nTài liệu tham khảo:\n{context_str}"
                        ),
                    }
                ]

                try:
                    rag_content = await asyncio.to_thread(
                        generate_content_nvidia,
                        messages=messages,
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
                    logger.error(
                        "[BG] RAG content generation failed for plan %d: %s",
                        plan.id,
                        exc,
                    )
            else:
                logger.warning(
                    "[BG] No RAG materials found for plan %d (subject=%d) — "
                    "upload/index tài liệu môn học trước",
                    plan.id,
                    subject_id,
                )
            await asyncio.sleep(0.05)

        # 2. Sau khi sinh xong toàn bộ tài liệu lý thuyết, mới bắt đầu sinh các đề kiểm tra tuần tự
        logger.info("[BG] All RAG materials generated. Starting quiz generation phase...")
        for plan in plans_to_generate:
            db.refresh(plan)
            if not quiz_repository.get_by_study_plan_id(db, plan.id):
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
                    logger.error(
                        "[BG] Quiz generation failed for plan %d: %s", plan.id, exc
                    )
            await asyncio.sleep(0.05)

        logger.info("[BG] Finished background generation for goal %d", goal_id)
    except Exception as exc:
        logger.exception(
            "[BG] Critical error in background task for goal %d: %s", goal_id, exc
        )
    finally:
        db.close()
