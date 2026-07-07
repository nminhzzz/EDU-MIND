"use client";

import React, { useEffect, useState } from "react";
import { recommendationApi, AIRecommendation } from "@/services/recommendation";
import { MarkdownText } from "@/components/student/markdown-text";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, Calendar, MessageSquare, AlertCircle, RefreshCw } from "lucide-react";
import { toast } from "sonner";

export default function StudentRecommendationsPage() {
  const [recommendations, setRecommendations] = useState<AIRecommendation[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const response = await recommendationApi.getMyRecommendations();
      setRecommendations(response.data);
    } catch (err: any) {
      console.error("Lỗi khi tải danh sách đề xuất:", err);
      toast.error("Không thể tải danh sách đề xuất ôn tập AI.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("vi-VN", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="max-w-4xl mx-auto py-6 px-4 text-left space-y-6">
      {/* Header Banner */}
      <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-8 rounded-2xl shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-zinc-900 dark:text-white">
              Đề xuất ôn tập từ AI
            </h1>
            <Sparkles className="w-5 h-5 text-indigo-500 animate-pulse" />
          </div>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
            Tổng hợp các đề xuất ôn tập cá nhân hóa do AI biên soạn sau khi bạn hoàn thành các bài thi thử.
          </p>
        </div>
        <button
          onClick={fetchRecommendations}
          disabled={loading}
          className="p-3 bg-zinc-50 hover:bg-zinc-100 dark:bg-zinc-950 dark:hover:bg-zinc-900 border border-zinc-250 dark:border-zinc-750 hover:border-zinc-800 dark:hover:border-zinc-200 rounded-xl transition-all cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 text-zinc-650 dark:text-zinc-400 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

      {/* Main Content */}
      <AnimatePresence mode="wait">
        {loading ? (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="py-24 text-center space-y-4"
          >
            <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400 font-mono">
              Đang tải danh sách đề xuất ôn tập AI...
            </p>
          </motion.div>
        ) : recommendations.length === 0 ? (
          <motion.div
            key="empty"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-12 rounded-2xl text-center shadow-sm space-y-4"
          >
            <div className="w-12 h-12 bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 rounded-full flex items-center justify-center mx-auto">
              <AlertCircle className="w-6 h-6" />
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-extrabold text-zinc-800 dark:text-zinc-250">
                Chưa có đề xuất ôn tập nào
              </h3>
              <p className="text-xs text-zinc-500 dark:text-zinc-400 max-w-md mx-auto leading-relaxed">
                Đề xuất ôn tập từ AI sẽ được tự động tạo khi bạn làm bài thi thử đạt kết quả dưới 8.0 điểm. Hãy tiếp tục cố gắng trong các bài kiểm tra nhé!
              </p>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="list"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-4"
          >
            {recommendations.map((rec) => (
              <motion.div
                key={rec.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm hover:border-indigo-300 dark:hover:border-indigo-800 transition-all duration-200"
              >
                {/* Recommendation Header */}
                <div className="flex items-center justify-between pb-3 border-b border-zinc-100 dark:border-zinc-800/80 mb-4">
                  <div className="flex items-center gap-2 text-zinc-400 dark:text-zinc-500 font-mono text-xs">
                    <Calendar className="w-4 h-4 text-indigo-500" />
                    <span>{formatDate(rec.created_at)}</span>
                  </div>
                  <span className="text-[10px] font-extrabold px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 rounded-full">
                    Đã duyệt & áp dụng
                  </span>
                </div>

                {/* Recommendation Body */}
                <div className="space-y-3">
                  <div className="text-sm text-zinc-750 dark:text-zinc-350 leading-relaxed font-medium bg-zinc-50/50 dark:bg-zinc-950/20 border border-zinc-200/40 dark:border-zinc-850/80 p-4 rounded-xl text-left">
                    <MarkdownText content={rec.recommendation} />
                  </div>
                </div>

                {/* Teacher Feedback (if any) */}
                {rec.teacher_feedback && (
                  <div className="mt-4 p-4 border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950/40 rounded-xl flex gap-3 text-left">
                    <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 flex items-center justify-center shrink-0">
                      <MessageSquare className="w-4 h-4" />
                    </div>
                    <div>
                      <span className="text-[10px] font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider block font-mono">
                        Lời nhắn của thầy cô
                      </span>
                      <p className="text-xs text-zinc-650 dark:text-zinc-450 mt-1 font-medium italic">
                        "{rec.teacher_feedback}"
                      </p>
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
