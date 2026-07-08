"use client";

import React from "react";
import Link from "next/link";
import { Plus } from "lucide-react";
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
      className="flex flex-col md:flex-row md:items-center justify-between gap-6 bg-gradient-to-tr from-indigo-500/10 via-violet-500/5 to-transparent border border-zinc-200/80 dark:border-zinc-800 p-8 rounded-2xl shadow-sm transition-all"
    >
      <div className="space-y-2 text-left">
        <span className="text-[10px] font-sans font-bold tracking-wider text-indigo-600 dark:text-indigo-400 block uppercase">
          Hệ thống Gia sư Học tập Thông minh AI
        </span>
        <h1 className="text-2xl font-black text-zinc-900 dark:text-white tracking-tight">
          Chào mừng quay lại, {fullName || "Học sinh"}!
        </h1>
        <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed font-medium">
          Lộ trình học cá nhân hóa được tự động giám sát và cập nhật liên tục từ AI Agent của bạn.
        </p>
      </div>
      <div className="flex flex-wrap gap-3">
        <button
          onClick={onJoinClassClick}
          className="px-5 py-3 bg-white hover:bg-zinc-50 border border-zinc-200 text-zinc-800 dark:bg-zinc-900 dark:hover:bg-zinc-800 dark:border-zinc-700 dark:text-zinc-100 rounded-xl font-bold text-xs tracking-wider transition-all shadow-sm active:scale-[0.98] cursor-pointer flex items-center gap-2"
        >
          <Plus className="w-4 h-4 text-indigo-500" />
          Vào lớp học
        </button>
        <Link
          href={ROUTES.STUDENT_GOALS}
          className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold text-xs tracking-wider transition-all shadow-lg shadow-indigo-500/10 hover:shadow-indigo-500/20 active:scale-[0.98] cursor-pointer flex items-center justify-center"
        >
          Đặt mục tiêu mới
        </Link>
      </div>
    </motion.div>
  );
}
