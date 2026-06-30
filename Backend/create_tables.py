from app.database.mysql import engine, Base
# Import all models to ensure they are registered with Base.metadata before creating tables
from app.models.user import User
from app.models.subject import Subject
from app.models.study_goal import StudyGoal
from app.models.study_plan import StudyPlan
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.learning_analytic import LearningAnalytic
from app.models.notification import Notification
from app.models.classroom import Classroom
from app.models.classroom_student import ClassroomStudent
from app.models.study_document import StudyDocument
from app.models.student_preference import StudentPreference
from app.models.study_plan_progress import StudyPlanProgress
from app.models.ai_recommendation_review import AIRecommendationReview

from sqlalchemy import text

def main():
    print("--- KHỞI TẠO CÁC BẢNG DỮ LIỆU MYSQL ---")
    try:
        print("Đang xóa các bảng cũ...")
        with engine.connect() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            Base.metadata.drop_all(bind=conn)
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            conn.commit()
            
        print("Đang tạo các bảng mới...")
        Base.metadata.create_all(bind=engine)
        print("✔ Tất cả các bảng đã được khởi tạo thành công trong MySQL!")
    except Exception as e:


        print("✘ Lỗi khi khởi tạo các bảng:")
        print(e)

if __name__ == "__main__":
    main()
