"use client";

import React from "react";
import { RecommendationsView } from "@/features/student/components/recommendations/recommendations-view";
import { useRecommendations } from "@/features/student/hooks/use-recommendations";

export default function StudentRecommendationsPage() {
  const { recommendations, loading, fetchRecommendations } = useRecommendations();

  return (
    <RecommendationsView
      recommendations={recommendations}
      loading={loading}
      onRefresh={fetchRecommendations}
    />
  );
}
