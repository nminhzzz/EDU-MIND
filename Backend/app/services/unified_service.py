import json
import uuid
from datetime import date, datetime
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session
from app.models.user import User
from app.models.subject import Subject
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.models.quiz import Quiz
from app.models.student_preference import StudentPreference

from app.database.mongodb import get_mongodb_db
from app.database.redis import get_redis_client
from app.repositories import chat_repository
from app.schemas.unified_goal import UnifiedGoalPlanResponse
from app.agents.unified_agent import generate_unified_plan, generate_unified_plan_stream


async def generate_unified_draft(
    student: User,
    subject_obj: Subject,
    target_score: float,
    deadline: date,
    user_message: Optional[str] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sinh/tinh chỉnh lộ trình hợp nhất và lưu vào Redis Cache.
    """
    db_mongo = get_mongodb_db()
    redis_client = get_redis_client()

    # 1. Khởi tạo hoặc lấy session_id
    if not session_id:
        session_id = await chat_repository.create_chat_session(
            student_id=student.id,
            title=f"Lập lộ trình {subject_obj.name}"
        )

    # 2. Lưu tin nhắn của học sinh vào MongoDB
    if user_message:
        await chat_repository.add_chat_message(session_id, "user", user_message)

    # 3. Lấy lịch sử chat cũ
    history_msgs = await chat_repository.get_chat_messages(session_id)

    # 4. Đọc Student Preference (MySQL)
    # Lấy preferences từ DB session
    from app.database.mysql import SessionLocal
    db_mysql = SessionLocal()
    pref = db_mysql.query(StudentPreference).filter(StudentPreference.student_id == student.id).first()
    db_mysql.close()

    study_hours_per_day = 2.0
    preferred_time = "evening"
    off_days = ["sun"]
    available_schedule = None

    if pref:
        study_hours_per_day = float(pref.study_hours_per_day) if pref.study_hours_per_day else 2.0
        preferred_time = pref.preferred_study_time or "evening"
        available_schedule = pref.available_schedule
        if available_schedule:
            off_days = []
            for k, v in available_schedule.items():
                is_available = any(v.get(slot) for slot in ["morning", "afternoon", "evening"]) if isinstance(v, dict) else bool(v)

                if not is_available:
                    off_days.append(k)

    # Khung giờ tiếng Việt tương ứng
    TIME_MAP = {"morning": "buổi sáng", "afternoon": "buổi chiều", "evening": "buổi tối"}
    preferred_time_vn = TIME_MAP.get(preferred_time, "buổi tối")

    # 5. Gọi Super Agent lập lộ trình
    current_date = date.today().strftime("%Y-%m-%d")
    plan = await generate_unified_plan(
        subject=subject_obj.name,
        target_score=target_score,
        deadline=deadline,
        student_id=student.id,
        subject_id=subject_obj.id,
        study_hours_per_day=study_hours_per_day,
        preferred_time=preferred_time_vn,
        off_days=off_days,
        current_date=current_date,
        available_schedule=available_schedule,
        history=history_msgs,
        db_mongo=db_mongo
    )

    # 6. Lưu lộ trình nháp vào Redis Cache (1800 giây = 30 phút) kèm metadata
    redis_key = f"unified_draft:{session_id}"
    cache_data = plan.model_dump()
    cache_data["_subject_id"] = subject_obj.id
    cache_data["_subject_name"] = subject_obj.name
    cache_data["_target_score"] = target_score
    cache_data["_deadline"] = deadline.isoformat()
    cache_data["_student_id"] = student.id
    redis_client.setex(redis_key, 1800, json.dumps(cache_data, ensure_ascii=False))
    print(f"-> Cached unified draft in Redis for session {session_id} (TTL: 1800s)")

    # 7. Lưu câu trả lời của AI vào MongoDB history
    await chat_repository.add_chat_message(session_id, "assistant", plan.model_dump_json())

    return {
        "session_id": session_id,
        "plan": plan
    }


async def generate_unified_draft_stream(
    student: User,
    subject_obj: Subject,
    target_score: float,
    deadline: date,
    user_message: Optional[str] = None,
    session_id: Optional[str] = None
):
    """
    Streaming version: yields (type, data) tuples.
    Types: 'progress', 'token', 'complete', 'error'
    """
    db_mongo = get_mongodb_db()
    redis_client = get_redis_client()

    if not session_id:
        session_id = await chat_repository.create_chat_session(
            student_id=student.id,
            title=f"Lập lộ trình {subject_obj.name}"
        )
        yield ("progress", f"🆔 Phiên làm việc: {session_id}")

    if user_message:
        await chat_repository.add_chat_message(session_id, "user", user_message)

    history_msgs = await chat_repository.get_chat_messages(session_id)

    from app.database.mysql import SessionLocal
    db_mysql = SessionLocal()
    pref = db_mysql.query(StudentPreference).filter(StudentPreference.student_id == student.id).first()
    db_mysql.close()

    study_hours_per_day = 2.0
    preferred_time = "evening"
    off_days = ["sun"]
    available_schedule = None
    if pref:
        study_hours_per_day = float(pref.study_hours_per_day) if pref.study_hours_per_day else 2.0
        preferred_time = pref.preferred_study_time or "evening"
        available_schedule = pref.available_schedule
        if available_schedule:
            off_days = []
            for k, v in available_schedule.items():
                is_available = any(v.values()) if isinstance(v, dict) else bool(v)
                if not is_available:
                    off_days.append(k)

    TIME_MAP = {"morning": "buổi sáng", "afternoon": "buổi chiều", "evening": "buổi tối"}
    preferred_time_vn = TIME_MAP.get(preferred_time, "buổi tối")

    current_date = date.today().strftime("%Y-%m-%d")

    plan = None
    async for msg_type, msg_data in generate_unified_plan_stream(
        subject=subject_obj.name, target_score=target_score, deadline=deadline,
        student_id=student.id, subject_id=subject_obj.id,
        study_hours_per_day=study_hours_per_day,
        preferred_time=preferred_time_vn, off_days=off_days,
        current_date=current_date, available_schedule=available_schedule,
        history=history_msgs, db_mongo=db_mongo
    ):
        if msg_type == "complete":
            plan = msg_data
        elif msg_type == "error":
            yield ("error", msg_data)
            return
        else:
            yield (msg_type, msg_data)

    if plan is None:
        yield ("error", "Không thể tạo lộ trình.")
        return

    cache_data = plan.model_dump()
    cache_data["_subject_id"] = subject_obj.id
    cache_data["_subject_name"] = subject_obj.name
    cache_data["_target_score"] = target_score
    cache_data["_deadline"] = deadline.isoformat()
    cache_data["_student_id"] = student.id
    redis_key = f"unified_draft:{session_id}"
    redis_client.setex(redis_key, 1800, json.dumps(cache_data, ensure_ascii=False))

    await chat_repository.add_chat_message(session_id, "assistant", plan.model_dump_json())

    yield ("progress", "💾 Đã lưu bản nháp. Bạn có thể nói 'lưu lại' để xác nhận.")
    yield ("complete_plan", {
        "session_id": session_id,
        "plan": plan,
        "plan_text": format_plan_as_text(plan)
    })


async def confirm_unified_draft(
    db: Session,
    student: User,
    subject_obj: Subject,
    session_id: str,
    target_score: float,
    deadline: date
) -> Dict[str, Any]:
    """
    Xác nhận lưu lộ trình nháp trọn gói từ Redis (hoặc Fallback Mongo) vào MySQL.
    """
    redis_client = get_redis_client()
    db_mongo = get_mongodb_db()

    redis_key = f"unified_draft:{session_id}"
    cached_data = redis_client.get(redis_key)

    plan = None
    if cached_data:
        print(f"-> Redis Cache HIT for key {redis_key}. Loading unified draft.")
        try:
            data = json.loads(cached_data)
            plan = UnifiedGoalPlanResponse(**data)
        except Exception as e:
            print(f"[Warning] Failed parsing Redis data: {e}")

    if not plan:
        print(f"-> Redis Cache MISS or expired for key {redis_key}. Fallback to MongoDB.")
        last_msg = await chat_repository.get_last_assistant_message(session_id)
        if not last_msg:
            raise ValueError("Không tìm thấy lộ trình nháp cũ trong cache hay MongoDB. Vui lòng tạo mới.")
        try:
            data = json.loads(last_msg)
            plan = UnifiedGoalPlanResponse(**data)
        except Exception as e:
            raise ValueError(f"Dữ liệu lộ trình nháp bị lỗi cấu trúc: {e}")

    # 1. Tạo mục tiêu học tập (StudyGoal)
    db_goal = StudyGoal(
        student_id=student.id,
        subject_id=subject_obj.id,
        title=f"Lộ trình học {subject_obj.name} - Mục tiêu {target_score}/10",
        target_score=target_score,
        deadline=deadline,
        status="active"
    )
    db.add(db_goal)
    db.flush()

    # 2. Lưu lịch học chi tiết hàng ngày (StudyPlan)
    db_plans = []
    for day_task in plan.daily_schedule:
        study_date_val = datetime.strptime(day_task.date, "%Y-%m-%d").date()
        start_time_val = datetime.strptime(day_task.start_time, "%H:%M").time()
        end_time_val = datetime.strptime(day_task.end_time, "%H:%M").time()

        db_plan = StudyPlan(
            goal_id=db_goal.id,
            student_id=student.id,
            title=day_task.task,
            task_description=day_task.description,
            rag_content=None, # Sẽ sinh hoặc truy vấn RAG on-the-fly khi bắt đầu học
            study_date=study_date_val,
            start_time=start_time_val,
            end_time=end_time_val,
            status="todo"
        )
        db.add(db_plan)
        db_plans.append(db_plan)
    db.flush()

    # 3. Lưu đề thi thử (Quiz & QuestionBank)
    total_quizzes = 0
    for quiz_item in plan.quizzes:
        questions_json = []
        for q in quiz_item.questions:
            options_data = [{"key": opt.key, "value": opt.value} for opt in q.options] if q.options else []
            questions_json.append({
                "question_text": q.question_text,
                "options": options_data,
                "correct_answer": q.correct_answer,
                "explanation": q.explanation
            })

        # Tìm study_plan_id phù hợp trong db_plans để liên kết quiz vào đúng task ngày học
        matched_plan_id = None
        for p in db_plans:
            clean_quiz_title = quiz_item.title.lower()
            for r in ["quiz", "bài kiểm tra", "tuần", "luyện tập", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ":", "-", "_"]:
                clean_quiz_title = clean_quiz_title.replace(r, "")
            clean_quiz_title = clean_quiz_title.strip()

            if len(clean_quiz_title) >= 3 and (clean_quiz_title in p.title.lower() or p.title.lower() in clean_quiz_title):
                matched_plan_id = p.id
                break

        # Nếu không khớp, lấy task cuối cùng của tuần liên quan (hoặc fallback về task gần nhất)
        if not matched_plan_id and db_plans:
            matched_plan_id = db_plans[-1].id

        db_quiz = Quiz(
            student_id=student.id,
            subject_id=subject_obj.id,
            study_plan_id=matched_plan_id,
            title=quiz_item.title,
            difficulty="medium",
            total_questions=len(questions_json),
            questions=questions_json,
            generated_by_ai=True
        )
        db.add(db_quiz)
        total_quizzes += 1

    db.commit()
    db.refresh(db_goal)

    # 4. Xóa Redis cache sau khi confirm thành công
    try:
        redis_client.delete(redis_key)
        print(f"-> Deleted cache key {redis_key} after successful confirmation.")
    except Exception as e:
        print(f"[Warning] Failed deleting cache key {redis_key}: {e}")

    return {
        "goal": db_goal,
        "total_plans": len(db_plans),
        "total_quizzes": total_quizzes
    }


def format_plan_as_text(plan) -> str:
    lines = []
    lines.append(f"📅 **Lộ trình tuần:**")
    for w in plan.weeks:
        lines.append(f"  • Tuần {w.week}: {' | '.join(w.tasks[:3])}")
        if len(w.tasks) > 3:
            lines.append(f"    ... và {len(w.tasks) - 3} nhiệm vụ khác")

    lines.append(f"\n📆 **Thời khóa biểu chi tiết ({len(plan.daily_schedule)} buổi):**")
    for day in plan.daily_schedule[:5]:
        lines.append(f"  • {day.date} ({day.start_time}-{day.end_time}): {day.task}")
    if len(plan.daily_schedule) > 5:
        lines.append(f"    ... và {len(plan.daily_schedule) - 5} buổi khác")

    lines.append(f"\n📚 **Tài liệu tham khảo ({len(plan.curriculum_materials)} tài liệu):**")
    for m in plan.curriculum_materials[:3]:
        lines.append(f"  • {m.topic}")

    lines.append(f"\n📝 **Bài kiểm tra ({len(plan.quizzes)} đề):**")
    for q in plan.quizzes:
        lines.append(f"  • {q.title} ({len(q.questions)} câu)")

    return "\n".join(lines)


def get_active_goal_for_subject(db, student_id: int, subject_id: int):
    from app.models.study_goal import StudyGoal
    return db.query(StudyGoal).filter(
        StudyGoal.student_id == student_id,
        StudyGoal.subject_id == subject_id,
        StudyGoal.status == "active"
    ).order_by(StudyGoal.created_at.desc()).first()


async def generate_materials_and_quizzes_for_plans_bg(
    goal_id: int,
    student_id: int,
    subject_id: int
):
    from app.database.mysql import SessionLocal
    from app.database.mongodb import get_mongodb_db
    from app.models.study_plan import StudyPlan
    from app.models.quiz import Quiz
    from app.services.quiz_service import generate_and_save_quiz
    from app.services.embedding_service import vector_search_materials
    from app.agents.base import generate_content_nvidia
    
    db = SessionLocal()
    db_mongo = get_mongodb_db()
    try:
        # 1. Lấy tất cả kế hoạch học tập của mục tiêu này
        plans = db.query(StudyPlan).filter(
            StudyPlan.goal_id == goal_id,
            StudyPlan.student_id == student_id
        ).all()
        
        print(f"[BG Task] Bắt đầu sinh ngầm tài liệu & quiz cho lộ trình {goal_id}. Số lượng ngày học: {len(plans)}")
        
        for p in plans:
            # 1.1 RAG: Tìm tài liệu liên quan trong MongoDB
            try:
                materials = await vector_search_materials(
                    db_mongo=db_mongo,
                    query_text=p.title,
                    subject_id=subject_id,
                    top_k=5
                )
            except Exception as e:
                print(f"[BG Task] Lỗi tìm tài liệu cho bài học {p.id}: {e}")
                materials = []
                
            if materials:
                context_str = "\n\n".join([m["content"] for m in materials if "content" in m])
                
                # 1.2 Gọi AI viết bài giảng lý thuyết chuyên sâu (tối thiểu 1500 từ)
                messages = [
                    {
                        "role": "user",
                        "content": f"Dựa trên tài liệu tham khảo giáo trình sau, hãy biên soạn một tài liệu bài giảng lý thuyết cực kỳ chi tiết, chuyên sâu và đầy đủ (độ dài tối thiểu 1500 từ) về chủ đề '{p.title}'.\n\nTài liệu tham khảo:\n{context_str}"
                    }
                ]
                try:
                    rag_content = generate_content_nvidia(
                        messages=messages,
                        system_instruction=(
                            "Bạn là một giáo sư đại học có thâm niên giảng dạy. Hãy viết tài liệu bài học bằng tiếng Việt cực kỳ chi tiết, khoa học, phân tích cặn kẽ bản chất và đưa ra các liên hệ thực tiễn sinh động.\n"
                            "CẤU TRÚC TÀI LIỆU (BẮT BUỘC):\n"
                            "I. KHÁI NIỆM CỐT LÕI & CƠ SỞ LÝ LUẬN\n"
                            "II. PHÂN TÍCH CHI TIẾT & BẢN CHẤT LÝ LUẬN (Phân tích sâu sắc, đa chiều)\n"
                            "III. VÍ DỤ THỰC TIỄN & MINH HỌA SINH ĐỘNG (Liên hệ ví dụ cụ thể đời sống)\n"
                            "IV. KẾT LUẬN & BÀI HỌC RÚT RA\n"
                            "Hãy đi trực tiếp vào nội dung tài liệu, không viết lời dẫn mở đầu hay lời chào của AI."
                        ),
                        temperature=0.3
                    )
                    # Cập nhật cột rag_content trong MySQL
                    p.rag_content = rag_content
                    db.commit()
                    print(f"[BG Task] Đã sinh tài liệu RAG chi tiết cho bài học {p.id}: {p.title}")
                except Exception as e:
                    print(f"[BG Task] Lỗi sinh nội dung RAG cho bài học {p.id}: {e}")
            
            # 1.3 Kiểm tra xem đã có đề thi liên kết chưa, nếu chưa thì tạo
            existing_quiz = db.query(Quiz).filter(Quiz.study_plan_id == p.id).first()
            if not existing_quiz:
                try:
                    await generate_and_save_quiz(
                        db=db,
                        db_mongo=db_mongo,
                        student_id=student_id,
                        subject_id=subject_id,
                        topic=p.title,
                        difficulty="medium",
                        total_questions=10,
                        study_plan_id=p.id
                    )
                    print(f"[BG Task] Đã sinh và liên kết đề thi 10 câu thành công cho bài học {p.id}")
                except Exception as e:
                    print(f"[BG Task] Lỗi sinh quiz cho bài học {p.id}: {e}")
                    
        print(f"[BG Task] Hoàn tất sinh ngầm tài liệu & quiz cho lộ trình {goal_id}!")
    except Exception as e:
        print(f"[BG Task] Lỗi nghiêm trọng trong tác vụ nền: {e}")
    finally:
        db.close()
