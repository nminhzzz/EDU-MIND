"use client";

import React from "react";
import { BookOpen, Calendar, Target, Zap } from "lucide-react";
import type { RoadmapPlan } from "@/types/goal";

interface DraftKpiWidgetsProps { plan: RoadmapPlan; targetScore: number }

export function DraftKpiWidgets({ plan, targetScore }: DraftKpiWidgetsProps) {
  const totalWeeks = plan.weeks?.length ?? 0;
  const totalSessions = plan.daily_schedule?.length ?? 0;
  const density = totalWeeks > 0 ? (totalSessions / totalWeeks).toFixed(1) : "0";
  const items = [
    { label: "Thời lượng", value: `${totalWeeks} tuần`, icon: Calendar },
    { label: "Buổi học", value: `${totalSessions} buổi`, icon: BookOpen },
    { label: "Mật độ", value: `${density} buổi/tuần`, icon: Zap },
    { label: "Mục tiêu", value: `${targetScore}/10`, icon: Target },
  ];

  return (
    <div className="grid w-full grid-cols-2 gap-3 lg:grid-cols-4">
      {items.map(({ label, value, icon: Icon }) => (
        <div key={label} className="flex min-w-0 items-center gap-3 rounded-xl border border-zinc-200 bg-zinc-50/60 p-4 dark:border-zinc-800 dark:bg-zinc-950/30">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-white text-indigo-600 shadow-sm ring-1 ring-zinc-200 dark:bg-zinc-900 dark:ring-zinc-800"><Icon className="size-5" /></div>
          <div className="min-w-0"><p className="text-xs font-medium text-zinc-500 dark:text-zinc-400">{label}</p><p className="truncate text-base font-bold text-zinc-950 dark:text-white">{value}</p></div>
        </div>
      ))}
    </div>
  );
}
