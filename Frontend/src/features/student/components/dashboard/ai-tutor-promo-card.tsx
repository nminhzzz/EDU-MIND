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
    <div className="bg-gradient-to-br from-indigo-900 via-indigo-950 to-zinc-950 dark:from-zinc-900 dark:to-zinc-950 text-zinc-50 p-8 rounded-2xl flex flex-col justify-between border border-zinc-200/5 dark:border-zinc-800 shadow-md">
      <div className="space-y-6">
        <div className="space-y-2">
          <span className="text-[10px] font-bold tracking-wider text-indigo-300 block uppercase">
            Gia sư AI 24/7
          </span>
          <h3 className="text-lg font-black tracking-tight">Trợ lý học tập thông minh</h3>
          <p className="text-xs text-zinc-400 leading-relaxed font-medium">
            Thảo luận trực tiếp cùng trợ lý học tập AI để được giải nghĩa lý thuyết, vẽ sơ đồ tư duy hoặc giải bài tập khó ngay lập tức.
          </p>
        </div>

        {!statsLoading && stats?.weak_areas && stats.weak_areas.length > 0 && (
          <div className="space-y-3 pt-5 border-t border-white/10 dark:border-zinc-800">
            <span className="text-[10px] font-bold text-zinc-400 tracking-wider block uppercase">
              Kiến thức cần củng cố
            </span>
            <div className="flex flex-wrap gap-2">
              {stats.weak_areas.map((topic: string) => (
                <span
                  key={topic}
                  className="text-[9px] font-bold px-2.5 py-1 bg-white/10 dark:bg-zinc-800/80 border border-white/5 dark:border-zinc-700 text-indigo-200 dark:text-indigo-400 rounded-lg"
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
        className="mt-8 px-5 py-3.5 bg-white hover:bg-zinc-100 text-indigo-950 rounded-xl font-bold text-xs text-center tracking-wider transition-all shadow-lg active:scale-[0.98] cursor-pointer"
      >
        Hỏi Gia sư AI ngay
      </Link>
    </div>
  );
}
