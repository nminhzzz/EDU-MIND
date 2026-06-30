# Sơ đồ Quan hệ Thực thể (ER Diagram) — AI Learning Assistant Platform

Tài liệu này mô tả toàn bộ thiết kế cơ sở dữ liệu của hệ thống, bao gồm:
- **MySQL** (SQLAlchemy ORM): 16 bảng quan hệ — lưu trữ dữ liệu có cấu trúc, ràng buộc ACID.
- **MongoDB** (Motor Async): 8 collections — lưu trữ dữ liệu phi cấu trúc, linh hoạt cho AI.

---

## 🗄️ MySQL — ER Diagram

```mermaid
erDiagram
    USERS {
        BIGINT id PK
        VARCHAR email UK
        VARCHAR password_hash
        VARCHAR full_name
        VARCHAR avatar_url
        ENUM role
        VARCHAR grade
        ENUM learning_level
        BOOLEAN is_active
        DATETIME created_at
        DATETIME updated_at
    }

    STUDENT_PREFERENCES {
        BIGINT id PK
        BIGINT student_id FK
        INT study_hours_per_day
        VARCHAR preferred_study_time
        JSON available_schedule
        DATETIME created_at
    }

    CLASSROOMS {
        BIGINT id PK
        BIGINT teacher_id FK
        BIGINT subject_id FK
        VARCHAR class_name
        VARCHAR class_code UK
        TEXT description
        DATETIME created_at
    }

    CLASSROOM_STUDENTS {
        BIGINT id PK
        BIGINT classroom_id FK
        BIGINT student_id FK
        DATETIME joined_at
    }

    SUBJECTS {
        BIGINT id PK
        VARCHAR name
        VARCHAR code UK
        TEXT description
        DATETIME created_at
    }


    STUDY_GOALS {
        BIGINT id PK
        BIGINT student_id FK
        BIGINT subject_id FK
        VARCHAR title
        DECIMAL target_score
        DATE deadline
        ENUM status
        DATETIME created_at
    }

    STUDY_PLANS {
        BIGINT id PK
        BIGINT student_id FK
        BIGINT goal_id FK
        VARCHAR title
        TEXT task_description
        DATE study_date
        TIME start_time
        TIME end_time
        BOOLEAN ai_generated
        ENUM status
        DATETIME created_at
    }

    STUDY_PLAN_PROGRESS {
        BIGINT id PK
        BIGINT study_plan_id FK
        BIGINT student_id FK
        DECIMAL completion_percent
        DATETIME completed_at
    }

    QUESTION_BANK {
        BIGINT id PK
        BIGINT subject_id FK
        VARCHAR topic
        ENUM difficulty
        TEXT question_text
        JSON options
        VARCHAR correct_answer
        TEXT explanation
        BIGINT created_by FK
        VARCHAR embedding_id
        DATETIME created_at
    }

    QUIZZES {
        BIGINT id PK
        BIGINT classroom_id FK
        BIGINT subject_id FK
        BIGINT teacher_id FK
        VARCHAR title
        ENUM difficulty
        INT total_questions
        BOOLEAN generated_by_ai
        DATETIME created_at
    }

    QUESTIONS {
        BIGINT id PK
        BIGINT quiz_id FK
        BIGINT question_bank_id FK
        DATETIME created_at
    }

    QUIZ_ATTEMPTS {
        BIGINT id PK
        BIGINT quiz_id FK
        BIGINT student_id FK
        JSON answers
        DECIMAL score
        INT correct_count
        INT wrong_count
        INT duration_seconds
        DATETIME submitted_at
    }

    LEARNING_ANALYTICS {
        BIGINT id PK
        BIGINT student_id FK
        BIGINT subject_id FK
        DECIMAL average_score
        INT quizzes_completed
        JSON weak_topics
        JSON strong_topics
        TEXT ai_feedback
        DATETIME updated_at
    }

    AI_RECOMMENDATION_REVIEWS {
        BIGINT id PK
        BIGINT student_id FK
        BIGINT teacher_id FK
        TEXT recommendation
        TEXT teacher_feedback
        ENUM status
        DATETIME created_at
    }

    NOTIFICATIONS {
        BIGINT id PK
        BIGINT user_id FK
        VARCHAR title
        TEXT content
        ENUM type
        BOOLEAN is_read
        DATETIME created_at
    }

    %% ── Relationships ──────────────────────────────────────
    USERS ||--|| STUDENT_PREFERENCES : "has"
    USERS ||--o{ CLASSROOMS : "teaches"
    USERS ||--o{ CLASSROOM_STUDENTS : "joins"
    CLASSROOMS ||--o{ CLASSROOM_STUDENTS : "contains"
    SUBJECTS ||--o{ CLASSROOMS : "contains"
    USERS ||--o{ STUDY_GOALS : "sets"
    SUBJECTS ||--o{ STUDY_GOALS : "targets"
    STUDY_GOALS ||--o{ STUDY_PLANS : "generates"
    STUDY_PLANS ||--o{ STUDY_PLAN_PROGRESS : "tracks"
    SUBJECTS ||--o{ QUESTION_BANK : "contains"
    USERS ||--o{ QUESTION_BANK : "creates"
    CLASSROOMS ||--o{ QUIZZES : "contains"
    SUBJECTS ||--o{ QUIZZES : "belongs to"
    USERS ||--o{ QUIZZES : "creates"
    QUIZZES ||--o{ QUESTIONS : "contains"
    QUESTION_BANK ||--o{ QUESTIONS : "references"
    USERS ||--o{ QUIZ_ATTEMPTS : "submits"
    QUIZZES ||--o{ QUIZ_ATTEMPTS : "receives"
    USERS ||--o{ LEARNING_ANALYTICS : "owns"
    SUBJECTS ||--o{ LEARNING_ANALYTICS : "analyzes"
    USERS ||--o{ AI_RECOMMENDATION_REVIEWS : "receives"
    USERS ||--o{ AI_RECOMMENDATION_REVIEWS : "reviews"
    USERS ||--o{ NOTIFICATIONS : "receives"
```

---

## 🍃 MongoDB — Collection Schemas

```mermaid
erDiagram
    CHAT_SESSIONS {
        ObjectId _id PK
        Long student_id
        Long classroom_id
        String title
        Date created_at
        Date updated_at
    }

    CHAT_MESSAGES {
        ObjectId _id PK
        ObjectId session_id FK
        String role
        String content
        Date created_at
    }

    AI_LOGS {
        ObjectId _id PK
        String agent_name
        Long student_id
        Object input
        Object output
        Double execution_time
        Date created_at
    }

    AI_RECOMMENDATIONS {
        ObjectId _id PK
        Long student_id
        String source_agent
        Array recommendations
        Date created_at
    }

    STUDY_MATERIAL_EMBEDDINGS {
        ObjectId _id PK
        Long subject_id
        String topic
        String content
        Array embedding
        Object metadata
        Date created_at
    }

    LEARNING_EVENTS {
        ObjectId _id PK
        Long student_id
        String event_type
        Object metadata
        Date created_at
    }

    GENERATED_QUIZZES {
        ObjectId _id PK
        Long student_id
        Long subject_id
        Array questions
        Date created_at
    }

    AGENT_MEMORY {
        ObjectId _id PK
        Long student_id
        String goal
        String progress
        Object context
        Date updated_at
    }

    %% ── Relationships ──────────────────────────────────────
    CHAT_SESSIONS ||--o{ CHAT_MESSAGES : "contains"
    AI_RECOMMENDATIONS }o--|| AGENT_MEMORY : "updates"
    LEARNING_EVENTS }o--|| AI_RECOMMENDATIONS : "triggers"
    STUDY_MATERIAL_EMBEDDINGS }o--|| GENERATED_QUIZZES : "generates"
    CHAT_SESSIONS }o--|| AI_LOGS : "logs"
    GENERATED_QUIZZES }o--|| AI_LOGS : "created_by"
    AGENT_MEMORY }o--|| AI_LOGS : "used_by"
```

---

## 🔍 Chú thích Thiết kế Quan trọng

### MySQL

| # | Quan hệ | Giải thích |
|---|---------|-----------|
| 1 | `USERS` → `STUDENT_PREFERENCES` | **1-1**: Mỗi học sinh có đúng 1 bộ cài đặt học tập. |
| 2 | `USERS` → `CLASSROOMS` | Một giáo viên quản lý nhiều lớp. |
| 3 | `CLASSROOMS` ↔ `USERS` | **N-N** qua `CLASSROOM_STUDENTS`: Học sinh tham gia nhiều lớp. |
| 4 | `SUBJECTS` → `CLASSROOMS` | **1-N**: Một môn học có nhiều lớp học giảng dạy, mỗi lớp chỉ thuộc về 1 môn. |
| 5 | `STUDY_GOALS` → `STUDY_PLANS` | Mỗi mục tiêu sinh ra nhiều task học tập theo ngày. |
| 6 | `STUDY_PLANS` → `STUDY_PLAN_PROGRESS` | Theo dõi % hoàn thành từng task (cập nhật nhiều lần). |
| 7 | `QUESTION_BANK` ↔ `QUIZZES` | **N-N** qua `QUESTIONS`: Câu hỏi từ kho được tái sử dụng trên nhiều đề. |
| 8 | `LEARNING_ANALYTICS` | Tổng hợp điểm và điểm yếu/mạnh theo từng môn — đầu vào cho Recommendation Agent. |
| 9 | `AI_RECOMMENDATION_REVIEWS` | HITL: Giáo viên xem xét và phê duyệt đề xuất AI trước khi gửi học sinh. |

### MongoDB

| Collection | Mục đích |
|-----------|---------|
| `chat_sessions` | Phiên hội thoại Chat Tutor (1 học sinh, nhiều phiên). |
| `chat_messages` | Lịch sử tin nhắn theo phiên — Conversation Memory cho AI. |
| `ai_logs` | Giám sát Input/Output mỗi lần gọi Agent — phục vụ debug & fine-tuning. |
| `ai_recommendations` | Đề xuất ôn tập của AI, chờ sync sang MySQL sau khi giáo viên duyệt. |
| `study_material_embeddings` | Vector store cho RAG — tài liệu học được chunk & encode. |
| `learning_events` | Stream sự kiện học tập real-time → kích hoạt Recommendation Agent. |
| `generated_quizzes` | Đề thi nháp do AI sinh — lưu tạm trước khi giáo viên xác nhận vào MySQL. |
| `agent_memory` | LangGraph persistent state — Agent nhớ tiến trình qua nhiều phiên. |

---

## ⚡ Luồng Dữ liệu Hybrid Database

```
Học sinh làm bài quiz
        │
        ▼
MySQL: quiz_attempts ──► Celery Task ──► LearningAnalyticsAgent
                                                │
                              ┌─────────────────┼─────────────────┐
                              ▼                 ▼                 ▼
                    MySQL: learning_analytics   MongoDB: ai_logs  MongoDB: learning_events
                              │
                              ▼
                    RecommendationAgent ──► MongoDB: ai_recommendations
                              │
                              ▼
                    MySQL: ai_recommendation_reviews (status=pending)
                              │
                    Giáo viên phê duyệt (HITL)
                              │
                              ▼ (status=approved)
                    MySQL: study_plans (task ôn tập mới)
                              │
                              ▼
                    MySQL: notifications (thông báo học sinh)
```
