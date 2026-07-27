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
        iconBg="bg-indigo-50 dark:bg-indigo-950/60"
        iconColor="text-indigo-600 dark:text-indigo-400"
        animationDelay={0.05}
      >
        <div className="w-full bg-zinc-100 dark:bg-zinc-800 h-2.5 rounded-full mt-4 overflow-hidden p-0.5 border border-zinc-200/50 dark:border-zinc-700/50">
          <div
            className="bg-gradient-to-r from-indigo-500 via-purple-500 to-violet-600 h-full rounded-full transition-all duration-700 shadow-sm"
            style={{ width: `${stats?.overall?.progress_pct || 0}%` }}
          />
        </div>
      </DashboardKpiCard>

      <DashboardKpiCard
        label="Mục tiêu hoạt động"
        value={statsLoading ? "-- mục tiêu" : `${stats?.active_goals || 0} đang chạy`}
        subtitle={
          <>
            <Bell className="w-3.5 h-3.5 text-amber-500" />
            Có {stats?.unread_notifications || 0} thông báo chưa đọc.
          </>
        }
        icon={Target}
        iconBg="bg-purple-50 dark:bg-purple-950/60"
        iconColor="text-purple-600 dark:text-purple-400"
        animationDelay={0.1}
      />
    </div>
  );
}

