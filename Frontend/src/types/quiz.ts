export interface QuizQuestion {
  question_text: string;
  options: string[];
  correct_answer?: string; // Tùy chọn, bị ẩn khi học sinh làm bài
  explanation?: string;    // Giải thích chi tiết đáp án
}

export interface Quiz {
  id: number;
  title: string;
  description: string | null;
  student_id: number;
  study_plan_id: number | null;
  questions: QuizQuestion[];
  is_active: boolean;
  created_at: string;
}

export interface QuizAttempt {
  id: number;
  quiz_id: number;
  student_id: number;
  answers: Record<string, string>; // Mapping chỉ số câu hỏi (ví dụ: "0") sang phương án lựa chọn (ví dụ: "A")
  score: number;
  is_passed: boolean;
  created_at: string;
}
