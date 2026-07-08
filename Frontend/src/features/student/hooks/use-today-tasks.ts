"use client";

import { useCallback, useState } from "react";
import { studyPlanService } from "@/features/student/services/study-plan";
import type { StudyPlan } from "@/features/student/types";
import { getLocalDateString } from "@/utils/date";

/** @deprecated Use useDailyTasks instead */
export function useTodayTasks() {
  const [tasks, setTasks] = useState<StudyPlan[]>([]);
  const [tasksLoading, setTasksLoading] = useState(true);

  const fetchTodayTasks = useCallback(async () => {
    try {
      const todayStr = getLocalDateString();
      const response = await studyPlanService.getPlans({
        start_date: todayStr,
        end_date: todayStr,
      });
      setTasks(response.data);
    } catch (err) {
      console.error("Lỗi tải danh sách nhiệm vụ:", err);
    } finally {
      setTasksLoading(false);
    }
  }, []);

  return {
    tasks,
    tasksLoading,
    fetchTodayTasks,
  };
}
