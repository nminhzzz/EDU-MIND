export interface QuizOption {
  key: string;
  value: string;
}

export interface StudentQuizQuestion {
  question_text: string;
  question_type?: "mcq" | "true_false" | "essay";
  options?: QuizOption[];
  correct_answer?: string;
  explanation?: string;
}

/** Quiz payload used by student take/review/quick-quiz flows. */
export interface StudentQuiz {
  id: number;
  title: string;
  difficulty?: string;
  total_questions: number;
  questions: StudentQuizQuestion[];
  deadline?: string;
  time_limit_minutes?: number;
  max_tab_violations?: number;
  classroom_id?: number;
  created_at?: string;
  latest_attempt?: any;
}

export interface GeneratedQuiz {
  id: number;
  title: string;
  questions?: StudentQuizQuestion[];
}

export interface QuizSubmitAnswer {
  question_index: number;
  answer: string;
  is_correct?: boolean;
}

export interface QuizSubmitPayload {
  answers: QuizSubmitAnswer[];
  duration_seconds: number;
  tab_violations_count: number;
  essay_file_path?: string;
}

export interface AIAssessment {
  overall_feedback: string;
  strengths?: string[];
  weaknesses?: string[];
  recommendation?: string;
}

export interface QuizAttemptResult {
  id: number;
  quiz_id: number;
  student_id: number;
  score: number;
  correct_count: number;
  wrong_count: number;
  duration_seconds: number;
  submitted_at: string;
  tab_violations_count?: number;
  ai_assessment?: AIAssessment | null;
  answers?: {
    question_index: number;
    answer: string;
    is_correct: boolean;
    score?: number;
    feedback?: string;
    essay_file_path?: string | null;
  }[];
}

export type { QuizAttemptHistory } from "@/types/quiz";
