"use client";

import React from "react";
import { Clock, Trophy } from "lucide-react";
import { StudentQuiz } from "@/features/student/types/quiz";

interface QuizDetailHeaderProps {
  quiz: StudentQuiz;
  isReview: boolean;
  duration: number;
}

export function QuizDetailHeader({ quiz, isReview, duration }: QuizDetailHeaderProps) {
  return (
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <span className="text-[10px] font-bold text-indigo-650 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 px-2.5 py-1 rounded-lg uppercase tracking-wide">
          Độ khó: {quiz.difficulty}
        </span>
        <h1 className="text-xl font-black text-zinc-900 dark:text-white mt-2">{quiz.title}</h1>
      </div>

      {isReview ? (
        <div className="flex items-center gap-2 text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40 px-4 py-2 rounded-xl text-xs font-bold">
          <Trophy className="w-4 h-4" />
          Đã hoàn thành luyện tập
        </div>
      ) : (
        <div className="flex items-center gap-2 text-indigo-650 bg-indigo-50 dark:bg-indigo-950/40 px-4 py-2 rounded-xl text-xs font-bold">
          <Clock className="w-4 h-4" />
          Thời gian: {Math.floor(duration / 60)}p {duration % 60}s
        </div>
      )}
    </div>
  );
}
