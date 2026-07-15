"use client";

import React from "react";
import { motion } from "framer-motion";
import { Clock, ChevronRight, Trophy } from "lucide-react";
import Link from "next/link";
import { ROUTES } from "@/constants/routes";
import type { QuizAttemptHistory } from "@/features/student/types";

interface QuizHistoryTableProps {
  attempts: QuizAttemptHistory[];
}

export function QuizHistoryTable({ attempts }: QuizHistoryTableProps) {
  if (attempts.length === 0) {
    return (
      <div className="py-16 text-center text-zinc-450 dark:text-zinc-550 space-y-3">
        <Trophy className="w-12 h-12 mx-auto opacity-30 text-indigo-400" />
        <p className="text-sm font-semibold text-zinc-600 dark:text-zinc-400">
          Bạn chưa hoàn thành bài tập nào. Hãy làm các bài tập được giao ở phía trên!
        </p>
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
                <span
                  className={`inline-block px-2.5 py-1 rounded-lg text-xs font-bold ${
                    att.score >= 8
                      ? "text-emerald-600 bg-emerald-50 dark:bg-emerald-950/30 dark:text-emerald-400"
                      : att.score >= 5
                        ? "text-amber-600 bg-amber-50 dark:bg-amber-950/30 dark:text-amber-400"
                        : "text-red-650 bg-red-50 dark:bg-red-950/30 dark:text-red-400"
                  }`}
                >
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
                  href={ROUTES.STUDENT_QUIZ(att.quiz_id)}
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
