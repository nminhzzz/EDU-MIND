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
      className="flex flex-col md:flex-row md:items-center justify-between gap-6 bg-card border border-border p-6 sm:p-8 rounded-xl shadow-sm"
    >
      <div className="space-y-2 text-left">
        <span className="text-[11px] font-semibold tracking-wide text-primary block uppercase">
          Hệ thống Gia sư Học tập Thông minh AI
        </span>
        <h1 className="text-2xl font-bold text-foreground tracking-tight text-balance">
          Chào mừng quay lại, {fullName || "Học sinh"}!
        </h1>
        <p className="text-sm text-muted-foreground leading-relaxed">
          Lộ trình học cá nhân hóa được tự động giám sát và cập nhật liên tục từ AI Agent của bạn.
        </p>
      </div>
      <div className="flex flex-wrap gap-3">
        <button
          onClick={onJoinClassClick}
          className="px-4 py-2.5 bg-background hover:bg-accent border border-input text-foreground rounded-lg font-medium text-sm transition-colors shadow-sm active:scale-[0.99] cursor-pointer flex items-center gap-2"
        >
          <Plus className="w-4 h-4 text-primary" />
          Vào lớp học
        </button>
        <Link
          href={ROUTES.STUDENT_GOALS}
          className="px-5 py-2.5 bg-primary hover:bg-primary/90 text-primary-foreground rounded-lg font-medium text-sm transition-colors shadow-sm active:scale-[0.99] cursor-pointer flex items-center justify-center"
        >
          Đặt mục tiêu mới
        </Link>
      </div>
    </motion.div>
  );
}
