"use client";

import React from "react";
import Link from "next/link";
import { Plus, Sparkles, Target, ArrowRight } from "lucide-react";
import { ROUTES } from "@/features/student/constants";
import { Badge } from "@/components/ui";

interface StudentWelcomeBannerProps {
  fullName: string;
  onJoinClassClick: () => void;
}

export function StudentWelcomeBanner({ fullName, onJoinClassClick }: StudentWelcomeBannerProps) {
  return (
    <section className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900 sm:p-8">
      <div className="flex flex-col justify-between gap-6 md:flex-row md:items-center">
        <div className="space-y-3 max-w-xl text-left">
          <Badge className="border-indigo-200 bg-indigo-50 text-indigo-700 dark:border-indigo-900 dark:bg-indigo-950/50 dark:text-indigo-300"><Sparkles className="size-3.5" /> Trợ lý học tập AI</Badge>
          
          <h1 className="text-2xl font-bold tracking-tight text-zinc-950 dark:text-white md:text-3xl">
            Chào mừng quay lại, {fullName || "Học sinh"}! 👋
          </h1>
          
          <p className="max-w-2xl text-sm font-normal leading-6 text-zinc-600 dark:text-zinc-400">
            Lộ trình học cá nhân hóa được tự động giám sát và cập nhật liên tục từ AI Agent của bạn. Hãy sẵn sàng cho bài học hôm nay!
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={onJoinClassClick}
            className="px-5 py-3 bg-white hover:bg-sky-50/80 dark:bg-sky-900 dark:hover:bg-sky-800 text-sky-900 dark:text-sky-100 rounded-md font-bold text-xs tracking-wider transition-all border border-sky-200 dark:border-sky-700 active:scale-[0.98] cursor-pointer flex items-center gap-2 shadow-xs"
          >
            <Plus className="w-4 h-4 text-sky-600 dark:text-sky-400" />
            Vào lớp học
          </button>
          
          <Link
            href={ROUTES.STUDENT_GOALS}
            className="px-6 py-3 bg-sky-600 hover:bg-sky-700 dark:bg-sky-500 dark:hover:bg-sky-400 text-white dark:text-slate-950 rounded-md font-extrabold text-xs tracking-wider transition-all border border-sky-600 dark:border-sky-500 active:scale-[0.98] cursor-pointer flex items-center gap-2 group shadow-md shadow-sky-500/20"
          >
            <Target className="w-4 h-4 text-sky-100 dark:text-slate-900 group-hover:rotate-12 transition-transform" />
            Đặt mục tiêu mới
            <ArrowRight className="w-3.5 h-3.5 text-sky-100 dark:text-slate-900 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>
      </div>
    </section>
  );
}

