"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ROUTES } from "@/features/student/constants";
import { studyPlanService } from "@/features/student/services/study-plan";
import type { StudyPlan } from "@/features/student/types";
import { toast } from "sonner";

export function useTaskDetail(taskId: string | undefined) {
  const router = useRouter();
  const [task, setTask] = useState<StudyPlan | null>(null);
  const [loading, setLoading] = useState(true);

  const loadTask = useCallback(async (silent = false) => {
    if (!taskId) return;

    if (!silent) setLoading(true);
    try {
      const response = await studyPlanService.getPlan(Number(taskId));
      setTask(response.data);
    } catch (err) {
      console.error("Lỗi tải chi tiết nhiệm vụ:", err);
      if (!silent) {
        toast.error("Không thể tải nhiệm vụ học tập.");
        router.push(ROUTES.STUDENT_TASKS);
      }
    } finally {
      if (!silent) setLoading(false);
    }
  }, [taskId, router]);

  useEffect(() => {
    loadTask();
  }, [loadTask]);

  return {
    task,
    loading,
    refreshTask: loadTask,
  };
}
