"use client";

import React from "react";
import { AnimatePresence, motion } from "framer-motion";
import { AIRecommendation } from "@/features/student/types/recommendation";
import { RecommendationCard } from "./recommendation-card";
import { RecommendationsEmptyState } from "./recommendations-empty-state";
import { RecommendationsLoadingState } from "./recommendations-loading-state";

interface RecommendationsListProps {
  recommendations: AIRecommendation[];
  loading: boolean;
}

export function RecommendationsList({ recommendations, loading }: RecommendationsListProps) {
  return (
    <AnimatePresence mode="wait">
      {loading ? (
        <RecommendationsLoadingState />
      ) : recommendations.length === 0 ? (
        <RecommendationsEmptyState />
      ) : (
        <motion.div
          key="list"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="space-y-4"
        >
          {recommendations.map((rec) => (
            <RecommendationCard key={rec.id} recommendation={rec} />
          ))}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
