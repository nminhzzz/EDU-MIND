import { apiClient } from "@/services/api-client";
import type { QuizAttemptHistory } from "@/features/student/types";
import {
  QuizAttemptResult,
  QuizSubmitPayload,
  StudentQuiz,
} from "@/features/student/types/quiz";

export const quizService = {
  getHistory: () => apiClient.get<QuizAttemptHistory[]>("/quizzes/student/history"),

  getAssigned: () => apiClient.get<StudentQuiz[]>("/quizzes/student/assigned"),

  getById: (quizId: string | number) =>
    apiClient.get<StudentQuiz>(`/quizzes/${quizId}`),

  getReview: (quizId: string | number) =>
    apiClient.get<StudentQuiz>(`/quizzes/${quizId}/review`),

  getByPlanId: (studyPlanId: number) =>
    apiClient.get<StudentQuiz>(`/quizzes/plan/${studyPlanId}`),

  generateForPlan: (studyPlanId: number) =>
    apiClient.post<StudentQuiz>(`/quizzes/plan/${studyPlanId}/generate`, null, {
      timeout: 120_000,
    }),

  submit: (quizId: string | number, payload: QuizSubmitPayload) =>
    apiClient.post<QuizAttemptResult>(`/quizzes/${quizId}/submit`, payload),

  uploadEssay: (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return apiClient.post<{ file_path: string }>("/quizzes/upload-essay", fd, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default quizService;
