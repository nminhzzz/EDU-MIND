"use client";

import React from "react";
import { useParams } from "next/navigation";
import { QuizDetailView } from "@/features/student/components/quizzes/quiz-detail-view";
import { QuizLoadingState } from "@/features/student/components/quizzes/quiz-loading-state";
import { useQuizAttempt } from "@/features/student/hooks/use-quiz-attempt";

export default function StudentQuizDetailPage() {
  const params = useParams();
  const quizId = params.id as string | undefined;

  const {
    quiz,
    loading,
    isReview,
    currentQuestionIndex,
    selectedAnswers,
    duration,
    submitting,
    handleSelectOption,
    handleSubmit,
    goToPreviousQuestion,
    goToNextQuestion,
    goToQuestion,
    goBackToList,
    essayFilePath,
    uploadingEssay,
    handleUploadEssay,
  } = useQuizAttempt(quizId);

  if (loading) {
    return <QuizLoadingState />;
  }

  if (!quiz) return null;

  return (
    <QuizDetailView
      quiz={quiz}
      isReview={isReview}
      duration={duration}
      currentQuestionIndex={currentQuestionIndex}
      selectedAnswers={selectedAnswers}
      submitting={submitting}
      onSelectOption={handleSelectOption}
      onPrevious={goToPreviousQuestion}
      onNext={goToNextQuestion}
      onSubmit={handleSubmit}
      onBackToList={goBackToList}
      onSelectQuestion={goToQuestion}
      essayFilePath={essayFilePath}
      uploadingEssay={uploadingEssay}
      handleUploadEssay={handleUploadEssay}
    />
  );
}
