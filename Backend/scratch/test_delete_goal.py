import requests
from app.database.mysql import SessionLocal
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.models.quiz import Quiz
from app.models.user import User

BASE_URL = "http://127.0.0.1:8000"

def test_delete_roadmap():
    print("--- 1. LOGGING IN AS STUDENT ---")
    login_res = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
        "email": "student_test@edumind.com",
        "password": "studentpassword"
    })
    if login_res.status_code != 200:
        print("Login failed!")
        return
        
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    db = SessionLocal()
    student = db.query(User).filter(User.email == "student_test@edumind.com").first()
    student_id = student.id
    
    # Lấy danh sách goals hiện tại
    goals = db.query(StudyGoal).filter(StudyGoal.student_id == student_id).all()
    if not goals:
        print("No active goals found. Creating a temporary goal first...")
        # Tạo nhanh một goal nháp
        draft_res = requests.post(
            f"{BASE_URL}/api/v1/goals/unified/draft",
            json={"subject_id": 1, "target_score": 9.5, "deadline": "2026-08-18", "user_message": "Tạo lộ trình"},
            headers=headers
        )
        session_id = draft_res.json()["session_id"]
        # Confirm
        requests.post(
            f"{BASE_URL}/api/v1/goals/unified/confirm",
            json={"subject_id": 1, "target_score": 9.5, "deadline": "2026-08-18", "session_id": session_id},
            headers=headers
        )
        db.close()
        db = SessionLocal()
        goals = db.query(StudyGoal).filter(StudyGoal.student_id == student_id).all()

    target_goal = goals[0]
    goal_id = target_goal.id
    print(f"\n--- 2. DETECTED GOAL TO DELETE ---")
    print(f"Goal ID: {goal_id}, Title: {target_goal.title}")
    
    plan_count_before = db.query(StudyPlan).filter(StudyPlan.goal_id == goal_id).count()
    plan_ids = [p.id for p in target_goal.study_plans]
    quiz_count_before = db.query(Quiz).filter(Quiz.study_plan_id.in_(plan_ids)).count() if plan_ids else 0
    print(f"Number of linked plans before delete: {plan_count_before}")
    print(f"Number of linked quizzes before delete: {quiz_count_before}")
    
    print(f"\n--- 3. SENDING DELETE REQUEST FOR GOAL {goal_id} ---")
    delete_res = requests.delete(f"{BASE_URL}/api/v1/goals/{goal_id}", headers=headers)
    print(f"Delete response status code: {delete_res.status_code}")
    print(f"Response body: {delete_res.json()}")
    
    db.close()
    db = SessionLocal()
    
    # Kiểm tra xem Goal đã bị xóa chưa
    goal_after = db.query(StudyGoal).filter(StudyGoal.id == goal_id).first()
    plan_count_after = db.query(StudyPlan).filter(StudyPlan.goal_id == goal_id).count()
    quiz_count_after = db.query(Quiz).filter(Quiz.study_plan_id.in_(plan_ids)).count() if plan_ids else 0
    
    print(f"\n--- 4. POST-DELETE VERIFICATION ---")
    print(f"Is StudyGoal in DB? {'Yes' if goal_after else 'No (Success)'}")
    print(f"Linked plans count after: {plan_count_after} (Expected: 0)")
    print(f"Linked quizzes count after: {quiz_count_after} (Expected: 0)")
    
    if not goal_after and plan_count_after == 0 and quiz_count_after == 0:
        print("\n✅ SUCCESS: Roadmap and all cascading data successfully purged!")
    else:
        print("\n❌ FAILURE: Some data was not cleaned up correctly!")
        
    db.close()

if __name__ == "__main__":
    test_delete_roadmap()
