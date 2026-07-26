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
    <div className="bg-primary text-primary-foreground p-6 sm:p-8 rounded-xl flex flex-col justify-between shadow-sm">
      <div className="space-y-6">
        <div className="space-y-2">
          <span className="text-[11px] font-semibold tracking-wide text-primary-foreground/70 block uppercase">
            Gia sư AI 24/7
          </span>
          <h3 className="text-lg font-bold tracking-tight">Trợ lý học tập thông minh</h3>
          <p className="text-sm text-primary-foreground/80 leading-relaxed">
            Thảo luận trực tiếp cùng trợ lý học tập AI để được giải nghĩa lý thuyết, vẽ sơ đồ tư duy hoặc giải bài tập khó ngay lập tức.
          </p>
        </div>

        {!statsLoading && stats?.weak_areas && stats.weak_areas.length > 0 && (
          <div className="space-y-3 pt-5 border-t border-primary-foreground/15">
            <span className="text-[11px] font-semibold text-primary-foreground/70 tracking-wide block uppercase">
              Kiến thức cần củng cố
            </span>
            <div className="flex flex-wrap gap-2">
              {stats.weak_areas.map((topic: string) => (
                <span
                  key={topic}
                  className="text-[11px] font-medium px-2.5 py-1 bg-primary-foreground/10 border border-primary-foreground/15 text-primary-foreground rounded-md"
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
        className="mt-8 px-5 py-2.5 bg-primary-foreground hover:bg-primary-foreground/90 text-primary rounded-lg font-semibold text-sm text-center transition-colors active:scale-[0.99] cursor-pointer"
      >
        Hỏi Gia sư AI ngay
      </Link>
    </div>
  );
}
