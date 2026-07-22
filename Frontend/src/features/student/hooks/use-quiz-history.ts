"use client";

import { useEffect, useState } from "react";
import { quizService } from "@/features/student/services/quiz";
import type { QuizAttemptHistory, StudentQuiz } from "@/features/student/types";

interface UseQuizHistoryOptions {
  initialAttempts: QuizAttemptHistory[];
  initialAssigned: StudentQuiz[];
  fetchOnClient?: boolean;
}

export function useQuizHistory({
  initialAttempts,
  initialAssigned,
  fetchOnClient = false,
}: UseQuizHistoryOptions) {
  const [attempts, setAttempts] = useState<QuizAttemptHistory[]>(initialAttempts);
  const [assignedQuizzes, setAssignedQuizzes] = useState<StudentQuiz[]>(initialAssigned);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!fetchOnClient) return;

    const loadData = async () => {
      setLoading(true);
      try {
        const [historyRes, assignedRes] = await Promise.all([
          quizService.getHistory().catch(() => ({ data: [] })),
          quizService.getAssigned().catch(() => ({ data: [] })),
        ]);
        setAttempts(historyRes?.data || []);
        setAssignedQuizzes(assignedRes?.data || []);
      } catch (err) {
        console.error("Lỗi tải dữ liệu bài kiểm tra phía client:", err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [fetchOnClient]);

  return {
    attempts,
    assignedQuizzes,
    loading,
  };
}
