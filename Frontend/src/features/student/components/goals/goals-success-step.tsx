"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ROUTES } from "@/constants/routes";

export function GoalsSuccessStep() {
  return (
    <motion.div
      key="success"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0 }}
      className="max-w-md mx-auto text-center space-y-6 py-12"
    >
      <div className="w-16 h-16 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 rounded-full flex items-center justify-center text-3xl font-black mx-auto select-none">
        ✓
      </div>
      <div className="space-y-2">
        <h2 className="text-xl font-black text-zinc-950 dark:text-white uppercase">
          KÍCH HOẠT THÀNH CÔNG!
        </h2>
        <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed font-medium">
          Mục tiêu học tập của bạn đã được ghi nhận. AI Agent đã tạo đầy đủ các buổi học hàng ngày, tài liệu bài giảng và bộ câu hỏi ôn tập thông minh tương thích.
        </p>
      </div>
      <Link
        href={ROUTES.STUDENT_DASHBOARD}
        className="inline-block w-full py-3.5 bg-zinc-950 hover:bg-zinc-900 dark:bg-zinc-50 dark:hover:bg-zinc-100 text-zinc-50 dark:text-zinc-950 font-bold rounded-xl text-xs tracking-wider transition-all cursor-pointer"
      >
        ĐI ĐẾN BẢNG ĐIỀU KHIỂN {"->"}
      </Link>
    </motion.div>
  );
}
