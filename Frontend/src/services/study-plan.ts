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

  updatePlanStatus: (planId: number, status: "todo" | "doing" | "done") =>
    apiClient.patch<StudyPlan>(`/plans/${planId}`, { status }),
};

export default studyPlanApi;
