"use client";

import React, { useState } from "react";
import { StudentQuiz } from "@/features/student/types/quiz";
import { QuizDetailHeader } from "./quiz-detail-header";
import { QuizQuestionMap } from "./quiz-question-map";
import { QuizQuestionPanel } from "./quiz-question-panel";
import { AIQuizFeedbackCard } from "./ai-quiz-feedback-card";
import { FileText, Sparkles } from "lucide-react";

interface QuizDetailViewProps {
  quiz: StudentQuiz;
  isReview: boolean;
  duration: number;
  timeRemaining: number;
  timeLimit: number;
  tabViolations: number;
  currentQuestionIndex: number;
  selectedAnswers: Record<number, string>;
  submitting: boolean;
  onSelectOption: (questionIndex: number, optionKey: string) => void;
  onPrevious: () => void;
  onNext: () => void;
  onSubmit: () => void;
  onBackToList: () => void;
  onSelectQuestion: (index: number) => void;
  essayFilePath?: string | null;
  uploadingEssay?: boolean;
  handleUploadEssay?: (file: File) => void;
}

export function QuizDetailView({
  quiz,
  isReview,
  duration,
  timeRemaining,
  timeLimit,
  tabViolations,
  currentQuestionIndex,
  selectedAnswers,
  submitting,
  onSelectOption,
  onPrevious,
  onNext,
  onSubmit,
  onBackToList,
  onSelectQuestion,
  essayFilePath,
  uploadingEssay,
  handleUploadEssay,
}: QuizDetailViewProps) {
  const [activeTab, setActiveTab] = useState<"review" | "ai_feedback">("review");

  const mcqQuestions = quiz.questions.filter((q) => q.question_type !== "essay");
  const currentQuestion = isReview
    ? quiz.questions[currentQuestionIndex]
    : (currentQuestionIndex < mcqQuestions.length ? mcqQuestions[currentQuestionIndex] : null);

  return (
    <div className="space-y-6 text-left max-w-4xl mx-auto">
      {/* Tab Switcher for Review Mode */}
      {isReview && (
        <div className="flex items-center gap-2 p-1.5 bg-sky-50/70 dark:bg-sky-950/40 border border-sky-200/80 dark:border-sky-900/50 rounded-md shadow-xs">
          <button
            type="button"
            onClick={() => setActiveTab("review")}
            className={`flex-1 py-3 px-4 text-xs font-extrabold rounded-md transition-all flex items-center justify-center gap-2 cursor-pointer ${
              activeTab === "review"
                ? "bg-white dark:bg-sky-900 text-sky-950 dark:text-white shadow-xs border border-sky-200 dark:border-sky-800"
                : "text-sky-700 dark:text-sky-300 hover:bg-white/60 dark:hover:bg-sky-900/40"
            }`}
          >
            <FileText className="w-4 h-4 text-sky-600 dark:text-sky-400" />
            Xem lại bài kiểm tra đã làm
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("ai_feedback")}
            className={`flex-1 py-3 px-4 text-xs font-extrabold rounded-md transition-all flex items-center justify-center gap-2 cursor-pointer ${
              activeTab === "ai_feedback"
                ? "bg-white dark:bg-sky-900 text-sky-950 dark:text-white shadow-xs border border-sky-200 dark:border-sky-800"
                : "text-sky-700 dark:text-sky-300 hover:bg-white/60 dark:hover:bg-sky-900/40"
            }`}
          >
            <Sparkles className="w-4 h-4 text-sky-500 animate-pulse" />
            Đánh giá & Lời phê từ AI
            {quiz.latest_attempt?.score !== undefined && (
              <span className="ml-1 px-2 py-0.5 text-[10px] font-mono font-black bg-sky-100 dark:bg-sky-900 text-sky-700 dark:text-sky-300 rounded-md border border-sky-200 dark:border-sky-800">
                {quiz.latest_attempt.score.toFixed(1)}/10
              </span>
            )}
          </button>
        </div>
      )}

      {/* Tab 1: Quiz Review Mode (Header + Question Panel + Question Map) */}
      {(!isReview || activeTab === "review") && (
        <div className="space-y-6">
          <QuizDetailHeader
            quiz={quiz}
            isReview={isReview}
            duration={duration}
            timeRemaining={timeRemaining}
            timeLimit={timeLimit}
            tabViolations={tabViolations}
          />

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <QuizQuestionPanel
              quiz={quiz}
              question={currentQuestion}
              questionIndex={currentQuestionIndex}
              isReview={isReview}
              selectedAnswers={selectedAnswers}
              submitting={submitting}
              onSelectOption={onSelectOption}
              onPrevious={onPrevious}
              onNext={onNext}
              onSubmit={onSubmit}
              onBackToList={onBackToList}
              essayFilePath={essayFilePath}
              uploadingEssay={uploadingEssay}
              handleUploadEssay={handleUploadEssay}
            />

            <QuizQuestionMap
              quiz={quiz}
              currentQuestionIndex={currentQuestionIndex}
              selectedAnswers={selectedAnswers}
              onSelectQuestion={onSelectQuestion}
              isReview={isReview}
            />
          </div>
        </div>
      )}

      {/* Tab 2: AI Feedback & Assessment */}
      {isReview && activeTab === "ai_feedback" && quiz.latest_attempt && (
        <div className="space-y-6">
          <AIQuizFeedbackCard
            assessment={quiz.latest_attempt.ai_assessment}
            score={quiz.latest_attempt.score ?? 0}
            correctCount={quiz.latest_attempt.correct_count ?? 0}
            totalQuestions={quiz.questions.length}
            submittedAt={quiz.latest_attempt.submitted_at}
          />
        </div>
      )}
    </div>
  );
}
