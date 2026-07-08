"use client";

import { useEffect } from "react";
import { useDashboardSSE } from "./use-dashboard-sse";
import { useStudentClassrooms } from "./use-student-classrooms";
import { useTodayTasks } from "./use-today-tasks";

export function useDashboard() {
  const sse = useDashboardSSE();
  const tasks = useTodayTasks();
  const classrooms = useStudentClassrooms();

  useEffect(() => {
    const disconnect = sse.connect();
    tasks.fetchTodayTasks();
    classrooms.fetchClassrooms();
    return disconnect;
  }, [sse.connect, tasks.fetchTodayTasks, classrooms.fetchClassrooms]);

  return {
    stats: sse.stats,
    statsLoading: sse.statsLoading,
    statsError: sse.statsError,
    ...tasks,
    ...classrooms,
  };
}
