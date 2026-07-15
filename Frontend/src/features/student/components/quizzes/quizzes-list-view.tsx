"use client";

import React from "react";
import { ClipboardList, Trophy } from "lucide-react";
import type { QuizAttemptHistory, StudentQuiz } from "@/features/student/types";
import { QuizHistoryTable } from "./quiz-history-table";
import Link from "next/link";

interface QuizzesListViewProps {
  attempts: QuizAttemptHistory[];
  assignedQuizzes: StudentQuiz[];
  loading?: boolean;
}

export function QuizzesListView({
  attempts,
  assignedQuizzes,
  loading = false,
}: QuizzesListViewProps) {
  // Helper to check if student already attempted the quiz and get the score
  const getQuizResult = (quizId: number) => {
    const attempt = attempts.find((a) => a.quiz_id === quizId);
    return attempt ? { completed: true, score: attempt.score } : { completed: false, score: null };
  };

  return (
    <div className="space-y-6 text-left">
      <div>
        <h1 className="text-2xl font-black text-zinc-900 dark:text-white">
          Nhiệm Vụ & Bài Tập
        </h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
          Hoàn thành các bài tập và đề kiểm tra trắc nghiệm do Giáo viên giao cho lớp của bạn.
        </p>
      </div>

      {/* 1. Assigned Quizzes List */}
      <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm space-y-4">
        <h2 className="font-extrabold text-sm text-zinc-850 dark:text-zinc-200 flex items-center gap-2 border-b border-zinc-100 dark:border-zinc-800 pb-3">
          <ClipboardList className="w-4 h-4 text-indigo-500" />
          Bài tập được giao từ lớp học
        </h2>

        {loading ? (
          <div className="py-8 text-center text-zinc-400 font-bold text-sm">
            Đang tải danh sách bài tập...
          </div>
        ) : assignedQuizzes.length === 0 ? (
          <div className="py-8 text-center text-zinc-400 font-semibold text-sm">
            Hiện tại bạn chưa được giao bài tập nào. Hãy tận hưởng thời gian nghỉ ngơi!
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {assignedQuizzes.map((quiz) => {
              const result = getQuizResult(quiz.id);
              return (
                <div
                  key={quiz.id}
                  className="flex flex-col justify-between p-5 border border-zinc-150 dark:border-zinc-800 rounded-xl bg-zinc-50/50 dark:bg-zinc-950/30 hover:border-zinc-200 dark:hover:border-zinc-700 transition-all"
                >
                  <div className="space-y-2">
                    <div className="flex justify-between items-start gap-2">
                      <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-indigo-50 text-indigo-600 dark:bg-indigo-950/40 dark:text-indigo-400">
                        {quiz.difficulty === "easy" ? "Dễ" : quiz.difficulty === "hard" ? "Khó" : "Trung bình"}
                      </span>
                      {result.completed ? (
                        <span className="px-2.5 py-0.5 rounded-full text-[11px] font-extrabold bg-green-50 text-green-700 dark:bg-green-950/40 dark:text-green-400 border border-green-200/50 dark:border-green-800/30">
                          Điểm: {result.score} / 10
                        </span>
                      ) : (
                        <span className="px-2.5 py-0.5 rounded-full text-[11px] font-extrabold bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:amber-400 border border-amber-200/50 dark:border-amber-800/30">
                          Chưa hoàn thành
                        </span>
                      )}
                    </div>
                    <h3 className="font-extrabold text-sm text-zinc-900 dark:text-white line-clamp-1">
                      {quiz.title}
                    </h3>
                    <p className="text-[12px] text-zinc-500 dark:text-zinc-400">
                      Số câu hỏi: <strong className="text-zinc-700 dark:text-zinc-200">{quiz.total_questions}</strong> câu
                    </p>
                    {quiz.deadline && (
                      <p className="text-[11px] text-zinc-400 dark:text-zinc-500">
                        Hạn chót: {new Date(quiz.deadline).toLocaleDateString("vi-VN", {
                          hour: "2-digit",
                          minute: "2-digit",
                          day: "2-digit",
                          month: "2-digit",
                        })}
                      </p>
                    )}
                  </div>

                  <div className="mt-4 pt-3 border-t border-zinc-100/50 dark:border-zinc-800/50 flex justify-end">
                    {result.completed ? (
                      <Link
                        href={`/student/quizzes/${quiz.id}`}
                        className="px-4 py-1.5 border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-700 dark:text-zinc-300 font-bold text-xs rounded-lg transition-all"
                      >
                        Xem lại bài
                      </Link>
                    ) : (
                      <Link
                        href={`/student/quizzes/${quiz.id}`}
                        className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-lg transition-all"
                      >
                        Bắt đầu làm bài
                      </Link>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 2. Attempts History */}
      <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm space-y-4">
        <h2 className="font-extrabold text-sm text-zinc-850 dark:text-zinc-200 flex items-center gap-2 border-b border-zinc-100 dark:border-zinc-800 pb-3">
          <Trophy className="w-4 h-4 text-amber-500" />
          Lịch sử điểm số bài thi
        </h2>

        <QuizHistoryTable attempts={attempts} />
      </div>
    </div>
  );
}
