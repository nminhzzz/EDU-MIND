"use client";

import React from "react";
import { ChevronLeft, ChevronRight, RotateCcw, Send } from "lucide-react";
import { StudentQuiz, StudentQuizQuestion } from "@/features/student/types/quiz";

function getOptionStyle(
  isReview: boolean,
  isSelected: boolean,
  isCorrect: boolean,
): string {
  if (!isReview && isSelected) {
    return "border-indigo-600 dark:border-indigo-500 bg-indigo-50/20 dark:bg-indigo-950/20 text-indigo-600 dark:text-indigo-400";
  }
  if (isReview) {
    if (isCorrect) {
      return "border-emerald-600 dark:border-emerald-500 bg-emerald-50/10 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-400";
    }
    if (isSelected && !isCorrect) {
      return "border-red-650 dark:border-red-500 bg-red-50/10 dark:bg-red-950/20 text-red-650 dark:text-red-400";
    }
  }
  return "border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 hover:border-zinc-350 dark:hover:border-zinc-700";
}

interface QuizQuestionPanelProps {
  quiz: StudentQuiz;
  question: StudentQuizQuestion;
  questionIndex: number;
  isReview: boolean;
  selectedAnswers: Record<number, string>;
  submitting: boolean;
  onSelectOption: (questionIndex: number, optionKey: string) => void;
  onPrevious: () => void;
  onNext: () => void;
  onSubmit: () => void;
  onBackToList: () => void;
}

export function QuizQuestionPanel({
  quiz,
  question,
  questionIndex,
  isReview,
  selectedAnswers,
  submitting,
  onSelectOption,
  onPrevious,
  onNext,
  onSubmit,
  onBackToList,
}: QuizQuestionPanelProps) {
  return (
    <div className="lg:col-span-2 bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm flex flex-col justify-between min-h-[400px]">
      <div>
        <div className="flex items-center justify-between pb-3 border-b border-zinc-100 dark:border-zinc-800 mb-6">
          <span className="text-xs font-bold text-zinc-400">
            Câu hỏi {questionIndex + 1} / {quiz.total_questions}
          </span>
        </div>

        <h3 className="text-base font-extrabold text-zinc-850 dark:text-zinc-100 leading-relaxed mb-6">
          {question.question_text}
        </h3>

        <div className="space-y-3">
          {question.options.map((opt) => {
            const isSelected = selectedAnswers[questionIndex] === opt.key;
            const isCorrect = question.correct_answer === opt.key;
            const optionStyle = getOptionStyle(isReview, isSelected, isCorrect);

            return (
              <button
                key={opt.key}
                onClick={() => onSelectOption(questionIndex, opt.key)}
                disabled={isReview}
                className={`w-full flex items-start gap-4 p-4 border rounded-xl text-left transition-all ${optionStyle}`}
              >
                <span className="font-extrabold text-sm">{opt.key}.</span>
                <span className="text-sm font-semibold">{opt.value}</span>
              </button>
            );
          })}
        </div>

        {isReview && question.explanation && (
          <div className="mt-8 p-5 bg-indigo-50/30 dark:bg-zinc-950/30 border border-indigo-100/50 dark:border-zinc-800 rounded-xl space-y-2">
            <h4 className="text-xs font-bold text-indigo-650 dark:text-indigo-400 uppercase tracking-wider">
              Giải thích đáp án AI
            </h4>
            <p className="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed font-medium">
              {question.explanation}
            </p>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between pt-6 border-t border-zinc-100 dark:border-zinc-800 mt-8">
        <button
          onClick={onPrevious}
          disabled={questionIndex === 0}
          className="px-4 py-2 border border-zinc-200 dark:border-zinc-700 disabled:opacity-30 rounded-xl text-xs font-bold flex items-center gap-1 cursor-pointer"
        >
          <ChevronLeft className="w-4 h-4" />
          Câu trước
        </button>

        {questionIndex < quiz.total_questions - 1 ? (
          <button
            onClick={onNext}
            className="px-4 py-2 bg-zinc-800 dark:bg-zinc-700 text-white rounded-xl text-xs font-bold flex items-center gap-1 cursor-pointer"
          >
            Câu sau
            <ChevronRight className="w-4 h-4" />
          </button>
        ) : !isReview ? (
          <button
            onClick={onSubmit}
            disabled={submitting}
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 cursor-pointer shadow-md shadow-indigo-500/10"
          >
            <Send className="w-3.5 h-3.5" />
            Nộp bài thi
          </button>
        ) : (
          <button
            onClick={onBackToList}
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Quay lại kho
          </button>
        )}
      </div>
    </div>
  );
}
