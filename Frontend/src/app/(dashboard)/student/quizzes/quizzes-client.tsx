"use client";

import React from "react";
import { QuizzesListView } from "@/features/student/components/quizzes/quizzes-list-view";
import { useQuizHistory } from "@/features/student/hooks/use-quiz-history";
import type { QuizAttemptHistory, StudentQuiz } from "@/features/student/types";

interface QuizzesClientProps {
  initialAttempts: QuizAttemptHistory[];
  initialAssigned: StudentQuiz[];
  fetchOnClient?: boolean;
}

export function QuizzesClient({
  initialAttempts,
  initialAssigned,
  fetchOnClient = false,
}: QuizzesClientProps) {
  const { attempts, assignedQuizzes, loading } = useQuizHistory({
    initialAttempts,
    initialAssigned,
    fetchOnClient,
  });

  return (
    <QuizzesListView
      attempts={attempts}
      assignedQuizzes={assignedQuizzes}
      loading={loading}
    />
  );
}
