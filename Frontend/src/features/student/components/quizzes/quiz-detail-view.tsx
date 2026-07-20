"use client";

import React from "react";
import { StudentQuiz } from "@/features/student/types/quiz";
import { QuizDetailHeader } from "./quiz-detail-header";
import { QuizQuestionMap } from "./quiz-question-map";
import { QuizQuestionPanel } from "./quiz-question-panel";

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
  const mcqQuestions = quiz.questions.filter((q) => q.question_type !== "essay");
  const currentQuestion = isReview
    ? quiz.questions[currentQuestionIndex]
    : (currentQuestionIndex < mcqQuestions.length ? mcqQuestions[currentQuestionIndex] : null);

  return (
    <div className="space-y-6 text-left max-w-4xl mx-auto">
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
  );
}
