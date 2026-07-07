import requests
import time
from app.database.mysql import SessionLocal
from app.models.study_plan import StudyPlan
from app.models.quiz import Quiz
from app.models.user import User

BASE_URL = "http://127.0.0.1:8000"


def test_confirm():
    print("--- 1. LOGGING IN AS STUDENT ---")
    login_res = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": "student@test.com", "password": "password123"},
    )
    if login_res.status_code != 200:
        print("Login failed!")
        print(login_res.text)
        return

    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    db = SessionLocal()
    student = db.query(User).filter(User.email == "student@test.com").first()
    student_id = student.id
    print(f"Logged in student email: {student.email}, ID: {student_id}")

    print("\n--- 2. CREATING UNIFIED DRAFT ---")
    draft_res = requests.post(
        f"{BASE_URL}/api/v1/goals/unified/draft",
        json={
            "subject_id": 1,
            "target_score": 9,
            "deadline": "2026-08-18",
            "user_message": "Hãy lập lộ trình cho tôi",
        },
        headers=headers,
    )
    if draft_res.status_code != 200:
        print("Draft failed!")
        print(draft_res.text)
        return

    draft_data = draft_res.json()
    session_id = draft_data["session_id"]
    print(f"Draft generated successfully! Session ID: {session_id}")

    print("\n--- 3. CONFIRMING ROADMAP ---")
    confirm_res = requests.post(
        f"{BASE_URL}/api/v1/goals/unified/confirm",
        json={
            "subject_id": 1,
            "target_score": 9,
            "deadline": "2026-08-18",
            "session_id": session_id,
        },
        headers=headers,
    )
    print(f"Confirm response status: {confirm_res.status_code}")
    print(confirm_res.json())

    print("Waiting 20 seconds for background RAG/Quiz generation to process...")
    time.sleep(20)

    print("\n--- 4. VERIFYING DATABASE RELATIONSHIPS ---")
    db.close()
    db = SessionLocal()
    try:
        # Check plans with RAG curriculum attached
        plans = (
            db.query(StudyPlan)
            .filter(StudyPlan.student_id == student_id, StudyPlan.rag_content != None)
            .all()
        )
        print(
            f"Found {len(plans)} study plan tasks with attached RAG curriculum materials!"
        )
        for p in plans[:2]:
            print(f"  Plan: {p.title}")
            print(f"  RAG content snippet: {p.rag_content[:120]}...")

        # Check quizzes with linked study_plan_id
        quizzes = (
            db.query(Quiz)
            .filter(Quiz.student_id == student_id, Quiz.study_plan_id != None)
            .all()
        )
        print(
            f"Found {len(quizzes)} quizzes successfully linked to daily study plan tasks!"
        )
        for q in quizzes[:2]:
            print(f"  Quiz title: {q.title}")
            print(f"  Linked to study_plan_id: {q.study_plan_id}")

    finally:
        db.close()


if __name__ == "__main__":
    test_confirm()
