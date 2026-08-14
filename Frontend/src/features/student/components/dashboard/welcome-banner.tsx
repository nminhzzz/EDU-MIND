"use client";

import React from "react";
import Link from "next/link";
import { Plus, Sparkles, Target, ArrowRight } from "lucide-react";
import { ROUTES } from "@/features/student/constants";
import { motion } from "framer-motion";

interface StudentWelcomeBannerProps {
  fullName: string;
  onJoinClassClick: () => void;
}

export function StudentWelcomeBanner({ fullName, onJoinClassClick }: StudentWelcomeBannerProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-sky-50 via-blue-50/60 to-cyan-50/40 dark:from-sky-950/60 dark:via-blue-950/40 dark:to-slate-900 p-8 md:p-10 text-sky-950 dark:text-sky-50 border border-sky-200/80 dark:border-sky-900/50 shadow-sm"
    >
      {/* Soft Sky Blue Glow Circle */}
      <div className="absolute -right-10 -bottom-10 w-72 h-72 bg-sky-200/60 dark:bg-sky-800/20 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-3 max-w-xl text-left">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/80 dark:bg-sky-900/60 border border-sky-200 dark:border-sky-800 text-sky-700 dark:text-sky-300 text-[11px] font-bold tracking-wider uppercase shadow-xs">
            <Sparkles className="w-3.5 h-3.5 text-sky-500 dark:text-sky-400" />
            Hệ thống Gia sư Học tập Thông minh AI
          </div>
          
          <h1 className="text-2xl md:text-3xl font-black tracking-tight text-sky-950 dark:text-white">
            Chào mừng quay lại, {fullName || "Học sinh"}! 👋
          </h1>
          
          <p className="text-xs md:text-sm text-sky-900/80 dark:text-sky-200/80 leading-relaxed font-medium">
            Lộ trình học cá nhân hóa được tự động giám sát và cập nhật liên tục từ AI Agent của bạn. Hãy sẵn sàng cho bài học hôm nay!
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={onJoinClassClick}
            className="px-5 py-3 bg-white hover:bg-sky-50/80 dark:bg-sky-900 dark:hover:bg-sky-800 text-sky-900 dark:text-sky-100 rounded-xl font-bold text-xs tracking-wider transition-all border border-sky-200 dark:border-sky-700 active:scale-[0.98] cursor-pointer flex items-center gap-2 shadow-xs"
          >
            <Plus className="w-4 h-4 text-sky-600 dark:text-sky-400" />
            Vào lớp học
          </button>
          
          <Link
            href={ROUTES.STUDENT_GOALS}
            className="px-6 py-3 bg-sky-600 hover:bg-sky-700 dark:bg-sky-500 dark:hover:bg-sky-400 text-white dark:text-slate-950 rounded-xl font-extrabold text-xs tracking-wider transition-all border border-sky-600 dark:border-sky-500 active:scale-[0.98] cursor-pointer flex items-center gap-2 group shadow-md shadow-sky-500/20"
          >
            <Target className="w-4 h-4 text-sky-100 dark:text-slate-900 group-hover:rotate-12 transition-transform" />
            Đặt mục tiêu mới
            <ArrowRight className="w-3.5 h-3.5 text-sky-100 dark:text-slate-900 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>
      </div>
    </motion.div>
  );
}

