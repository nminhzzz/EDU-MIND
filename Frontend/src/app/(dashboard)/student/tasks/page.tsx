"use client";

import React, { useEffect } from "react";
import { DailyTasksView } from "@/features/student/components/study-plans/daily-tasks-view";
import { useDailyTasks } from "@/features/student/hooks/use-daily-tasks";

export default function StudentDailyTasksPage() {
  const { tasks, loading, fetchTodayTasks } = useDailyTasks();

  useEffect(() => {
    fetchTodayTasks();
  }, [fetchTodayTasks]);

  const todayLabel = new Date().toLocaleDateString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });

  return <DailyTasksView tasks={tasks} loading={loading} todayLabel={todayLabel} />;
}
