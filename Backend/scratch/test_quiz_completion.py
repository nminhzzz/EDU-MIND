import requests
from app.database.mysql import SessionLocal
from app.models.study_plan import StudyPlan
from app.models.study_plan_progress import StudyPlanProgress
from app.models.quiz import Quiz
from app.models.user import User

BASE_URL = "http://127.0.0.1:8000"

def test_quiz_completion_logic():
    print("--- 1. LOGGING IN AS STUDENT ---")
    login_res = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
        "email": "student_test@edumind.com",
        "password": "studentpassword"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    db = SessionLocal()
    student = db.query(User).filter(User.email == "student_test@edumind.com").first()
    student_id = student.id
    
    # 1. Tìm hoặc tạo 1 study plan để test
    plan = db.query(StudyPlan).filter(StudyPlan.student_id == student_id).first()
    if not plan:
        print("No study plan found, please run test_confirm_api.py first to create a roadmap.")
        return
        
    plan_id = plan.id
    print(f"\nUsing StudyPlan ID: {plan_id}, Title: {plan.title}, Current Status: {plan.status}")
    
    # Reset status về todo trước khi kiểm thử
    plan.status = "todo"
    db.commit()
    
    # 2. Thử tự tích "done" thủ công qua PATCH API -> Kỳ vọng lỗi 400
    print("\n--- 2. TRYING TO MANUALLY MARK AS DONE VIA PATCH API ---")
    patch_res = requests.patch(
        f"{BASE_URL}/api/v1/plans/{plan_id}",
        json={"status": "done"},
        headers=headers
    )
    print(f"PATCH /plans/{plan_id} status code: {patch_res.status_code}")
    print(f"Response: {patch_res.json()}")
    assert patch_res.status_code == 400, "Should block manual DONE status!"
    print("✅ SUCCESS: API blocked student from manually marking task as done!")
    
    # 3. Thử cập nhật "doing" thủ công qua PATCH API -> Kỳ vọng thành công 200
    print("\n--- 3. TRYING TO MANUALLY MARK AS DOING VIA PATCH API ---")
    patch_doing_res = requests.patch(
        f"{BASE_URL}/api/v1/plans/{plan_id}",
        json={"status": "doing"},
        headers=headers
    )
    print(f"PATCH /plans/{plan_id} status code: {patch_doing_res.status_code}")
    assert patch_doing_res.status_code == 200, "Should allow marking as doing!"
    print("✅ SUCCESS: Student successfully set task to 'doing'!")
    
    # 4. Luôn dọn dẹp và tạo mới một đề thi 10 câu để test chính xác thang điểm
    from app.models.quiz_attempt import QuizAttempt
    quizzes = db.query(Quiz).filter(Quiz.study_plan_id == plan_id).all()
    quiz_ids = [q.id for q in quizzes]
    if quiz_ids:
        db.query(QuizAttempt).filter(QuizAttempt.quiz_id.in_(quiz_ids)).delete(synchronize_session=False)
        db.query(Quiz).filter(Quiz.id.in_(quiz_ids)).delete(synchronize_session=False)
        db.commit()

    print(f"Creating a fresh 10-question test quiz for study plan {plan_id}...")
    quiz = Quiz(
        student_id=student_id,
        subject_id=plan.subject_id,
        study_plan_id=plan_id,
        title=f"Test Quiz for Plan {plan_id}",
        difficulty="medium",
        total_questions=10,
        questions=[{
            "question_text": f"Question {i}",
            "correct_answer": "A",
            "options": [{"key": "A", "value": "Option A"}, {"key": "B", "value": "Option B"}],
            "explanation": "Explanation"
        } for i in range(10)],
        generated_by_ai=True
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    
    quiz_id = quiz.id
    print(f"\nUsing Quiz ID: {quiz_id}, Title: {quiz.title}")
    
    # 5. Đọc các đáp án đúng thực tế từ DB để sinh câu trả lời chính xác
    questions = quiz.questions or []
    correct_answers = [q.get("correct_answer", "A") for q in questions]
    
    # Hàm sinh câu trả lời sai: Nếu đúng là A thì chọn B, ngược lại chọn A
    def get_wrong_answer(correct):
        return "B" if str(correct).strip().upper() == "A" else "A"

    # Nộp bài đạt 5/10 điểm (ngưỡng đỗ cũ nhưng trượt ngưỡng mới) -> Kế hoạch học vẫn là 'doing'
    print("\n--- 4. SUBMITTING QUIZ ATTEMPT WITH 5/10 SCORE (5 correct answers) ---")
    answers_low = []
    for i, correct in enumerate(correct_answers):
        ans_val = correct if i < 5 else get_wrong_answer(correct)
        answers_low.append({"question_index": i, "answer": ans_val})
        
    submit_low_res = requests.post(
        f"{BASE_URL}/api/v1/quizzes/{quiz_id}/submit",
        json={
            "answers": answers_low,
            "duration_seconds": 120
        },
        headers=headers
    )
    print(f"Submit low score status code: {submit_low_res.status_code}")
    print(f"Attempt result: Score {submit_low_res.json()['score']}/10.0, Correct: {submit_low_res.json()['correct_count']}")
    
    db.close()
    db = SessionLocal()
    plan_after_low = db.query(StudyPlan).filter(StudyPlan.id == plan_id).first()
    progress_low = db.query(StudyPlanProgress).filter(StudyPlanProgress.study_plan_id == plan_id).first()
    print(f"StudyPlan Status after low score: '{plan_after_low.status}' (Expected: 'doing')")
    print(f"Completion Percent after low score: {float(progress_low.completion_percent) if progress_low else 0.0}% (Expected: 50.0%)")
    assert plan_after_low.status == "doing", "Task should remain 'doing'!"
    print("✅ SUCCESS: Score 5/10 did not trigger auto-completion!")
    
    # 6. Nộp bài đạt 9/10 điểm (đạt ngưỡng mới >= 8.0) -> Kế hoạch học tự động chuyển thành 'done', progress 100%
    print("\n--- 5. SUBMITTING QUIZ ATTEMPT WITH 9/10 SCORE (9 correct answers) ---")
    answers_high = []
    for i, correct in enumerate(correct_answers):
        ans_val = correct if i < 9 else get_wrong_answer(correct)
        answers_high.append({"question_index": i, "answer": ans_val})
        
    submit_high_res = requests.post(
        f"{BASE_URL}/api/v1/quizzes/{quiz_id}/submit",
        json={
            "answers": answers_high,
            "duration_seconds": 150
        },
        headers=headers
    )
    print(f"Submit high score status code: {submit_high_res.status_code}")
    print(f"Attempt result: Score {submit_high_res.json()['score']}/10.0, Correct: {submit_high_res.json()['correct_count']}")
    
    db.close()
    db = SessionLocal()
    plan_after_high = db.query(StudyPlan).filter(StudyPlan.id == plan_id).first()
    progress_high = db.query(StudyPlanProgress).filter(StudyPlanProgress.study_plan_id == plan_id).first()
    print(f"StudyPlan Status after high score: '{plan_after_high.status}' (Expected: 'done')")
    print(f"Completion Percent after high score: {float(progress_high.completion_percent) if progress_high else 0.0}% (Expected: 100.0%)")
    
    assert plan_after_high.status == "done", "Task should automatically become 'done'!"
    assert float(progress_high.completion_percent) == 100.0, "Progress should be 100.0%!"
    print("✅ SUCCESS: Score 9/10 triggered auto-completion and 100.0% progress sync!")
    
    print("\n🎉 ALL TESTS PASSED: AUTO-COMPLETION RULES WORK FLAWLESSLY!")
    db.close()

if __name__ == "__main__":
    test_quiz_completion_logic()
