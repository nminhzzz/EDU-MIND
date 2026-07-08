"use client";

import React from "react";
import { Calendar, MessageSquare } from "lucide-react";
import { motion } from "framer-motion";
import { MarkdownText } from "@/components/student/markdown-text";
import { AIRecommendation } from "@/features/student/types/recommendation";
import { formatRecommendationDate } from "@/features/student/utils/recommendation";

interface RecommendationCardProps {
  recommendation: AIRecommendation;
}

export function RecommendationCard({ recommendation }: RecommendationCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm hover:border-indigo-300 dark:hover:border-indigo-800 transition-all duration-200"
    >
      <div className="flex items-center justify-between pb-3 border-b border-zinc-100 dark:border-zinc-800/80 mb-4">
        <div className="flex items-center gap-2 text-zinc-400 dark:text-zinc-500 font-mono text-xs">
          <Calendar className="w-4 h-4 text-indigo-500" />
          <span>{formatRecommendationDate(recommendation.created_at)}</span>
        </div>
        <span className="text-[10px] font-extrabold px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 rounded-full">
          Đã duyệt & áp dụng
        </span>
      </div>

      <div className="space-y-3">
        <div className="text-sm text-zinc-750 dark:text-zinc-350 leading-relaxed font-medium bg-zinc-50/50 dark:bg-zinc-950/20 border border-zinc-200/40 dark:border-zinc-850/80 p-4 rounded-xl text-left">
          <MarkdownText content={recommendation.recommendation} />
        </div>
      </div>

      {recommendation.teacher_feedback && (
        <div className="mt-4 p-4 border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950/40 rounded-xl flex gap-3 text-left">
          <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 flex items-center justify-center shrink-0">
            <MessageSquare className="w-4 h-4" />
          </div>
          <div>
            <span className="text-[10px] font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider block font-mono">
              Lời nhắn của thầy cô
            </span>
            <p className="text-xs text-zinc-650 dark:text-zinc-450 mt-1 font-medium italic">
              "{recommendation.teacher_feedback}"
            </p>
          </div>
        </div>
      )}
    </motion.div>
  );
}
