"use client";

import { useCallback, useState } from "react";
import type { StudyPlan } from "@/features/student/types";

export type TaskStudyTab = "material" | "quiz";

export function useTaskStudy(
  task: StudyPlan,
  onRefresh?: (silent?: boolean) => void,
) {
  const [activeTab, setActiveTab] = useState<TaskStudyTab>("material");
  const subjectId = task.subject_id || 1;

  const handleQuizSuccess = useCallback(() => {
    // Keep the quiz pane mounted so its freshly returned result remains
    // visible. A full refresh temporarily unmounts TaskStudyView and resets the
    // active tab back to "material".
    onRefresh?.(true);
  }, [onRefresh]);

  return {
    activeTab,
    setActiveTab,
    subjectId,
    handleQuizSuccess,
  };
}
