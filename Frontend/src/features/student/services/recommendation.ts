import { apiClient } from "@/services/api-client";
import { AIRecommendation } from "@/features/student/types/recommendation";

export const recommendationService = {
  getMyRecommendations: () =>
    apiClient.get<AIRecommendation[]>("/recommendations/my-recommendations"),
};

export default recommendationService;
