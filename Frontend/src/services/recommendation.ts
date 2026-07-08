import { apiClient } from "./api-client";
import { User } from "@/types/user";

/** Matches Backend AIRecommendationReviewResponse. */
export interface AIRecommendation {
  id: number;
  student_id: number;
  teacher_id: number | null;
  recommendation: string;
  teacher_feedback: string | null;
  status: "pending" | "approved" | "rejected" | string;
  created_at: string;
  student?: User | null;
}

export const recommendationApi = {
  getMyRecommendations: () =>
    apiClient.get<AIRecommendation[]>("/recommendations/my-recommendations"),

  getPendingReviews: () =>
    apiClient.get<AIRecommendation[]>("/recommendations/pending"),

  reviewRecommendation: (
    reviewId: number,
    status: "approved" | "rejected",
    teacherFeedback?: string,
  ) =>
    apiClient.patch<AIRecommendation>(`/recommendations/${reviewId}`, {
      status,
      teacher_feedback: teacherFeedback || null,
    }),
};

export default recommendationApi;
