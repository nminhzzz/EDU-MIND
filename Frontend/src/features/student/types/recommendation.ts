/** Matches Backend AIRecommendationReviewResponse (student view). */
export interface AIRecommendation {
  id: number;
  student_id: number;
  teacher_id: number | null;
  recommendation: string;
  teacher_feedback: string | null;
  status: "pending" | "approved" | "rejected" | string;
  created_at: string;
}
