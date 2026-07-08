export interface QuizOption {
  key: string;
  value: string;
}

export interface StudentQuizQuestion {
  question_text: string;
  options: QuizOption[];
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
}

export interface QuizAttemptResult {
  score: number;
  correct_count: number;
  wrong_count: number;
}

export interface GenerateQuizPayload {
  subject_id: number;
  topic: string;
  difficulty: string;
  total_questions: number;
  study_plan_id?: number;
}

export interface GenerateQuizFormState {
  subject_id: string;
  topic: string;
  difficulty: string;
  total_questions: number;
}

export type { QuizAttemptHistory } from "@/types/quiz";
