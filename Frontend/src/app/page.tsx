"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  GraduationCap,
  Briefcase,
  ArrowRight,
  Sparkles,
  Route,
  MessagesSquare,
} from "lucide-react";
import { ROUTES } from "@/constants/routes";

export default function Home() {
  return (
    <div className="min-h-screen w-full flex flex-col bg-background">
      {/* Top navigation */}
      <header className="w-full border-b border-border">
        <div className="mx-auto flex h-16 w-full max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground text-sm font-black shadow-sm logo-em">
              EM
            </div>
            <span className="text-[15px] font-bold tracking-tight text-foreground">
              EduMind
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Link
              href={ROUTES.LOGIN}
              className="rounded-lg px-3.5 py-2 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
            >
              Đăng nhập
            </Link>
            <Link
              href={ROUTES.REGISTER}
              className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground shadow-sm hover:bg-primary/90 transition-colors"
            >
              Đăng ký
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <main className="flex-1">
        <section className="mx-auto flex w-full max-w-4xl flex-col items-center px-6 pt-20 pb-16 text-center">
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-3.5 py-1.5 text-xs font-medium text-muted-foreground"
          >
            <Sparkles className="h-3.5 w-3.5 text-primary" />
            Học tập cá nhân hóa cùng Gia sư AI
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.08, duration: 0.5 }}
            className="mt-6 max-w-2xl text-4xl font-bold leading-tight tracking-tight text-foreground text-balance md:text-5xl"
          >
            Nền tảng Học tập Cá nhân hóa Thông minh
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.16, duration: 0.5 }}
            className="mt-4 max-w-lg text-lg leading-relaxed text-muted-foreground text-pretty"
          >
            Tối ưu hóa lộ trình tự học, tự động hóa thi thử trắc nghiệm và thảo
            luận cùng Gia sư AI đồng hành 24/7.
          </motion.p>

          {/* Feature chips */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.24, duration: 0.5 }}
            className="mt-6 flex flex-wrap items-center justify-center gap-2"
          >
            {[
              { icon: Route, label: "Lộ trình học tập" },
              { icon: MessagesSquare, label: "Gia sư AI" },
              { icon: GraduationCap, label: "Thi thử tự chấm" },
            ].map(({ icon: Icon, label }) => (
              <span
                key={label}
                className="inline-flex items-center gap-1.5 rounded-lg bg-muted px-3 py-1.5 text-xs font-medium text-foreground"
              >
                <Icon className="h-3.5 w-3.5 text-primary" />
                {label}
              </span>
            ))}
          </motion.div>

          {/* Role cards */}
          <div className="mt-14 grid w-full max-w-2xl grid-cols-1 gap-5 text-left md:grid-cols-2">
            {/* Student */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.5 }}
              whileHover={{ y: -4 }}
              className="group flex flex-col justify-between rounded-2xl border border-border bg-card p-6 shadow-sm transition-shadow hover:shadow-md"
            >
              <div>
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary-muted text-primary transition-transform group-hover:scale-105">
                  <GraduationCap className="h-5 w-5" />
                </div>
                <h2 className="mt-5 text-lg font-semibold text-foreground">
                  Không gian Học sinh
                </h2>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                  Tự xây dựng lộ trình học tập mục tiêu, tương tác cùng Chatbot
                  AI Tutor để giải đáp kiến thức và thực hành làm đề trắc nghiệm
                  chấm điểm tự động.
                </p>
              </div>
              <Link
                href={ROUTES.STUDENT_DASHBOARD}
                className="mt-6 inline-flex items-center gap-1.5 text-sm font-semibold text-primary"
              >
                Vào học ngay
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
              </Link>
            </motion.div>

            {/* Teacher */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.38, duration: 0.5 }}
              whileHover={{ y: -4 }}
              className="group flex flex-col justify-between rounded-2xl border border-border bg-card p-6 shadow-sm transition-shadow hover:shadow-md"
            >
              <div>
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-muted text-foreground transition-transform group-hover:scale-105">
                  <Briefcase className="h-5 w-5" />
                </div>
                <h2 className="mt-5 text-lg font-semibold text-foreground">
                  Không gian Giáo viên
                </h2>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                  Quản lý ngân hàng tài liệu bài giảng, tạo lớp học trực quan,
                  theo dõi tiến độ làm bài thi thử của từng học sinh để tối ưu
                  hóa giảng dạy.
                </p>
              </div>
              <Link
                href={ROUTES.TEACHER_DASHBOARD}
                className="mt-6 inline-flex items-center gap-1.5 text-sm font-semibold text-foreground"
              >
                Truy cập giảng dạy
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
              </Link>
            </motion.div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border">
        <div className="mx-auto flex w-full max-w-6xl flex-col items-center justify-between gap-2 px-6 py-6 text-sm text-muted-foreground sm:flex-row">
          <span>© {new Date().getFullYear()} EduMind. Học tập thông minh.</span>
          <span>Được hỗ trợ bởi trí tuệ nhân tạo</span>
        </div>
      </footer>
    </div>
  );
}
