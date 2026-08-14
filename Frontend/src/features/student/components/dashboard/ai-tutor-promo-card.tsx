"use client";

import React from "react";
import Link from "next/link";
import { ROUTES } from "@/constants/routes";
import type { StudentDashboardStats } from "@/features/student/types";

interface AiTutorPromoCardProps {
  stats: StudentDashboardStats | null;
  statsLoading: boolean;
}

export function AiTutorPromoCard({ stats, statsLoading }: AiTutorPromoCardProps) {
  return (
    <div className="bg-gradient-to-br from-sky-50/90 via-blue-50/70 to-slate-50 dark:from-sky-950/70 dark:to-slate-900 text-sky-950 dark:text-sky-100 p-8 rounded-md flex flex-col justify-between border border-sky-200/90 dark:border-sky-900/60 shadow-xs">
      <div className="space-y-6">
        <div className="space-y-2">
          <span className="text-[10px] font-bold tracking-wider text-sky-600 dark:text-sky-400 block uppercase">
            Gia sư AI 24/7
          </span>
          <h3 className="text-lg font-black tracking-tight text-sky-950 dark:text-white">Trợ lý học tập thông minh</h3>
          <p className="text-xs text-sky-900/75 dark:text-sky-300/80 leading-relaxed font-medium">
            Thảo luận trực tiếp cùng trợ lý học tập AI để được giải nghĩa lý thuyết, vẽ sơ đồ tư duy hoặc giải bài tập khó ngay lập tức.
          </p>
        </div>

        {!statsLoading && stats?.weak_areas && stats.weak_areas.length > 0 && (
          <div className="space-y-3 pt-5 border-t border-sky-200/80 dark:border-sky-900/60">
            <span className="text-[10px] font-bold text-sky-600 dark:text-sky-400 tracking-wider block uppercase">
              Kiến thức cần củng cố
            </span>
            <div className="flex flex-wrap gap-2">
              {stats.weak_areas.map((topic: string) => (
                <span
                  key={topic}
                  className="text-[9px] font-bold px-2.5 py-1 bg-white/90 dark:bg-sky-900/60 border border-sky-200 dark:border-sky-800 text-sky-800 dark:text-sky-200 rounded-md shadow-xs"
                >
                  {topic}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      <Link
        href={ROUTES.STUDENT_CHAT}
        className="mt-8 px-5 py-3.5 bg-sky-600 hover:bg-sky-700 dark:bg-sky-500 dark:hover:bg-sky-400 text-white dark:text-slate-950 rounded-md font-bold text-xs text-center tracking-wider transition-all shadow-md shadow-sky-500/15 border border-sky-600 active:scale-[0.98] cursor-pointer"
      >
        Hỏi Gia sư AI ngay
      </Link>
    </div>
  );
}
