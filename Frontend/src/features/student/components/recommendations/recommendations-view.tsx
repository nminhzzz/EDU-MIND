"use client";

import React from "react";
import { AIRecommendation } from "@/features/student/types/recommendation";
import { RecommendationsHeader } from "./recommendations-header";
import { RecommendationsList } from "./recommendations-list";

interface RecommendationsViewProps {
  recommendations: AIRecommendation[];
  loading: boolean;
  onRefresh: () => void;
}

export function RecommendationsView({
  recommendations,
  loading,
  onRefresh,
}: RecommendationsViewProps) {
  return (
    <div className="max-w-4xl mx-auto py-6 px-4 text-left space-y-6">
      <RecommendationsHeader loading={loading} onRefresh={onRefresh} />
      <RecommendationsList recommendations={recommendations} loading={loading} />
    </div>
  );
}
