"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { GraduationCap, Briefcase, ArrowRight } from "lucide-react";
import { ROUTES } from "@/constants/routes";

export default function Home() {
  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center p-6 bg-gradient-to-tr from-zinc-50 via-zinc-100 to-indigo-50/30 dark:from-zinc-950 dark:via-zinc-900 dark:to-zinc-950 relative overflow-hidden">
      {/* Background Decorative Blobs */}
      <div className="absolute top-[-25%] left-[-15%] w-[60%] h-[60%] rounded-full bg-indigo-500/5 blur-[140px] pointer-events-none" />
      <div className="absolute bottom-[-25%] right-[-15%] w-[60%] h-[60%] rounded-full bg-violet-500/5 blur-[140px] pointer-events-none" />

      <div className="w-full max-w-4xl z-10 flex flex-col items-center">
        {/* Logo and Tagline */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6 }}
          className="w-16 h-16 rounded-3xl bg-gradient-to-tr from-indigo-600 to-violet-500 text-white font-black text-3xl flex items-center justify-center shadow-xl shadow-indigo-500/20 mb-6"
        >
          EM
        </motion.div>
        
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.6 }}
          className="text-4xl md:text-5xl font-black tracking-tight text-center bg-gradient-to-r from-zinc-900 via-zinc-800 to-zinc-900 dark:from-white dark:via-zinc-100 dark:to-white bg-clip-text text-transparent max-w-2xl leading-tight"
        >
          Nền tảng Học tập Cá nhân hóa Thông minh
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="text-zinc-500 dark:text-zinc-400 text-center mt-4 max-w-lg text-lg"
        >
          Tối ưu hóa lộ trình tự học, tự động hóa thi thử trắc nghiệm và thảo luận cùng Gia sư AI đồng hành 24/7.
        </motion.p>

        {/* Action Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-2xl mt-12">
          {/* Student Card */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            whileHover={{ y: -5 }}
            className="group bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl p-8 rounded-3xl shadow-lg dark:shadow-zinc-950/30 flex flex-col justify-between transition-all cursor-pointer"
          >
            <div>
              <div className="w-12 h-12 rounded-2xl bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <GraduationCap className="w-6 h-6" />
              </div>
              <h2 className="text-xl font-bold text-zinc-900 dark:text-white">Không gian Học sinh</h2>
              <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-2 leading-relaxed">
                Tự xây dựng lộ trình học tập mục tiêu, tương tác cùng Chatbot AI Tutor để giải đáp kiến thức và thực hành làm đề trắc nghiệm chấm điểm tự động.
              </p>
            </div>
            <Link href={ROUTES.STUDENT_DASHBOARD} className="mt-8 flex items-center justify-between text-sm font-bold text-indigo-600 dark:text-indigo-400 group-hover:text-indigo-500">
              Vào học ngay
              <ArrowRight className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" />
            </Link>
          </motion.div>

          {/* Teacher Card */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            whileHover={{ y: -5 }}
            className="group bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl p-8 rounded-3xl shadow-lg dark:shadow-zinc-950/30 flex flex-col justify-between transition-all cursor-pointer"
          >
            <div>
              <div className="w-12 h-12 rounded-2xl bg-violet-50 dark:bg-violet-950/50 text-violet-600 dark:text-violet-400 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Briefcase className="w-6 h-6" />
              </div>
              <h2 className="text-xl font-bold text-zinc-900 dark:text-white">Không gian Giáo viên</h2>
              <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-2 leading-relaxed">
                Quản lý ngân hàng tài liệu bài giảng, tạo lớp học trực quan, theo dõi tiến độ làm bài thi thử của từng học sinh để tối ưu hóa giảng dạy.
              </p>
            </div>
            <Link href={ROUTES.TEACHER_DASHBOARD} className="mt-8 flex items-center justify-between text-sm font-bold text-violet-600 dark:text-violet-400 group-hover:text-violet-500">
              Truy cập giảng dạy
              <ArrowRight className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" />
            </Link>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
