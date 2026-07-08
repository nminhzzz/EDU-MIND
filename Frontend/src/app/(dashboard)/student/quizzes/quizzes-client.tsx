"use client";

import React from "react";
import { QuizzesListView } from "@/features/student/components/quizzes/quizzes-list-view";
import { useQuizHistory } from "@/features/student/hooks/use-quiz-history";
import type { QuizAttemptHistory, Subject } from "@/features/student/types";

interface QuizzesClientProps {
  initialAttempts: QuizAttemptHistory[];
  initialSubjects: Subject[];
  fetchOnClient?: boolean;
}

export function QuizzesClient({
  initialAttempts,
  initialSubjects,
  fetchOnClient = false,
}: QuizzesClientProps) {
  const {
    attempts,
    subjects,
    showGenerateModal,
    openGenerateModal,
    closeGenerateModal,
  } = useQuizHistory({ initialAttempts, initialSubjects, fetchOnClient });

  return (
    <QuizzesListView
      attempts={attempts}
      subjects={subjects}
      showGenerateModal={showGenerateModal}
      onOpenGenerateModal={openGenerateModal}
      onCloseGenerateModal={closeGenerateModal}
    />
  );
}
