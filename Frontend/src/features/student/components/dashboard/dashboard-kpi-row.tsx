"use client";

import React from "react";
import type { StudentDashboardStats } from "@/features/student/types";
import { DashboardKpiCard } from "./dashboard-kpi-card";

interface DashboardKpiRowProps {
  stats: StudentDashboardStats | null;
  statsLoading: boolean;
}

export function DashboardKpiRow({ stats, statsLoading }: DashboardKpiRowProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
      <DashboardKpiCard
        label="Điểm trung bình"
        value={statsLoading ? "-- / 10" : `${stats?.quizzes?.avg_score || "0.0"} / 10`}
        subtitle={`Từ ${stats?.quizzes?.total_attempts || 0} bài tập đã luyện tập.`}
      />

      <DashboardKpiCard
        label="Tiến độ lộ trình"
        value={statsLoading ? "-- %" : `${stats?.overall?.progress_pct || 0}%`}
        subtitle={`Đã xong ${stats?.overall?.done_plans || 0} / ${stats?.overall?.total_plans || 0} nhiệm vụ.`}
        animationDelay={0.05}
      >
        <div className="w-full bg-zinc-100 dark:bg-zinc-800 h-1.5 rounded-full mt-3 overflow-hidden">
          <div
            className="bg-indigo-600 dark:bg-indigo-400 h-full rounded-full transition-all duration-500"
            style={{ width: `${stats?.overall?.progress_pct || 0}%` }}
          />
        </div>
      </DashboardKpiCard>

      <DashboardKpiCard
        label="Mục tiêu hoạt động"
        value={statsLoading ? "-- mục tiêu" : `${stats?.active_goals || 0} đang chạy`}
        subtitle={`Có ${stats?.unread_notifications || 0} thông báo chưa đọc.`}
        animationDelay={0.1}
      />
    </div>
  );
}
