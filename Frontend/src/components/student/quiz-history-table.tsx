"use client";

import React from "react";
import { motion } from "framer-motion";
import { Clock, ChevronRight, Trophy } from "lucide-react";
import Link from "next/link";

interface Attempt {
  attempt_id: number;
  quiz_id: number;
  quiz_title: string;
  score: number;
  correct_count: number;
  wrong_count: number;
  duration_seconds: number;
  submitted_at: string;
}

interface QuizHistoryTableProps {
  attempts: Attempt[];
  onGenerateClick: () => void;
}

export function QuizHistoryTable({ attempts, onGenerateClick }: QuizHistoryTableProps) {
  if (attempts.length === 0) {
    return (
      <div className="py-16 text-center text-zinc-450 dark:text-zinc-550 space-y-3">
        <Trophy className="w-12 h-12 mx-auto opacity-30 text-indigo-400" />
        <p className="text-sm font-semibold text-zinc-650 dark:text-zinc-350">Bạn chưa thực hiện bài luyện tập nào.</p>
        <button
          onClick={onGenerateClick}
          className="px-4 py-2 bg-indigo-55 hover:bg-indigo-100 text-indigo-600 dark:bg-indigo-950/40 dark:hover:bg-indigo-900/60 dark:text-indigo-400 rounded-xl text-xs font-bold transition-all cursor-pointer"
        >
          Sinh đề thi AI đầu tiên
        </button>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-zinc-200 dark:border-zinc-800 text-zinc-400 dark:text-zinc-500 text-xs font-bold uppercase tracking-wider">
            <th className="text-left py-3 px-4">Tên đề thi / Bài tập</th>
            <th className="text-center py-3 px-4">Điểm số</th>
            <th className="text-center py-3 px-4">Kết quả đúng</th>
            <th className="text-center py-3 px-4">Thời gian làm</th>
            <th className="text-right py-3 px-4">Ngày nộp</th>
            <th className="py-3 px-4"></th>
          </tr>
        </thead>
        <tbody>
          {attempts.map((att, idx) => (
            <motion.tr
              key={att.attempt_id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: idx * 0.02 }}
              className="border-b border-zinc-100 dark:border-zinc-800/50 hover:bg-zinc-50 dark:hover:bg-zinc-800/30 transition-colors"
            >
              <td className="py-3.5 px-4 font-semibold text-zinc-800 dark:text-zinc-200 text-left">
                {att.quiz_title}
              </td>
              <td className="py-3.5 px-4 text-center">
                <span className={`inline-block px-2.5 py-1 rounded-lg text-xs font-bold ${
                  att.score >= 8 ? 'text-emerald-600 bg-emerald-50 dark:bg-emerald-950/30 dark:text-emerald-400' :
                  att.score >= 5 ? 'text-amber-600 bg-amber-50 dark:bg-amber-950/30 dark:text-amber-400' :
                  'text-red-650 bg-red-50 dark:bg-red-950/30 dark:text-red-400'
                }`}>
                  {att.score.toFixed(1)} / 10
                </span>
              </td>
              <td className="py-3.5 px-4 text-center text-zinc-500">
                <span className="text-emerald-500 font-bold">{att.correct_count}</span>
                <span className="mx-1">/</span>
                <span className="text-red-400 font-bold">{att.wrong_count}</span>
              </td>
              <td className="py-3.5 px-4 text-center text-zinc-500">
                <span className="inline-flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-zinc-400" />
                  {att.duration_seconds} giây
                </span>
              </td>
              <td className="py-3.5 px-4 text-right text-zinc-450 text-xs">
                {new Date(att.submitted_at).toLocaleString("vi-VN")}
              </td>
              <td className="py-3.5 px-4 text-right">
                <Link
                  href={`/student/quizzes/${att.quiz_id}`}
                  className="text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center justify-end gap-1"
                >
                  Xem giải thích AI
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </td>
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
