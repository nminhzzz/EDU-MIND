"use client";

import React from "react";
import { BrainCircuit, Trophy } from "lucide-react";
import type { QuizAttemptHistory, Subject } from "@/features/student/types";
import { GenerateQuizModal } from "./generate-quiz-modal";
import { QuizHistoryTable } from "./quiz-history-table";

interface QuizzesListViewProps {
  attempts: QuizAttemptHistory[];
  subjects: Subject[];
  showGenerateModal: boolean;
  onOpenGenerateModal: () => void;
  onCloseGenerateModal: () => void;
}

export function QuizzesListView({
  attempts,
  subjects,
  showGenerateModal,
  onOpenGenerateModal,
  onCloseGenerateModal,
}: QuizzesListViewProps) {
  return (
    <div className="space-y-6 text-left">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-zinc-900 dark:text-white">
            Luyện Đề Thi & Bài Tập
          </h1>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
            Tự ôn tập củng cố kiến thức bằng các đề trắc nghiệm tạo tự động từ AI RAG.
          </p>
        </div>
        <button
          onClick={onOpenGenerateModal}
          className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm rounded-xl shadow-md transition-all active:scale-[0.98] cursor-pointer flex items-center gap-2"
        >
          <BrainCircuit className="w-4 h-4" />
          Sinh đề thi bằng AI
        </button>
      </div>

      <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm space-y-4">
        <h2 className="font-extrabold text-sm text-zinc-855 dark:text-zinc-250 flex items-center gap-2 border-b border-zinc-100 dark:border-zinc-800 pb-3">
          <Trophy className="w-4 h-4 text-amber-500" />
          Lịch sử bài thi đã làm
        </h2>

        <QuizHistoryTable attempts={attempts} onGenerateClick={onOpenGenerateModal} />
      </div>

      <GenerateQuizModal
        isOpen={showGenerateModal}
        onClose={onCloseGenerateModal}
        subjects={subjects}
      />
    </div>
  );
}
