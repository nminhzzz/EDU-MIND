"use client";

import React from "react";
import type { StudentDashboardStats } from "@/features/student/types";
import { DashboardKpiCard } from "./dashboard-kpi-card";
import { TrendingUp, Target, Bell } from "lucide-react";

interface DashboardKpiRowProps {
  stats: StudentDashboardStats | null;
  statsLoading: boolean;
}

export function DashboardKpiRow({ stats, statsLoading }: DashboardKpiRowProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
      <DashboardKpiCard
        label="Tiến độ lộ trình"
        value={statsLoading ? "-- %" : `${stats?.overall?.progress_pct || 0}%`}
        subtitle={`Đã xong ${stats?.overall?.done_plans || 0} / ${stats?.overall?.total_plans || 0} nhiệm vụ.`}
        icon={TrendingUp}
        iconBg="bg-white dark:bg-sky-900/50 border border-sky-200 dark:border-sky-800"
        iconColor="text-sky-600 dark:text-sky-300"
        animationDelay={0.05}
      >
        <div className="w-full bg-sky-100 dark:bg-sky-950 h-2.5 rounded-full mt-4 overflow-hidden p-0.5 border border-sky-200/80 dark:border-sky-900">
          <div
            className="bg-gradient-to-r from-sky-400 to-blue-500 h-full rounded-full transition-all duration-700 shadow-xs"
            style={{ width: `${stats?.overall?.progress_pct || 0}%` }}
          />
        </div>
      </DashboardKpiCard>

      <DashboardKpiCard
        label="Mục tiêu hoạt động"
        value={statsLoading ? "-- mục tiêu" : `${stats?.active_goals || 0} đang chạy`}
        subtitle={
          <>
            <Bell className="w-3.5 h-3.5 text-sky-500" />
            Có {stats?.unread_notifications || 0} thông báo chưa đọc.
          </>
        }
        icon={Target}
        iconBg="bg-white dark:bg-sky-900/50 border border-sky-200 dark:border-sky-800"
        iconColor="text-sky-600 dark:text-sky-300"
        animationDelay={0.1}
      />
    </div>
  );
}

