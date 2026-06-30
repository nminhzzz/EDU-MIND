import { apiClient } from "./api-client";

export interface StudyPlan {
  id: number;
  goal_id: number;
  student_id: number;
  title: string;
  task_description: string;
  study_date: string;
  start_time: string;
  end_time: string;
  status: "todo" | "doing" | "done";
  created_at: string;
}

export const studyPlanApi = {
  /**
   * Lấy danh sách nhiệm vụ học tập hàng ngày
   */
  getPlans: (params?: { goal_id?: number; status_filter?: string; start_date?: string; end_date?: string }) =>
    apiClient.get<StudyPlan[]>("/plans/", { params }),

  /**
   * Cập nhật trạng thái nhiệm vụ (todo -> doing -> done)
   */
  updatePlanStatus: (planId: number, status: "todo" | "doing" | "done") =>
    apiClient.patch<StudyPlan>(`/plans/${planId}`, { status }),
};

export default studyPlanApi;
