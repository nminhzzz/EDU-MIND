"use client";

import React, { useCallback, useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertCircle, ClipboardCheck, Sparkles } from "lucide-react";
import { toast } from "sonner";
import {
  AIRecommendation,
  recommendationApi,
} from "@/services/recommendation";
import { RecommendationReviewCard } from "@/components/teacher/recommendation-review-card";
import { parseApiError } from "@/utils/api-error";

export default function TeacherRecommendationsPage() {
  const [reviews, setReviews] = useState<AIRecommendation[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchReviews = useCallback(async () => {
    try {
      const res = await recommendationApi.getPendingReviews();
      setReviews(res.data);
    } catch (err) {
      console.error("Lỗi tải đề xuất chờ duyệt:", err);
      toast.error("Không thể tải danh sách đề xuất.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchReviews();
  }, [fetchReviews]);

  const handleReview = async (
    reviewId: number,
    status: "approved" | "rejected",
    feedback?: string,
  ) => {
    try {
      await recommendationApi.reviewRecommendation(reviewId, status, feedback);
      setReviews((prev) => prev.filter((r) => r.id !== reviewId));
      toast.success(
        status === "approved"
          ? "Đã duyệt đề xuất. Học sinh sẽ thấy trong mục Ôn tập AI."
          : "Đã từ chối đề xuất.",
      );
    } catch (err) {
      toast.error(parseApiError(err, "Không thể cập nhật đề xuất."));
      throw err;
    }
  };

  if (loading) {
    return (
      <div className="py-24 text-center space-y-4">
        <div className="w-10 h-10 border-4 border-violet-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400">
          Đang tải đề xuất chờ duyệt...
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-black text-zinc-900 dark:text-white flex items-center gap-2">
          <ClipboardCheck className="w-7 h-7 text-violet-600 dark:text-violet-400" />
          Duyệt đề xuất ôn tập AI
        </h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1 max-w-2xl">
          Khi học sinh làm bài thi dưới 8 điểm, AI tự động tạo đề xuất ôn tập.
          Bạn xem xét và duyệt trước khi gửi cho học sinh (Human-in-the-loop).
        </p>
      </div>

      {reviews.length > 0 && (
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-xl text-amber-700 dark:text-amber-400 text-sm font-semibold">
          <Sparkles className="w-4 h-4" />
          {reviews.length} đề xuất đang chờ duyệt
        </div>
      )}

      <AnimatePresence mode="wait">
        {reviews.length === 0 ? (
          <motion.div
            key="empty"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="text-center py-16 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl"
          >
            <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-zinc-100 dark:bg-zinc-800 text-zinc-400 flex items-center justify-center">
              <AlertCircle className="w-7 h-7" />
            </div>
            <h3 className="text-sm font-extrabold text-zinc-800 dark:text-zinc-200">
              Không có đề xuất nào cần duyệt
            </h3>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 max-w-md mx-auto mt-2 leading-relaxed">
              Đề xuất mới sẽ xuất hiện khi học sinh trong lớp của bạn làm bài
              thi và cần được AI gợi ý ôn tập thêm.
            </p>
          </motion.div>
        ) : (
          <motion.div
            key="list"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-4"
          >
            {reviews.map((review, idx) => (
              <RecommendationReviewCard
                key={review.id}
                review={review}
                onReview={handleReview}
                index={idx}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
