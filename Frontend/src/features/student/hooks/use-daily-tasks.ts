"use client";

import { useCallback, useState } from "react";
import { toast } from "sonner";
import { studyPlanService } from "@/features/student/services/study-plan";
import type { StudyPlan } from "@/features/student/types";
import { getLocalDateString } from "@/utils/date";

export function useDailyTasks() {
  const [tasks, setTasks] = useState<StudyPlan[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchTodayTasks = useCallback(async () => {
    setLoading(true);
    try {
      const todayStr = getLocalDateString();
      const response = await studyPlanService.getPlans({
        start_date: todayStr,
        end_date: todayStr,
      });
      setTasks(response.data);
    } catch (err) {
      console.error("Lỗi tải danh sách nhiệm vụ:", err);
      toast.error("Không thể tải nhiệm vụ học tập hôm nay.");
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    tasks,
    loading,
    fetchTodayTasks,
  };
}
