# Ý TƯỞNG BÁO CÁO CHI TIẾT: PHÂN HỆ AI DÀNH CHO GIÁO VIÊN (TEACHER AI SYSTEM)
## TỐI ƯU HÓA BẰNG CÔNG NGHỆ RAG & REDIS CACHE HYBRID - HỆ THỐNG EDU-MIND

Bản báo cáo này đề xuất giải pháp thiết kế kiến trúc và luồng nghiệp vụ cho **Phân hệ AI dành cho Giáo viên** thuộc hệ thống **EDU-MIND**. Hệ thống được tối ưu hóa bằng công nghệ **RAG (Retrieval-Augmented Generation)** và cơ chế **Redis Cache** nhằm giảm thiểu 50% chi phí token, tăng tốc độ phản hồi và nâng cao độ chính xác chuyên môn khi chấm bài và sinh đề thi.

---

## 1. Bản Đồ Tổng Quan Quy Trình Nghiệp Vụ

```
[Giáo viên] ──(Yêu cầu sinh 10 đề)──► [RAG + LLM Generator] ──► [Lưu 10 đề thi MySQL]
                                                                       │
                                                                 (Giao ngẫu nhiên)
                                                                       ▼
[Học sinh] ◄──(Làm bài thi tự luận/MCQ) ◄───────────────────────── [1 Đề thi thử]
    │
    ▼
[AI Auto-Grading Agent] (RAG Đáp án & Rubric chấm từ MongoDB)
    │
    ├─► Trả điểm và nhận xét chi tiết ngay lập tức
    ├─► Cập nhật Lịch sử học lực học sinh (Learning Analytics)
    └─► Gửi thông báo đẩy thời gian thực (SSE Dashboard)
```

---

## 2. Đặc Tả Chi Tiết Các Tính Năng AI Giáo Viên & Tối Ưu Hóa RAG

### 2.1. Sinh Bộ 10 Đề Thi Tự Động & Tiết Kiệm Token (RAG Quiz Generator)
*   **Nhiệm vụ**: Giáo viên yêu cầu: *"Tạo cho tôi 10 đề thi thử về môn Lập trình Java phần Hướng đối tượng"*.
*   **Ứng dụng RAG & Tối ưu hóa**:
    1.  **Chunking & Vector Store**: Tài liệu giáo trình được chia nhỏ thành các đoạn (chunk) khoảng 500 ký tự bằng `RecursiveCharacterTextSplitter` và chuyển thành vector lưu ở MongoDB Vector Search.
    2.  **Top-K Retrieval**: Khi nhận yêu cầu, hệ thống chỉ lấy **Top-K (k=3)** đoạn tài liệu có độ tương đồng cao nhất (> 0.7 similarity threshold). Điều này giúp giảm lượng token ngữ cảnh gửi lên LLM xuống dưới 50% so với việc gửi toàn bộ giáo trình.
    3.  **Redis Cache**: Nếu giáo viên khác yêu cầu sinh đề cùng môn học/chủ đề trong thời gian ngắn, hệ thống sẽ lấy trực tiếp kết quả từ **Redis Cache** mà không gọi LLM để tiết kiệm chi phí.

### 2.2. Cơ Chế Giao Đề Thi Ngẫu Nhiên (Random Quiz Assignment)
*   **Nhiệm vụ**: Khi sinh viên nhấn nút "Vào thi", hệ thống sẽ không chọn một đề cố định mà sẽ sử dụng thuật toán ngẫu nhiên lựa chọn 1 trong bộ 10 đề thi đã được AI sinh ra và lưu trữ sẵn trong MySQL.
*   **Mục đích**: Hạn chế gian lận thi cử và đảm bảo tính khách quan khi sinh viên làm bài.

### 2.3. Tác Tử AI Tự Động Chấm Bài Tự Luận Phức Tạp (AI Auto-Grading Agent)
*   **Nhiệm vụ**: Đối với các câu hỏi tự luận hoặc bài tập viết code, code thông thường không thể tự chấm. **Auto-Grading Agent** sẽ tự động đọc bài làm của học sinh và đánh giá điểm số.
*   **Ứng dụng RAG & Tối ưu hóa**:
    1.  **RAG Context**: AI truy vấn đáp án mẫu (Sample Answer) và thang điểm chi tiết (Scoring Rubric) của câu hỏi tương ứng lưu trong MongoDB.
    2.  **Chấm điểm & Nhận xét**: AI so sánh bài làm của học sinh với đáp án mẫu theo các tiêu chí (Đúng cú pháp, thuật toán tối ưu, giải thích rõ ràng). Trả về điểm số hệ 10.0, chỉ ra dòng code lỗi và viết nhận xét bồi dưỡng kiến thức.

### 2.4. Lưu Hồ Sơ Học Lực (Analytics Record & SSE Dashboard)
*   **Nhiệm vụ**: Ghi nhận kết quả chấm bài vào MySQL (`QuizAttempt`) và tự động kích hoạt **Analytics Agent** để cập nhật điểm yếu/điểm mạnh môn học vào bảng `learning_analytics`.
*   **Đẩy dữ liệu Real-time**: Kích hoạt sự kiện SSE gửi trực tiếp kết quả phân tích học lực về Dashboard của sinh viên ngay khi AI chấm điểm xong.

---

## 3. Sơ Đồ Tuần Tự (Sequence Diagram) Toàn Bộ Luồng Xử Lý

sequenceDiagram
    autonumber

    actor Teacher as GiaoVien
    actor Student as SinhVien

    participant FE as Frontend
    participant BE as Backend
    participant Cache as Redis
    participant DB_MySQL as MySQL
    participant DB_Mongo as MongoDB
    participant LLM as LLM

    Note over Teacher,LLM: Giai doan A Sinh bo 10 de thi bang RAG va Cache

    Teacher->>FE: Yeu cau tao bo 10 de thi chu de X

    FE->>BE: Generate Quiz Set

    BE->>Cache: Kiem tra bo de trong cache

    alt Cache Hit

        Cache-->>BE: Tra ve bo 10 de thi

    else Cache Miss

        BE->>DB_Mongo: Vector Search tai lieu chu de X

        DB_Mongo-->>BE: Tra ve cac chunks tai lieu

        BE->>LLM: Prompt + RAG Context

        Note over LLM: Sinh 10 de thi gom MCQ va tu luan

        LLM-->>BE: Quiz Set JSON

        BE->>Cache: Luu bo de TTL 3600s

    end

    BE->>DB_MySQL: Luu Quizzes

    BE->>DB_MySQL: Luu Questions

    BE-->>FE: Tao bo de thanh cong

    FE-->>Teacher: Hien thi 10 de thi

    Note over Student,DB_MySQL: Giai doan B Giao de ngau nhien va Lam bai

    Student->>FE: Vao thi khao sat

    FE->>BE: Random Assign Quiz

    Note over BE: Random 1 trong 10 de thi

    BE->>DB_MySQL: Lay chi tiet de thi

    DB_MySQL-->>BE: Tra ve de thi

    BE-->>FE: Gui de thi

    FE-->>Student: Hien thi de thi

    Student->>FE: Nop bai lam

    FE->>BE: Submit Quiz

    Note over BE,LLM: Giai doan C AI Auto Grading

    BE->>DB_Mongo: Lay Rubric va Dap an mau

    DB_Mongo-->>BE: Tra ve dap an chuan

    BE->>LLM: Auto Grading Agent

    Note over LLM: Cham diem va viet nhan xet

    LLM-->>BE: Score va Feedback

    BE->>DB_MySQL: Luu QuizAttempt

    BE->>DB_MySQL: Tao Notification

    BE-->>FE: Tra ket qua cham diem

    FE-->>Student: Hien thi diem va nhan xet

    Note over BE,Student: Giai doan D Learning Analytics va SSE

    Note over BE: Kich hoat update_student_analytics

    BE->>DB_MySQL: Lay lich su QuizAttempt

    DB_MySQL-->>BE: Tra ve lich su diem

    BE->>LLM: Analytics Agent

    LLM-->>BE: Learning Analytics

    BE->>DB_MySQL: Update learning_analytics

    BE->>FE: Gui SSE realtime update

    FE-->>Student: Dashboard cap nhat ngay lap tuc

## 4. Giải Thích Chi Tiết Luồng Hoạt Động Của Sơ Đồ

### 4.1. Giai đoạn A: Giáo viên tạo bộ 10 đề thi (RAG + Cache)
1.  Giáo viên gửi yêu cầu tạo bộ 10 đề thi kèm chủ đề thông qua giao diện Frontend.
2.  Backend tiếp nhận và kiểm tra trong bộ nhớ đệm **Redis Cache** xem chủ đề này đã từng được sinh đề thi trước đó chưa để tránh gọi trùng lặp (giảm chi phí API).
3.  Nếu không có sẵn trong Redis (Cache Miss), Backend gọi hàm nhúng vector để tìm các giáo trình dạy học liên quan nhất trong **MongoDB Vector DB** (Kỹ thuật RAG).
4.  Ngữ cảnh tài liệu thu gọn được gửi kèm Prompt yêu cầu tạo 10 đề thi lên LLM. AI trả về JSON có cấu trúc chứa 10 bộ đề thi gồm các câu hỏi trắc nghiệm (MCQ) xen lẫn tự luận mở rộng.
5.  Dữ liệu này được lưu vào **Redis Cache** (phục vụ lấy nhanh) và đồng bộ lưu vào cơ sở dữ liệu **MySQL** (bảng `quizzes`, `questions`, `question_bank`).

### 4.2. Giai đoạn B: Sinh viên vào thi ngẫu nhiên & làm bài
6.  Sinh viên nhấn nút "Vào thi", Frontend gửi yêu cầu lấy đề thi ngẫu nhiên.
7.  Backend truy vấn danh sách 10 đề thuộc lớp học hiện tại trong MySQL và sử dụng thuật toán ngẫu nhiên lấy ra 1 đề duy nhất.
8.  Backend trả thông tin đề thi đã ẩn các đáp án đúng về Frontend để sinh viên làm bài thi (hạn chế tối đa gian lận thi cử).
9.  Sinh viên làm bài (chọn đáp án trắc nghiệm + gõ câu trả lời/code tự luận) và nhấn Nộp bài.

### 4.3. Giai đoạn C: AI tự chấm điểm tự luận (Auto-Grading RAG)
10. Backend tiếp nhận bài làm của sinh viên. Với phần trắc nghiệm, hệ thống tự động so khớp đáp án. Với phần tự luận/viết code, hệ thống truy xuất **Thang điểm chấm (Rubric)** và **Đáp án mẫu** lưu trong MongoDB làm ngữ cảnh tham chiếu.
11. Hệ thống gửi bài làm của sinh viên cùng với Rubric chấm chuẩn lên **Auto-Grading Agent** để chấm điểm tự luận khách quan.
12. AI trả về kết quả đánh giá chi tiết theo từng tiêu chí (ví dụ: Tính đóng gói trong OOP đạt 2/2 điểm; Kế thừa bị viết sai cú pháp đạt 0/2 điểm,...).
13. Backend lưu kết quả chấm vào MySQL bảng `QuizAttempt`, tạo thông báo điểm và trả về màn hình cho học sinh.

### 4.4. Giai đoạn D: Đánh giá học lực & Đẩy Dashboard Real-time (SSE)
14. Hệ thống tự động kích hoạt tác vụ ngầm tính toán lại học lực môn học của sinh viên.
15. **Analytics Agent** đọc lịch sử làm bài mới nhất, phân tích sự thay đổi điểm số và xác định các điểm yếu/điểm mạnh mới để cập nhật bảng `learning_analytics`.
16. Ngay khi dữ liệu được ghi nhận vào database, Backend phát đi một sự kiện mạng (SSE Event) qua đường truyền **Server-Sent Events** đã kết nối sẵn với Frontend của sinh viên.
17. Màn hình Dashboard học tập của sinh viên tự động cập nhật ngay lập tức các con số thống kê và cảnh báo điểm yếu mới mà sinh viên không cần thực hiện tải lại trang (reload).
