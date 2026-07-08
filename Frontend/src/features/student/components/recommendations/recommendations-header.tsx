"use client";

import React from "react";
import { RefreshCw, Sparkles } from "lucide-react";

interface RecommendationsHeaderProps {
  loading: boolean;
  onRefresh: () => void;
}

export function RecommendationsHeader({ loading, onRefresh }: RecommendationsHeaderProps) {
  return (
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
        onClick={onRefresh}
        disabled={loading}
        className="p-3 bg-zinc-50 hover:bg-zinc-100 dark:bg-zinc-950 dark:hover:bg-zinc-900 border border-zinc-250 dark:border-zinc-750 hover:border-zinc-800 dark:hover:border-zinc-200 rounded-xl transition-all cursor-pointer disabled:opacity-50"
      >
        <RefreshCw className={`w-4 h-4 text-zinc-650 dark:text-zinc-400 ${loading ? "animate-spin" : ""}`} />
      </button>
    </div>
  );
}
