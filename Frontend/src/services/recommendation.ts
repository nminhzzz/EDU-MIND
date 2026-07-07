import { apiClient } from "./api-client";

export interface AIRecommendation {
  id: number;
  student_id: number;
  teacher_id: number | null;
  recommendation: string;
  teacher_feedback: string | null;
  status: "pending" | "approved" | "rejected";
  created_at: string;
}

export const recommendationApi = {
  getMyRecommendations: () => {
    return apiClient.get<AIRecommendation[]>("/recommendations/my-recommendations");
  }
};
