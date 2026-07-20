"use client";

import React from "react";
import { Clock, Trophy, AlertTriangle } from "lucide-react";
import { StudentQuiz } from "@/features/student/types/quiz";

interface QuizDetailHeaderProps {
  quiz: StudentQuiz;
  isReview: boolean;
  duration: number;
  timeRemaining: number;
  timeLimit: number;
  tabViolations: number;
}

export function QuizDetailHeader({
  quiz,
  isReview,
  duration,
  timeRemaining,
  timeLimit,
  tabViolations,
}: QuizDetailHeaderProps) {
  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  const isTimeCritical = !isReview && timeRemaining < 60 && timeRemaining > 0;

  return (
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <span className="text-[10px] font-bold text-indigo-650 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 px-2.5 py-1 rounded-lg uppercase tracking-wide">
          Độ khó: {quiz.difficulty}
        </span>
        <h1 className="text-xl font-black text-zinc-900 dark:text-white mt-2">{quiz.title}</h1>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        {/* Anti-cheat tab violations indicator */}
        {!isReview && tabViolations > 0 && (
          <div
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
              tabViolations >= 2
                ? "bg-red-50 dark:bg-red-950/40 text-red-650 animate-pulse border border-red-200 dark:border-red-900"
                : "bg-amber-50 dark:bg-amber-950/40 text-amber-650 border border-amber-200 dark:border-amber-900"
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            Rời màn hình: {tabViolations}/3
          </div>
        )}

        {isReview ? (
          <div className="flex items-center gap-2 text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40 px-4 py-2 rounded-xl text-xs font-bold border border-emerald-100 dark:border-emerald-900/40">
            <Trophy className="w-4 h-4" />
            Đã hoàn thành luyện tập
          </div>
        ) : (
          <div
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-black transition-all border ${
              isTimeCritical
                ? "bg-red-500 text-white animate-pulse border-red-600 shadow-md shadow-red-500/20"
                : "bg-indigo-50 dark:bg-indigo-950/40 text-indigo-650 dark:text-indigo-400 border-indigo-100 dark:border-indigo-900/40"
            }`}
          >
            <Clock className="w-4 h-4" />
            {isTimeCritical ? "SẮP HẾT GIỜ: " : "Thời gian còn lại: "}
            {formatTime(timeRemaining)}
          </div>
        )}
      </div>
    </div>
  );
}
