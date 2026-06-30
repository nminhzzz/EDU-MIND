import { apiClient } from "./api-client";

export interface StudentPreference {
  id: number;
  student_id: number;
  study_hours_per_day: number;
  preferred_study_time: "morning" | "afternoon" | "evening";
  available_schedule: Record<string, boolean>;
}

export interface Subject {
  id: number;
  name: string;
  code: string;
  description?: string;
}

export interface DraftRequest {
  subject_id: number;
  target_score: number;
  deadline: string;
  user_message?: string;
  session_id?: string;
}

export interface DraftResponse {
  message: string;
  session_id: string;
  plan: {
    weeks: Array<{
      week: number;
      tasks: string[];
    }>;
    daily_schedule: Array<{
      date: string;
      start_time: string;
      end_time: string;
      task: string;
      description: string;
    }>;
    curriculum_materials: Array<{
      topic: string;
      content: string;
    }>;
    quizzes: Array<{
      title: string;
      questions: any[];
    }>;
  };
}

export interface ConfirmRequest {
  subject_id: number;
  target_score: number;
  deadline: string;
  session_id: string;
}

export interface StudyGoalResponse {
  id: number;
  student_id: number;
  subject_id: number;
  title: string;
  target_score: number;
  deadline: string;
  status: "active" | "completed" | "cancelled";
  created_at: string;
}

export const goalApi = {
  /**
   * Lấy cấu hình lịch học cá nhân của học sinh
   */
  getPreferences: () =>
    apiClient.get<StudentPreference>("/users/preferences"),

  /**
   * Cập nhật/Khởi tạo cấu hình lịch học cá nhân
   */
  updatePreferences: (data: { study_hours_per_day: number; preferred_study_time: string; available_schedule: Record<string, boolean> }) =>
    apiClient.put<StudentPreference>("/users/preferences", data),

  /**
   * Lấy danh sách tất cả các môn học
   */
  getSubjects: () =>
    apiClient.get<Subject[]>("/subjects/"),

  /**
   * Lấy danh sách lộ trình học của học sinh
   */
  getGoals: () =>
    apiClient.get<StudyGoalResponse[]>("/goals/"),

  /**
   * Xóa một lộ trình học tập
   */
  deleteGoal: (id: number) =>
    apiClient.delete<{ message: string }>(`/goals/${id}`),

  /**
   * Tạo lộ trình nháp (hoặc gửi tin nhắn thảo luận tinh chỉnh)
   */
  createDraft: (data: DraftRequest) =>
    apiClient.post<DraftResponse>("/goals/unified/draft", data),

  /**
   * Xác nhận lưu chính thức lộ trình nháp vào MySQL
   */
  confirmDraft: (data: ConfirmRequest) =>
    apiClient.post<{ message: string; total_plans: number; total_quizzes: number }>("/goals/unified/confirm", data),
};

export default goalApi;
