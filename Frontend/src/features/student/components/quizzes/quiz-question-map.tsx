"use client";

import React from "react";
import { Check, X } from "lucide-react";
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
        <div className="flex flex-wrap gap-3 pt-1">
          {/* Render MCQs */}
          {mcqQuestions.map((_, idx) => {
            const originalIndex = quiz.questions.findIndex((q) => q === mcqQuestions[idx]);
            const isSelected = selectedAnswers[originalIndex] !== undefined;
            const isCurrent = isReview
              ? currentQuestionIndex === originalIndex
              : currentQuestionIndex === idx;

            const attemptAns = isReview
              ? quiz.latest_attempt?.answers?.find((a: any) => a.question_index === originalIndex)
              : undefined;

            const isCorrect = attemptAns?.is_correct === true;
            const isWrong = attemptAns && attemptAns.is_correct === false;

            let btnStyle =
              "border-zinc-200 dark:border-zinc-800 text-zinc-550 dark:text-zinc-400 bg-white dark:bg-zinc-900";

            if (isReview) {
              if (isCorrect) {
                btnStyle =
                  "border-emerald-500/60 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 font-extrabold";
              } else if (isWrong) {
                btnStyle =
                  "border-rose-500/60 bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 font-extrabold";
              }
            } else if (isCurrent) {
              btnStyle =
                "border-indigo-600 dark:border-indigo-400 text-indigo-600 dark:text-indigo-400 bg-indigo-50/20";
            } else if (isSelected) {
              btnStyle =
                "border-zinc-400 dark:border-zinc-600 text-zinc-800 dark:text-zinc-100 bg-zinc-50 dark:bg-zinc-800";
            }

            const currentRing = isReview && isCurrent ? "ring-2 ring-indigo-500 ring-offset-1 dark:ring-offset-zinc-900" : "";

            return (
              <button
                key={idx}
                onClick={() => onSelectQuestion(isReview ? originalIndex : idx)}
                className={`relative w-9 h-9 rounded-xl border flex items-center justify-center font-bold text-xs transition-all cursor-pointer ${btnStyle} ${currentRing}`}
              >
                {originalIndex + 1}
                {isReview && isCorrect && (
                  <span className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-emerald-500 text-white flex items-center justify-center shadow-sm ring-2 ring-white dark:ring-zinc-900">
                    <Check className="w-2.5 h-2.5 stroke-[3]" />
                  </span>
                )}
                {isReview && isWrong && (
                  <span className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-rose-500 text-white flex items-center justify-center shadow-sm ring-2 ring-white dark:ring-zinc-900">
                    <X className="w-2.5 h-2.5 stroke-[3]" />
                  </span>
                )}
              </button>
            );
          })}

          {/* Render Essay */}
          {isReview ? (
            essayQuestions.map((_, idx) => {
              const originalIndex = quiz.questions.findIndex((q) => q === essayQuestions[idx]);
              const isCurrent = currentQuestionIndex === originalIndex;

              const attemptAns = quiz.latest_attempt?.answers?.find(
                (a: any) => a.question_index === originalIndex,
              );
              const isCorrect = attemptAns?.is_correct === true;
              const isWrong = attemptAns && attemptAns.is_correct === false;

              let btnStyle =
                "border-zinc-200 dark:border-zinc-800 text-zinc-550 dark:text-zinc-400 bg-white dark:bg-zinc-900";
              if (isCorrect) {
                btnStyle =
                  "border-emerald-500/60 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 font-extrabold";
              } else if (isWrong) {
                btnStyle =
                  "border-rose-500/60 bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 font-extrabold";
              }

              const currentRing = isCurrent ? "ring-2 ring-indigo-500 ring-offset-1 dark:ring-offset-zinc-900" : "";

              return (
                <button
                  key={`essay-${idx}`}
                  onClick={() => onSelectQuestion(originalIndex)}
                  className={`relative w-9 h-9 rounded-xl border flex items-center justify-center font-bold text-xs transition-all cursor-pointer ${btnStyle} ${currentRing}`}
                >
                  {originalIndex + 1}
                  {isCorrect && (
                    <span className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-emerald-500 text-white flex items-center justify-center shadow-sm ring-2 ring-white dark:ring-zinc-900">
                      <Check className="w-2.5 h-2.5 stroke-[3]" />
                    </span>
                  )}
                  {isWrong && (
                    <span className="absolute -top-1.5 -right-1.5 w-4 h-4 rounded-full bg-rose-500 text-white flex items-center justify-center shadow-sm ring-2 ring-white dark:ring-zinc-900">
                      <X className="w-2.5 h-2.5 stroke-[3]" />
                    </span>
                  )}
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
