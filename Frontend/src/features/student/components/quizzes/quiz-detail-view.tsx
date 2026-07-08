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
  currentQuestionIndex: number;
  selectedAnswers: Record<number, string>;
  submitting: boolean;
  onSelectOption: (questionIndex: number, optionKey: string) => void;
  onPrevious: () => void;
  onNext: () => void;
  onSubmit: () => void;
  onBackToList: () => void;
  onSelectQuestion: (index: number) => void;
}

export function QuizDetailView({
  quiz,
  isReview,
  duration,
  currentQuestionIndex,
  selectedAnswers,
  submitting,
  onSelectOption,
  onPrevious,
  onNext,
  onSubmit,
  onBackToList,
  onSelectQuestion,
}: QuizDetailViewProps) {
  const currentQuestion = quiz.questions[currentQuestionIndex];

  return (
    <div className="space-y-6 text-left max-w-4xl mx-auto">
      <QuizDetailHeader quiz={quiz} isReview={isReview} duration={duration} />

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
        />

        <QuizQuestionMap
          quiz={quiz}
          currentQuestionIndex={currentQuestionIndex}
          selectedAnswers={selectedAnswers}
          onSelectQuestion={onSelectQuestion}
        />
      </div>
    </div>
  );
}
