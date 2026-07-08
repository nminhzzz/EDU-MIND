import { apiClient } from "@/services/api-client";
import type { QuizAttemptHistory } from "@/features/student/types";
import {
  GenerateQuizPayload,
  GeneratedQuiz,
  QuizAttemptResult,
  QuizSubmitPayload,
  StudentQuiz,
} from "@/features/student/types/quiz";

export const quizService = {
  getHistory: () => apiClient.get<QuizAttemptHistory[]>("/quizzes/student/history"),

  getById: (quizId: string | number) =>
    apiClient.get<StudentQuiz>(`/quizzes/${quizId}`),

  getReview: (quizId: string | number) =>
    apiClient.get<StudentQuiz>(`/quizzes/${quizId}/review`),

  getByPlanId: (studyPlanId: number) =>
    apiClient.get<StudentQuiz>(`/quizzes/plan/${studyPlanId}`),

  generate: (payload: GenerateQuizPayload) =>
    apiClient.post<GeneratedQuiz>("/quizzes/generate", payload),

  submit: (quizId: string | number, payload: QuizSubmitPayload) =>
    apiClient.post<QuizAttemptResult>(`/quizzes/${quizId}/submit`, payload),
};

export default quizService;
