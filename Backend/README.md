# Cấu trúc thư mục Backend - AI Learning Assistant Platform

Tài liệu này mô tả cấu trúc thư mục backend được thiết kế chuẩn chỉnh cho một dự án thực tế dựa trên **FastAPI**, tích hợp **SQLAlchemy (MySQL)**, **MongoDB**, **Redis**, **Celery (Background Tasks)** và **Agentic AI Workflow (LangGraph / LangChain / Pydantic)**.

---

## 📂 Sơ đồ cấu trúc thư mục tổng quan

```text
backend/
├── alembic/                     # Quản lý cơ sở dữ liệu migration (MySQL)
│   ├── env.py
│   ├── script.py.mako
│   └── versions/                # Chứa các file migrations
│
├── app/                         # Mã nguồn chính của ứng dụng
│   ├── main.py                  # Điểm khởi chạy FastAPI (Entrypoint)
│   │
│   ├── core/                    # Cấu hình hệ thống & Tiện ích dùng chung
│   │   ├── config.py            # Đọc biến môi trường (.env) bằng Pydantic Settings
│   │   ├── security.py          # Hashing mật khẩu, tạo/verify JWT token
│   │   ├── middleware.py        # CORS, Custom Logging, Rate Limiter
│   │   └── exceptions.py        # Định nghĩa các lỗi hệ thống (Custom Exception Handler)
│   │
│   ├── database/                # Thiết lập kết nối các database
│   │   ├── mysql.py             # Khởi tạo SQLAlchemy Engine, SessionLocal
│   │   ├── mongodb.py           # Khởi tạo Motor client (Async MongoDB) cho Chat History & Logs
│   │   └── redis.py             # Khởi tạo Redis client cho Caching & Message Queue
│   │
│   ├── models/                  # Định nghĩa SQLAlchemy Models (MySQL - 9 bảng chính)
│   │   ├── base.py              # Lớp Base dùng chung (id, created_at, updated_at)
│   │   ├── user.py              # Bảng users
│   │   ├── subject.py           # Bảng subjects
│   │   ├── study_goal.py        # Bảng study_goals
│   │   ├── study_plan.py        # Bảng study_plans
│   │   ├── quiz.py              # Bảng quizzes
│   │   ├── question.py          # Bảng questions (chứa đáp án JSON)
│   │   ├── quiz_attempt.py      # Bảng quiz_attempts
│   │   ├── learning_analytic.py # Bảng learning_analytics
│   │   └── notification.py      # Bảng notifications
│   │
│   ├── schemas/                 # Pydantic Schemas (Kiểm định dữ liệu Request/Response)
│   │   ├── auth.py              # Token, Login, Register schemas
│   │   ├── user.py              # User schemas (UserRead, UserUpdate...)
│   │   ├── study_goal.py
│   │   ├── study_plan.py
│   │   ├── quiz.py
│   │   ├── quiz_attempt.py
│   │   ├── learning_analytic.py
│   │   └── notification.py
│   │
│   ├── api/                     # Quản lý các endpoints API
│   │   ├── deps.py              # Dependency Injection (get_db, get_current_user...)
│   │   └── v1/
│   │       ├── router.py        # Tổng hợp tất cả router con
│   │       ├── auth.py          # /api/v1/auth/* (Đăng ký, đăng nhập)
│   │       ├── users.py         # /api/v1/users/* (Thông tin cá nhân, cập nhật profile)
│   │       ├── study_goals.py   # /api/v1/goals/* (Quản lý mục tiêu học tập)
│   │       ├── study_plans.py   # /api/v1/plans/* (Quản lý kế hoạch học tập)
│   │       ├── quizzes.py       # /api/v1/quizzes/* (Quản lý và thực hiện làm bài quiz)
│   │       ├── analytics.py     # /api/v1/analytics/* (Thống kê và phân tích học lực)
│   │       └── chat.py          # /api/v1/chat/* (SSE Streaming / WebSocket cho Chat Tutor)
│   │
│   ├── services/                # Tầng xử lý Logic Nghiệp Vụ (Business Logic) chính
│   │   ├── user_service.py      # CRUD user, phân quyền
│   │   ├── goal_service.py      # Tạo goal, tính toán deadline
│   │   ├── plan_service.py      # Cập nhật tiến trình học tập
│   │   ├── quiz_service.py      # Lưu trữ bài làm, chấm điểm tự động
│   │   └── analytic_service.py  # Tổng hợp lịch sử làm bài để đẩy qua AI phân tích
│   │
│   ├── repositories/            # Tầng truy xuất Cơ sở dữ liệu (CRUD trực tiếp)
│   │   ├── base.py              # Base Repository chứa generic CRUD methods
│   │   ├── user_repository.py
│   │   ├── goal_repository.py
│   │   ├── plan_repository.py
│   │   ├── quiz_repository.py
│   │   └── analytic_repository.py
│   │
│   ├── agents/                  # Hệ thống AI Agents (LangGraph / LangChain / Pydantic AI)
│   │   ├── base.py              # Cấu hình chung cho LLMs (OpenAI, Gemini), base class cho Agents
│   │   ├── prompts.py           # Nơi lưu trữ tập trung các Prompt System, Prompt Template
│   │   │
│   │   ├── tools/               # Các công cụ bổ sung cho Agent gọi khi cần (Tool Calling)
│   │   │   ├── datetime_tool.py # Tool lấy thời gian thực (Giúp AI hiểu "hôm nay là ngày mấy")
│   │   │   └── db_tools.py      # Tool truy vấn dữ liệu từ MySQL/MongoDB
│   │   │
│   │   ├── goal_planner/        # [PHASE 1] Goal Planner Agent (Sinh lộ trình dài hạn từ mục tiêu)
│   │   │   ├── agent.py         # Logic xử lý và dựng đồ thị agent (LangGraph)
│   │   │   └── schemas.py       # Pydantic Structured Output cho lộ trình học
│   │   │
│   │   ├── daily_planner/       # [PHASE 2] Daily Study Planner Agent (Lên lịch chi tiết từng ngày)
│   │   │   ├── agent.py
│   │   │   └── schemas.py
│   │   │
│   │   ├── quiz_generator/      # [PHASE 3] Quiz Generator Agent (Sinh đề thi tự động theo độ khó)
│   │   │   ├── agent.py
│   │   │   └── schemas.py
│   │   │
│   │   ├── auto_grading/        # [PHASE 4] Auto Grading Agent (Chấm bài tự luận/phức tạp nếu cần)
│   │   │   └── agent.py
│   │   │
│   │   ├── analytics_agent/     # [PHASE 5] Learning Analytics Agent (Đánh giá điểm yếu/mạnh học lực)
│   │   │   └── agent.py
│   │   │
│   │   ├── recommender/         # [PHASE 6] Recommendation Agent (Đề xuất bài ôn tập mới)
│   │   │   └── agent.py
│   │   │
│   │   ├── chat_tutor/          # [PHASE 7] Chat Tutor Agent (Chatbot kèm RAG & Memory hỗ trợ học tập)
│   │   │   ├── agent.py
│   │   │   └── memory.py        # Quản lý ngữ cảnh & lịch sử hội thoại từ MongoDB
│   │   │
│   │   └── teacher_assistant/   # [PHASE 8] Teacher Assistant Agent (Hỗ trợ giáo viên tạo/tối ưu đề thi)
│   │       └── agent.py
│   │
│   ├── workers/                 # Tầng lập lịch và xử lý tác vụ ngầm (Background Workers)
│   │   ├── celery_app.py        # Cấu hình Celery (Sử dụng Redis làm Broker)
│   │   ├── tasks.py             # Định nghĩa các task chạy ngầm (Gửi notification, sync analytics...)
│   │   └── scheduler.py         # [PHASE 9] APScheduler (Tự động quét study_plans lúc 08:00 sáng hàng ngày)
│   │
│   └── tests/                   # Tầng viết test (Unit Test, Integration Test)
│       ├── conftest.py          # Setup môi trường test (Test DB, mock AI)
│       ├── test_api/            # Test cho các APIs
│       └── test_agents/         # Test độ chính xác của các AI Agents
│
├── .env.example                 # File mẫu chứa các biến môi trường
├── .gitignore                   # Loại trừ các file không cần commit lên Git
├── alembic.ini                  # Cấu hình Alembic để migration DB
├── Dockerfile                   # Dockerfile đóng gói ứng dụng Backend FastAPI
├── docker-compose.yml           # Orchestration khởi chạy nhanh FastAPI, MySQL, MongoDB, Redis, Celery
├── requirements.txt             # Danh sách thư viện Python
└── README.md                    # File hướng dẫn dự án
```

---

## 🔍 Giải thích chi tiết các thành phần chính trong hệ thống

### 1. Database Layer (Tầng cơ sở dữ liệu)
Hệ thống sử dụng mô hình kết hợp **Hybrid Database** để đáp ứng tốt nhất các loại dữ liệu khác nhau:
- **MySQL (SQLAlchemy)** (`app/models/`): Lưu trữ dữ liệu cấu trúc cao, yêu cầu tính toàn vẹn (ACID) như thông tin người dùng, môn học, mục tiêu, kết quả làm bài, và kế hoạch học tập. Các quan hệ được ràng buộc chặt chẽ bằng Foreign Key.
- **MongoDB** (`app/database/mongodb.py`): Lưu trữ dữ liệu phi cấu trúc, mở rộng linh hoạt:
  - `chat_sessions`: Quản lý các phiên hội thoại của học sinh.
  - `chat_messages`: Lưu chi tiết các câu chat theo dạng chuỗi lịch sử (Memory cho Chat Tutor).
  - `ai_logs`: Log chi tiết Input/Output của các Agent nhằm mục đích giám sát chất lượng và tinh chỉnh (fine-tune) prompt sau này.
- **Redis** (`app/database/redis.py`):
  - **Caching**: Lưu phiên đăng nhập (`session:user:1`), dữ liệu Dashboard trang chủ của học sinh để load tức thì (`dashboard:1`), cache đề thi (`quiz:5`).
  - **Broker/Backend**: Làm hàng đợi cho Celery xử lý gửi thông báo ngầm hoặc đồng bộ dữ liệu.

### 2. Tầng AI Agents (`app/agents/`)
Đây là **Trái tim** của dự án (AI Learning Assistant). Mỗi Agent được đặt trong một thư mục riêng biệt giúp dễ bảo trì và mở rộng:
- **`tools/`**: Chứa các "kỹ năng" ngoại vi cho AI.
  - Ví dụ: `datetime_tool.py` giúp Agent xác định thời gian hiện tại chính xác tuyệt đối để phân tích xem học sinh có đang bị chậm deadline kế hoạch hay không.
- **`prompts.py`**: Quản lý tập trung toàn bộ System Prompt. Giúp lập trình viên dễ dàng điều chỉnh hành vi của AI mà không cần can thiệp sâu vào code logic.
- **Structured Output**: Sử dụng **Pydantic** trong từng agent (`schemas.py`) kết hợp với tính năng `response_format` của OpenAI/Gemini để ép AI trả về dữ liệu chuẩn JSON 100%, phục vụ việc ghi trực tiếp vào MySQL (như tạo quiz, tạo lịch học).

### 3. Tầng Repositories (`app/repositories/`)
- Đảm nhận toàn bộ các tác vụ truy vấn, cập nhật cơ sở dữ liệu (MySQL & MongoDB).
- Tách biệt hoàn toàn phần query raw SQL hoặc SQLAlchemy ORM ra khỏi tầng Business Logic (`services/`), giúp code dễ test, bảo trì và tái sử dụng.
- Kế thừa một `BaseRepository` chung chứa các hàm CRUD cơ bản (get, get_multi, create, update, delete).

### 4. Tầng Background Workers & Notifications (`app/workers/`)
- Giải quyết bài toán: Không làm nghẽn luồng Request-Response chính của người dùng khi cần thực hiện các tác vụ tốn thời gian.
- **APScheduler** (`app/workers/scheduler.py`): Thực hiện cronjob mỗi ngày (ví dụ 08:00 sáng), quét bảng `study_plans` tìm các task của ngày hôm đó và kích hoạt gửi thông báo qua bảng `notifications`.
- **Celery** (`app/workers/tasks.py`): Xử lý không đồng bộ các nhiệm vụ nặng như sinh phân tích học tập (`learning_analytics`) sau khi sinh viên hoàn thành quiz.

### 5. Tầng API (`app/api/`) và Streaming
- **SSE (Server-Sent Events) hoặc WebSocket** (`app/api/v1/chat.py`): Được dùng để thực hiện streaming câu trả lời từ AI (như ChatGPT). SSE được ưa chuộng hơn cho việc stream text 1 chiều vì nó chạy trực tiếp trên giao thức HTTP thông thường và tự động kết nối lại khi mất mạng.

---

## ⚡ Các luồng hoạt động chính (Workflow) của Hệ thống

### Luồng 1: Sinh lộ trình học tập dài hạn (Goal -> Study Plan)
1. Học sinh gửi Request đặt mục tiêu (`POST /api/v1/goals/`).
2. API nhận dữ liệu -> gọi `GoalPlannerAgent` (`app/agents/goal_planner/`).
3. Agent kết hợp thông tin mức học lực hiện tại (`learning_level`) + môn học -> sinh lộ trình các tuần (JSON).
4. `GoalService` nhận JSON lộ trình -> phân tách thành các task cụ thể và lưu vào cơ sở dữ liệu MySQL (`study_plans`).

### Luồng 2: Làm bài thi và Chấm điểm tự động (Quiz -> Attempt -> Analytics)
1. Học sinh nộp bài làm (`POST /api/v1/quizzes/{id}/submit`).
2. `AutoGradingAgent` (hoặc Service logic nếu là MCQ) tính toán số câu đúng/sai và lưu kết quả vào `quiz_attempts`.
3. Một Celery Task ngầm được đẩy vào queue -> Gọi `LearningAnalyticsAgent` (`app/agents/analytics_agent/`) để phân tích:
   - Đọc 20 bài làm gần nhất của học sinh.
   - Nhận diện các phần kiến thức yếu (`weak_topics`) và mạnh (`strong_topics`).
   - Cập nhật thông tin vào bảng `learning_analytics`.
4. Gọi tiếp `RecommendationAgent` để tạo các task ôn tập bổ sung vào `study_plans` của học sinh cho ngày tiếp theo.
