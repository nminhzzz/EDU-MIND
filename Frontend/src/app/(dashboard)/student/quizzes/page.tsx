import React from "react";
import { serverFetch, needsClientFallback, unwrapServerData } from "@/lib/server-api";
import type { QuizAttemptHistory, StudentQuiz } from "@/features/student/types";
import { QuizzesClient } from "./quizzes-client";

export default async function StudentQuizzesPage() {
  const [historyResult, assignedResult] = await Promise.all([
    serverFetch<QuizAttemptHistory[]>("/quizzes/student/history"),
    serverFetch<StudentQuiz[]>("/quizzes/student/assigned"),
  ]);

  const attempts = unwrapServerData(historyResult, []);
  const assignedQuizzes = unwrapServerData(assignedResult, []);
  const fetchOnClient = needsClientFallback([historyResult, assignedResult]);

  return (
    <QuizzesClient
      initialAttempts={attempts}
      initialAssigned={assignedQuizzes}
      fetchOnClient={fetchOnClient}
    />
  );
}
