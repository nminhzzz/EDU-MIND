import { apiClient } from "./api-client";

/** Matches Backend StudyPlanResponse. */
export interface StudyPlan {
  id: number;
  student_id: number;
  goal_id: number;
  subject_id?: number | null;
  title: string;
  task_description?: string | null;
  rag_content?: string | null;
  lesson_summary?: string | null;
  generation_status: "not_started" | "queued" | "generating" | "ready" | "failed";
  lesson_status: "not_started" | "queued" | "generating" | "ready" | "failed";
  quiz_status: "not_started" | "queued" | "generating" | "ready" | "failed";
  generation_error?: string | null;
  generation_attempts: number;
  generation_started_at?: string | null;
  generation_finished_at?: string | null;
  study_date: string;
  start_time: string;
  end_time: string;
  ai_generated?: boolean;
  status: "todo" | "doing" | "done";
  created_at: string;
}

export const studyPlanApi = {
  getPlans: (params?: {
    goal_id?: number;
    status_filter?: string;
    start_date?: string;
    end_date?: string;
  }) => apiClient.get<StudyPlan[]>("/plans/", { params }),

  getPlan: (planId: number) => apiClient.get<StudyPlan>(`/plans/${planId}`),

  startGeneration: (planId: number) =>
    apiClient.post<StudyPlan>(`/plans/${planId}/generation`),

  retryGeneration: (planId: number) =>
    apiClient.post<StudyPlan>(`/plans/${planId}/generation/retry`),

  updatePlanStatus: (planId: number, status: "todo" | "doing" | "done") =>
    apiClient.patch<StudyPlan>(`/plans/${planId}`, { status }),
};

export default studyPlanApi;
