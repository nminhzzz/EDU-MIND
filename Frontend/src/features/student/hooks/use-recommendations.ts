"use client";

import { useCallback, useEffect, useState } from "react";
import { recommendationService } from "@/features/student/services/recommendation";
import { AIRecommendation } from "@/features/student/types/recommendation";
import { parseApiError } from "@/utils/api-error";
import { toast } from "sonner";

export function useRecommendations() {
  const [recommendations, setRecommendations] = useState<AIRecommendation[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchRecommendations = useCallback(async () => {
    setLoading(true);
    try {
      const response = await recommendationService.getMyRecommendations();
      setRecommendations(response.data);
    } catch (err: unknown) {
      console.error("Lỗi khi tải danh sách đề xuất:", err);
      toast.error(parseApiError(err, "Không thể tải danh sách đề xuất ôn tập AI."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRecommendations();
  }, [fetchRecommendations]);

  return {
    recommendations,
    loading,
    fetchRecommendations,
  };
}
