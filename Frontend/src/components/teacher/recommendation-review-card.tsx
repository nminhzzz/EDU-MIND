"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  Calendar,
  Check,
  Loader2,
  MessageSquare,
  User,
  X,
} from "lucide-react";
import { AIRecommendation } from "@/services/recommendation";
import { MarkdownText } from "@/components/student/markdown-text";

interface RecommendationReviewCardProps {
  review: AIRecommendation;
  onReview: (
    reviewId: number,
    status: "approved" | "rejected",
    feedback?: string,
  ) => Promise<void>;
  index?: number;
}

export function RecommendationReviewCard({
  review,
  onReview,
  index = 0,
}: RecommendationReviewCardProps) {
  const [feedback, setFeedback] = useState("");
  const [submitting, setSubmitting] = useState<"approved" | "rejected" | null>(
    null,
  );

  const handleAction = async (status: "approved" | "rejected") => {
    setSubmitting(status);
    try {
      await onReview(review.id, status, feedback.trim() || undefined);
      setFeedback("");
    } finally {
      setSubmitting(null);
    }
  };

  const studentName =
    review.student?.full_name || `Học sinh #${review.student_id}`;
  const studentEmail = review.student?.email;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 p-6 rounded-2xl shadow-sm"
    >
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 pb-4 border-b border-zinc-100 dark:border-zinc-800 mb-4">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-xl bg-violet-50 dark:bg-violet-950/40 text-violet-600 dark:text-violet-400 flex items-center justify-center shrink-0">
            <User className="w-5 h-5" />
          </div>
          <div>
            <p className="text-sm font-bold text-zinc-800 dark:text-zinc-200">
              {studentName}
            </p>
            {studentEmail && (
              <p className="text-xs text-zinc-400 mt-0.5">{studentEmail}</p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2 text-zinc-400 dark:text-zinc-500 font-mono text-xs">
          <Calendar className="w-4 h-4 text-violet-500" />
          <span>
            {new Date(review.created_at).toLocaleString("vi-VN", {
              dateStyle: "short",
              timeStyle: "short",
            })}
          </span>
        </div>
      </div>

      <div className="text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed font-medium bg-zinc-50/50 dark:bg-zinc-950/20 border border-zinc-200/40 dark:border-zinc-800 p-4 rounded-xl">
        <MarkdownText content={review.recommendation} />
      </div>

      <div className="mt-4 space-y-3">
        <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
          <span className="inline-flex items-center gap-1.5">
            <MessageSquare className="w-3.5 h-3.5" />
            Lời nhắn cho học sinh (tuỳ chọn)
          </span>
        </label>
        <textarea
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          placeholder="VD: Em hãy ôn lại chương 2 và làm thêm bài tập..."
          rows={2}
          disabled={!!submitting}
          className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-violet-500 focus:border-transparent outline-none resize-none disabled:opacity-60"
        />
      </div>

      <div className="mt-4 flex flex-col sm:flex-row gap-3">
        <button
          type="button"
          onClick={() => handleAction("approved")}
          disabled={!!submitting}
          className="flex-1 py-2.5 px-4 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold text-sm rounded-xl transition-all active:scale-[0.98] flex items-center justify-center gap-2 cursor-pointer"
        >
          {submitting === "approved" ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Check className="w-4 h-4" />
          )}
          Duyệt & gửi cho học sinh
        </button>
        <button
          type="button"
          onClick={() => handleAction("rejected")}
          disabled={!!submitting}
          className="flex-1 py-2.5 px-4 border border-zinc-200 dark:border-zinc-700 hover:bg-zinc-50 dark:hover:bg-zinc-800 disabled:opacity-50 text-zinc-700 dark:text-zinc-300 font-bold text-sm rounded-xl transition-all active:scale-[0.98] flex items-center justify-center gap-2 cursor-pointer"
        >
          {submitting === "rejected" ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <X className="w-4 h-4" />
          )}
          Từ chối
        </button>
      </div>
    </motion.div>
  );
}
