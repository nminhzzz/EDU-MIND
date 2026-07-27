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
      className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-700 p-8 md:p-10 text-white shadow-xl shadow-indigo-500/20"
    >
      {/* Background Decorative Circles & Glowing Effects */}
      <div className="absolute -right-10 -bottom-10 w-72 h-72 bg-purple-400/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute right-1/3 -top-20 w-60 h-60 bg-indigo-300/20 rounded-full blur-2xl pointer-events-none" />

      <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-3 max-w-xl text-left">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/15 backdrop-blur-md border border-white/20 text-indigo-100 text-[11px] font-extrabold tracking-wider uppercase shadow-inner">
            <Sparkles className="w-3.5 h-3.5 text-amber-300 animate-spin" style={{ animationDuration: "4s" }} />
            Hệ thống Gia sư Học tập Thông minh AI
          </div>
          
          <h1 className="text-2xl md:text-3xl font-black tracking-tight text-white drop-shadow-sm">
            Chào mừng quay lại, {fullName || "Học sinh"}! 👋
          </h1>
          
          <p className="text-xs md:text-sm text-indigo-100/90 leading-relaxed font-medium">
            Lộ trình học cá nhân hóa được tự động giám sát và cập nhật liên tục từ AI Agent của bạn. Hãy sẵn sàng cho bài học hôm nay!
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={onJoinClassClick}
            className="px-5 py-3 bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/25 text-white rounded-xl font-bold text-xs tracking-wider transition-all shadow-lg active:scale-[0.98] cursor-pointer flex items-center gap-2"
          >
            <Plus className="w-4 h-4 text-amber-300" />
            Vào lớp học
          </button>
          
          <Link
            href={ROUTES.STUDENT_GOALS}
            className="px-6 py-3 bg-white hover:bg-indigo-50 text-indigo-700 rounded-xl font-extrabold text-xs tracking-wider transition-all shadow-xl shadow-black/10 hover:shadow-indigo-900/30 active:scale-[0.98] cursor-pointer flex items-center gap-2 group"
          >
            <Target className="w-4 h-4 text-indigo-600 group-hover:rotate-12 transition-transform" />
            Đặt mục tiêu mới
            <ArrowRight className="w-3.5 h-3.5 text-indigo-600 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>
      </div>
    </motion.div>
  );
}

