"use client";

import React from "react";
import { Calendar, Clock, BookOpen, Target } from "lucide-react";
import type { RoadmapPlan } from "@/types/goal";

interface DraftKpiWidgetsProps {
  plan: RoadmapPlan;
  targetScore: number;
}

export function DraftKpiWidgets({ plan, targetScore }: DraftKpiWidgetsProps) {
  const totalWeeks = plan.weeks ? plan.weeks.length : 0;
  const totalSessions = plan.daily_schedule ? plan.daily_schedule.length : 0;
  const avgSessionsPerWeek = totalWeeks > 0 ? (totalSessions / totalWeeks).toFixed(1) : 0;

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6 w-full">
      <div className="bg-zinc-50 dark:bg-zinc-950/40 border border-zinc-200/60 dark:border-zinc-850 p-3.5 rounded-2xl flex items-center gap-3">
        <div className="p-2.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 shrink-0">
          <Calendar className="w-4 h-4" />
        </div>
        <div>
          <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider block">Thời lượng</span>
          <span className="text-sm font-black text-zinc-900 dark:text-white font-mono">{totalWeeks} Tuần</span>
        </div>
      </div>

      <div className="bg-zinc-50 dark:bg-zinc-950/40 border border-zinc-200/60 dark:border-zinc-850 p-3.5 rounded-2xl flex items-center gap-3">
        <div className="p-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 shrink-0">
          <BookOpen className="w-4 h-4" />
        </div>
        <div>
          <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider block">Buổi học</span>
          <span className="text-sm font-black text-zinc-900 dark:text-white font-mono">{totalSessions} Buổi</span>
        </div>
      </div>

      <div className="bg-zinc-50 dark:bg-zinc-950/40 border border-zinc-200/60 dark:border-zinc-850 p-3.5 rounded-2xl flex items-center gap-3">
        <div className="p-2.5 rounded-xl bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400 shrink-0">
          <Clock className="w-4 h-4" />
        </div>
        <div>
          <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider block">Mật độ học</span>
          <span className="text-sm font-black text-zinc-900 dark:text-white font-mono">~{avgSessionsPerWeek} buổi/tuần</span>
        </div>
      </div>

      <div className="bg-zinc-50 dark:bg-zinc-950/40 border border-zinc-200/60 dark:border-zinc-850 p-3.5 rounded-2xl flex items-center gap-3">
        <div className="p-2.5 rounded-xl bg-purple-50 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400 shrink-0">
          <Target className="w-4 h-4" />
        </div>
        <div>
          <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider block">Mục tiêu</span>
          <span className="text-sm font-black text-zinc-900 dark:text-white font-mono">{targetScore} / 10</span>
        </div>
      </div>
    </div>
  );
}
