import React from "react";
import { serverFetch, needsClientFallback, unwrapServerData } from "@/lib/server-api";
import type { QuizAttemptHistory, Subject } from "@/features/student/types";
import { QuizzesClient } from "./quizzes-client";

export default async function StudentQuizzesPage() {
  const [historyResult, subjectsResult] = await Promise.all([
    serverFetch<QuizAttemptHistory[]>("/quizzes/student/history"),
    serverFetch<Subject[]>("/subjects/"),
  ]);

  const attempts = unwrapServerData(historyResult, []);
  const subjects = unwrapServerData(subjectsResult, []);
  const fetchOnClient = needsClientFallback([historyResult, subjectsResult]);

  return (
    <QuizzesClient
      initialAttempts={attempts}
      initialSubjects={subjects}
      fetchOnClient={fetchOnClient}
    />
  );
}
