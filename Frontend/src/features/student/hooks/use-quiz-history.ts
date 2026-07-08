"use client";

import { useCallback, useEffect, useState } from "react";
import { quizService } from "@/features/student/services/quiz";
import { useSubjects } from "@/features/student/hooks/use-subjects";
import type { QuizAttemptHistory, Subject } from "@/features/student/types";

interface UseQuizHistoryOptions {
  initialAttempts: QuizAttemptHistory[];
  initialSubjects: Subject[];
  fetchOnClient?: boolean;
}

export function useQuizHistory({
  initialAttempts,
  initialSubjects,
  fetchOnClient = false,
}: UseQuizHistoryOptions) {
  const { subjects, fetchSubjects } = useSubjects({ initialSubjects });
  const [attempts, setAttempts] = useState<QuizAttemptHistory[]>(initialAttempts);
  const [showGenerateModal, setShowGenerateModal] = useState(false);

  useEffect(() => {
    if (!fetchOnClient) return;

    const loadData = async () => {
      try {
        const [, historyRes] = await Promise.all([
          fetchSubjects(),
          quizService.getHistory(),
        ]);
        setAttempts(historyRes.data);
      } catch (err) {
        console.error("Lỗi tải dữ liệu luyện đề phía client:", err);
      }
    };

    loadData();
  }, [fetchOnClient, fetchSubjects]);

  const openGenerateModal = useCallback(() => setShowGenerateModal(true), []);
  const closeGenerateModal = useCallback(() => setShowGenerateModal(false), []);

  return {
    attempts,
    subjects,
    showGenerateModal,
    openGenerateModal,
    closeGenerateModal,
  };
}
