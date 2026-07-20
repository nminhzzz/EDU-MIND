export interface QuizQuestion {
  question_text: string;
  options: string[];
  correct_answer?: string;
  explanation?: string;
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
  answers: Record<string, string>;
  score: number;
  is_passed: boolean;
  created_at: string;
}

/** Matches Backend get_student_quiz_attempts history item. */
export interface QuizAttemptHistory {
  attempt_id: number;
  quiz_id: number;
  quiz_title: string;
  score: number;
  correct_count: number;
  wrong_count: number;
  duration_seconds: number;
  tab_violations_count: number;
  submitted_at: string;
}
