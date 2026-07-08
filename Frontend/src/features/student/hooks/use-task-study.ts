"use client";

import { useCallback, useState } from "react";
import type { StudyPlan } from "@/features/student/types";

export type TaskStudyTab = "material" | "quiz";

export function useTaskStudy(task: StudyPlan, onRefresh?: () => void) {
  const [activeTab, setActiveTab] = useState<TaskStudyTab>("material");
  const subjectId = task.subject_id || 1;

  const handleQuizSuccess = useCallback(() => {
    onRefresh?.();
  }, [onRefresh]);

  return {
    activeTab,
    setActiveTab,
    subjectId,
    handleQuizSuccess,
  };
}
