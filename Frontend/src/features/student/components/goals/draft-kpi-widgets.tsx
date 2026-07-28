"use client";

import React from "react";
import { Calendar, Clock, BookOpen, Target, Zap } from "lucide-react";
import type { RoadmapPlan } from "@/types/goal";

interface DraftKpiWidgetsProps {
  plan: RoadmapPlan;
  targetScore: number;
}

export function DraftKpiWidgets({ plan, targetScore }: DraftKpiWidgetsProps) {
  const totalWeeks = plan.weeks ? plan.weeks.length : 0;
  const totalSessions = plan.daily_schedule ? plan.daily_schedule.length : 0;
  const avgSessionsPerWeek = totalWeeks > 0 ? (totalSessions / totalWeeks).toFixed(1) : "0";

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5 mb-6 w-full">
      {/* 1. Thời lượng */}
      <div className="relative overflow-hidden bg-gradient-to-br from-indigo-50/80 via-white to-violet-50/50 dark:from-indigo-950/40 dark:via-zinc-900 dark:to-violet-950/30 border border-indigo-100 dark:border-indigo-900/40 p-4 rounded-2xl flex items-center gap-3.5 shadow-xs hover:shadow-md transition-all">
        <div className="p-3 rounded-xl bg-indigo-600 text-white shadow-md shadow-indigo-600/20 shrink-0">
          <Calendar className="w-5 h-5" />
        </div>
        <div>
          <span className="text-[10px] font-extrabold text-indigo-900/60 dark:text-indigo-300/70 uppercase tracking-wider block">
            Thời lượng
          </span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-lg font-black text-indigo-950 dark:text-white font-mono tracking-tight">
              {totalWeeks}
            </span>
            <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">Tuần</span>
          </div>
        </div>
      </div>

      {/* 2. Buổi học */}
      <div className="relative overflow-hidden bg-gradient-to-br from-emerald-50/80 via-white to-teal-50/50 dark:from-emerald-950/40 dark:via-zinc-900 dark:to-teal-950/30 border border-emerald-100 dark:border-emerald-900/40 p-4 rounded-2xl flex items-center gap-3.5 shadow-xs hover:shadow-md transition-all">
        <div className="p-3 rounded-xl bg-emerald-600 text-white shadow-md shadow-emerald-600/20 shrink-0">
          <BookOpen className="w-5 h-5" />
        </div>
        <div>
          <span className="text-[10px] font-extrabold text-emerald-900/60 dark:text-emerald-300/70 uppercase tracking-wider block">
            Buổi học
          </span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-lg font-black text-emerald-950 dark:text-white font-mono tracking-tight">
              {totalSessions}
            </span>
            <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400">Buổi</span>
          </div>
        </div>
      </div>

      {/* 3. Mật độ học */}
      <div className="relative overflow-hidden bg-gradient-to-br from-amber-50/80 via-white to-orange-50/50 dark:from-amber-950/40 dark:via-zinc-900 dark:to-orange-950/30 border border-amber-100 dark:border-amber-900/40 p-4 rounded-2xl flex items-center gap-3.5 shadow-xs hover:shadow-md transition-all">
        <div className="p-3 rounded-xl bg-amber-500 text-white shadow-md shadow-amber-500/20 shrink-0">
          <Zap className="w-5 h-5" />
        </div>
        <div>
          <span className="text-[10px] font-extrabold text-amber-900/60 dark:text-amber-300/70 uppercase tracking-wider block">
            Mật độ học
          </span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-lg font-black text-amber-950 dark:text-white font-mono tracking-tight">
              ~{avgSessionsPerWeek}
            </span>
            <span className="text-xs font-bold text-amber-600 dark:text-amber-400">buổi/tuần</span>
          </div>
        </div>
      </div>

      {/* 4. Mục tiêu */}
      <div className="relative overflow-hidden bg-gradient-to-br from-purple-50/80 via-white to-fuchsia-50/50 dark:from-purple-950/40 dark:via-zinc-900 dark:to-fuchsia-950/30 border border-purple-100 dark:border-purple-900/40 p-4 rounded-2xl flex items-center gap-3.5 shadow-xs hover:shadow-md transition-all">
        <div className="p-3 rounded-xl bg-purple-600 text-white shadow-md shadow-purple-600/20 shrink-0">
          <Target className="w-5 h-5" />
        </div>
        <div>
          <span className="text-[10px] font-extrabold text-purple-900/60 dark:text-purple-300/70 uppercase tracking-wider block">
            Mục tiêu điểm
          </span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-lg font-black text-purple-950 dark:text-white font-mono tracking-tight">
              {targetScore}
            </span>
            <span className="text-xs font-bold text-purple-600 dark:text-purple-400">/ 10</span>
          </div>
        </div>
      </div>
    </div>
  );
}
