import { apiClient } from "@/services/api-client";
import type { QuizAttemptHistory } from "@/features/student/types";
import {
  GenerateQuizPayload,
  GeneratedQuiz,
  QuizAttemptResult,
  QuizSubmitPayload,
  StudentQuiz,
} from "@/features/student/types/quiz";

/** AI quiz generation (RAG + LLM + QC) often takes 30–90s. Default axios timeout is 30s. */
const AI_QUIZ_GENERATE_TIMEOUT_MS = 120_000;

export const quizService = {
  getHistory: () => apiClient.get<QuizAttemptHistory[]>("/quizzes/student/history"),

  getById: (quizId: string | number) =>
    apiClient.get<StudentQuiz>(`/quizzes/${quizId}`),

  getReview: (quizId: string | number) =>
    apiClient.get<StudentQuiz>(`/quizzes/${quizId}/review`),

  getByPlanId: (studyPlanId: number) =>
    apiClient.get<StudentQuiz>(`/quizzes/plan/${studyPlanId}`),

  generate: (payload: GenerateQuizPayload) =>
    apiClient.post<GeneratedQuiz>("/quizzes/generate", payload, {
      timeout: AI_QUIZ_GENERATE_TIMEOUT_MS,
    }),

  submit: (quizId: string | number, payload: QuizSubmitPayload) =>
    apiClient.post<QuizAttemptResult>(`/quizzes/${quizId}/submit`, payload),
};

export default quizService;
