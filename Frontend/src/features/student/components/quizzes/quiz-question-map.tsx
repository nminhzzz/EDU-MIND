"use client";

import React from "react";
import { StudentQuiz } from "@/features/student/types/quiz";

interface QuizQuestionMapProps {
  quiz: StudentQuiz;
  currentQuestionIndex: number;
  selectedAnswers: Record<number, string>;
  onSelectQuestion: (index: number) => void;
  isReview?: boolean;
}

export function QuizQuestionMap({
  quiz,
  currentQuestionIndex,
  selectedAnswers,
  onSelectQuestion,
  isReview = false,
}: QuizQuestionMapProps) {
  const mcqQuestions = quiz.questions.filter((q) => q.question_type !== "essay");
  const essayQuestions = quiz.questions.filter((q) => q.question_type === "essay");

  return (
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm space-y-6">
      <div>
        <h3 className="font-extrabold text-xs text-zinc-400 uppercase tracking-wider border-b border-zinc-100 dark:border-zinc-800 pb-3 mb-4">
          Bản đồ câu hỏi
        </h3>
        <div className="flex flex-wrap gap-2.5">
          {/* Render MCQs */}
          {mcqQuestions.map((_, idx) => {
            const originalIndex = quiz.questions.findIndex((q) => q === mcqQuestions[idx]);
            const isSelected = selectedAnswers[originalIndex] !== undefined;
            const isCurrent = !isReview && currentQuestionIndex === idx;

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
                {originalIndex + 1}
              </button>
            );
          })}

          {/* Render Essay grouped or individually */}
          {isReview ? (
            essayQuestions.map((_, idx) => {
              const originalIndex = quiz.questions.findIndex((q) => q === essayQuestions[idx]);
              const isCurrent = currentQuestionIndex === originalIndex;

              let btnStyle =
                "border-zinc-200 dark:border-zinc-800 text-zinc-550 dark:text-zinc-400 bg-white dark:bg-zinc-900";
              if (isCurrent) {
                btnStyle =
                  "border-indigo-600 dark:border-indigo-400 text-indigo-600 dark:text-indigo-400 bg-indigo-50/20";
              }

              return (
                <button
                  key={`essay-${idx}`}
                  onClick={() => onSelectQuestion(originalIndex)}
                  className={`w-9 h-9 rounded-xl border flex items-center justify-center font-bold text-xs transition-all cursor-pointer ${btnStyle}`}
                >
                  {originalIndex + 1}
                </button>
              );
            })
          ) : (
            essayQuestions.length > 0 && (
              (() => {
                const isCurrent = currentQuestionIndex === mcqQuestions.length;
                let btnStyle =
                  "border-zinc-200 dark:border-zinc-800 text-zinc-550 dark:text-zinc-400 bg-white dark:bg-zinc-900";
                if (isCurrent) {
                  btnStyle =
                    "border-indigo-600 dark:border-indigo-400 text-indigo-600 dark:text-indigo-400 bg-indigo-50/20";
                }

                return (
                  <button
                    onClick={() => onSelectQuestion(mcqQuestions.length)}
                    className={`px-3.5 h-9 rounded-xl border flex items-center justify-center font-bold text-xs transition-all cursor-pointer ${btnStyle}`}
                  >
                    ✍ Tự luận
                  </button>
                );
              })()
            )
          )}
        </div>
      </div>
    </div>
  );
}
