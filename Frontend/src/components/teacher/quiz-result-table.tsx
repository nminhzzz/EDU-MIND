"use client";
import React from "react";
import { motion } from "framer-motion";
import { Trophy, Clock } from "lucide-react";

interface QuizAttempt {
  attempt_id: number;
  quiz_id: number;
  quiz_title: string;
  student_id: number;
  student_name: string;
  student_email: string;
  score: number;
  correct_count: number;
  wrong_count: number;
  duration_seconds: number;
  submitted_at: string;
}

interface QuizResultTableProps {
  attempts: QuizAttempt[];
}

export function QuizResultTable({ attempts }: QuizResultTableProps) {
  if (attempts.length === 0) {
    return (
      <div className="text-center py-12 text-zinc-400 dark:text-zinc-500">
        <Trophy className="w-10 h-10 mx-auto mb-3 opacity-40" />
        <p className="text-sm font-medium">Chưa có học sinh nào nộp bài.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-zinc-200 dark:border-zinc-800">
            <th className="text-left py-3 px-4 text-xs font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">Học sinh</th>
            <th className="text-left py-3 px-4 text-xs font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">Đề thi</th>
            <th className="text-center py-3 px-4 text-xs font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">Điểm</th>
            <th className="text-center py-3 px-4 text-xs font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">Đúng/Sai</th>
            <th className="text-center py-3 px-4 text-xs font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">Thời gian</th>
            <th className="text-right py-3 px-4 text-xs font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">Ngày nộp</th>
          </tr>
        </thead>
        <tbody>
          {attempts.map((att, idx) => (
            <motion.tr
              key={att.attempt_id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: idx * 0.03 }}
              className="border-b border-zinc-100 dark:border-zinc-800/50 hover:bg-zinc-50 dark:hover:bg-zinc-800/30 transition-colors"
            >
              <td className="py-3 px-4">
                <div>
                  <p className="font-semibold text-zinc-800 dark:text-zinc-200">{att.student_name}</p>
                  <p className="text-xs text-zinc-400">{att.student_email}</p>
                </div>
              </td>
              <td className="py-3 px-4 text-zinc-600 dark:text-zinc-400 max-w-[200px] truncate">{att.quiz_title}</td>
              <td className="py-3 px-4 text-center">
                <span className={`inline-block px-2.5 py-1 rounded-lg text-xs font-bold ${
                  att.score >= 8 ? 'text-emerald-600 bg-emerald-50 dark:bg-emerald-950/30 dark:text-emerald-400' :
                  att.score >= 5 ? 'text-amber-600 bg-amber-50 dark:bg-amber-950/30 dark:text-amber-400' :
                  'text-red-600 bg-red-50 dark:bg-red-950/30 dark:text-red-400'
                }`}>
                  {att.score.toFixed(1)}
                </span>
              </td>
              <td className="py-3 px-4 text-center text-zinc-600 dark:text-zinc-400">
                <span className="text-emerald-500">{att.correct_count}</span>
                <span className="text-zinc-300 dark:text-zinc-600 mx-1">/</span>
                <span className="text-red-400">{att.wrong_count}</span>
              </td>
              <td className="py-3 px-4 text-center text-zinc-500 dark:text-zinc-400">
                <span className="inline-flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  {att.duration_seconds ? `${Math.floor(att.duration_seconds / 60)}p${att.duration_seconds % 60}s` : '—'}
                </span>
              </td>
              <td className="py-3 px-4 text-right text-zinc-500 dark:text-zinc-400 text-xs">
                {new Date(att.submitted_at).toLocaleString("vi-VN")}
              </td>
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
