"use client";

import { useCallback, useState } from "react";
import { useSSE } from "./use-sse";
import type { StudentDashboardStats } from "@/features/student/types";

type DashboardSSEPayload = StudentDashboardStats & { error?: string };

export function useDashboardSSE() {
  const [stats, setStats] = useState<StudentDashboardStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [statsError, setStatsError] = useState<string | null>(null);

  const handleMessage = useCallback((parsed: DashboardSSEPayload) => {
    if (parsed.error) {
      setStatsError(parsed.error);
    } else {
      setStats(parsed);
      setStatsError(null);
    }
    setStatsLoading(false);
  }, []);

  const handleError = useCallback(() => {
    setStatsError("Mất kết nối đồng bộ dữ liệu thời gian thực.");
    setStatsLoading(false);
  }, []);

  const { connect } = useSSE<DashboardSSEPayload>({
    path: "/dashboard/stream",
    onMessage: handleMessage,
    onError: handleError,
  });

  return { stats, statsLoading, statsError, connect };
}
