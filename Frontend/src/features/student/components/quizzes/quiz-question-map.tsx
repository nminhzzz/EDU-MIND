"use client";

import React from "react";
import { StudentQuiz } from "@/features/student/types/quiz";

interface QuizQuestionMapProps {
  quiz: StudentQuiz;
  currentQuestionIndex: number;
  selectedAnswers: Record<number, string>;
  onSelectQuestion: (index: number) => void;
}

export function QuizQuestionMap({
  quiz,
  currentQuestionIndex,
  selectedAnswers,
  onSelectQuestion,
}: QuizQuestionMapProps) {
  return (
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm space-y-6">
      <div>
        <h3 className="font-extrabold text-xs text-zinc-400 uppercase tracking-wider border-b border-zinc-100 dark:border-zinc-800 pb-3 mb-4">
          Bản đồ câu hỏi
        </h3>
        <div className="flex flex-wrap gap-2.5">
          {quiz.questions.map((_, idx) => {
            const isSelected = selectedAnswers[idx] !== undefined;
            const isCurrent = currentQuestionIndex === idx;

            let btnStyle =
              "border-zinc-200 dark:border-zinc-800 text-zinc-550 dark:text-zinc-400 bg-white dark:bg-zinc-900";
            if (isCurrent) {
              btnStyle =
                "border-indigo-600 dark:border-indigo-400 text-indigo-600 dark:text-indigo-400 bg-indigo-50/20";
            } else if (isSelected) {
              btnStyle =
                "border-zinc-400 dark:border-zinc-600 text-zinc-800 dark:text-zinc-100 bg-zinc-50 dark:bg-zinc-800";
            }

            return (
              <button
                key={idx}
                onClick={() => onSelectQuestion(idx)}
                className={`w-9 h-9 rounded-xl border flex items-center justify-center font-bold text-xs transition-all cursor-pointer ${btnStyle}`}
              >
                {idx + 1}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
