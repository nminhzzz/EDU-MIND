"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { ROUTES } from "@/constants/routes";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  CheckSquare,
  Map,
  Award,
  BookOpen,
  Users,
  FolderKanban,
  Sparkles,
} from "lucide-react";

interface SidebarItem {
  label: string;
  href: string;
  icon: React.ElementType;
  color: string;
}

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuth();

  const role = user?.role || "student";

  const studentItems: SidebarItem[] = [
    { label: "Tổng quan", href: ROUTES.STUDENT_DASHBOARD, icon: LayoutDashboard, color: "text-indigo-500" },
    { label: "Nhiệm vụ hôm nay", href: ROUTES.STUDENT_TASKS, icon: CheckSquare, color: "text-emerald-500" },
    { label: "Lộ trình học", href: ROUTES.STUDENT_GOALS, icon: Map, color: "text-amber-500" },
    { label: "Bài kiểm tra", href: ROUTES.STUDENT_QUIZZES, icon: Award, color: "text-rose-500" },
  ];

  const teacherItems: SidebarItem[] = [
    { label: "Tổng quan", href: ROUTES.TEACHER_DASHBOARD, icon: LayoutDashboard, color: "text-indigo-500" },
    { label: "Quản lý Lớp học", href: ROUTES.TEACHER_CLASSROOMS, icon: Users, color: "text-violet-500" },
    { label: "Tài liệu & Đề thi", href: ROUTES.TEACHER_DOCUMENTS, icon: BookOpen, color: "text-sky-500" },
  ];

  const adminItems: SidebarItem[] = [
    { label: "Tổng quan Admin", href: "/admin", icon: LayoutDashboard, color: "text-indigo-500" },
    { label: "Quản lý Người dùng", href: "/admin/users", icon: Users, color: "text-emerald-500" },
    { label: "Quản lý Lớp học", href: "/admin/classrooms", icon: FolderKanban, color: "text-amber-500" },
    { label: "Quản lý Môn học", href: "/admin/subjects", icon: BookOpen, color: "text-rose-500" },
  ];

  const menuItems = role === "admin" ? adminItems : role === "teacher" ? teacherItems : studentItems;

  return (
    <aside className="w-64 h-screen fixed left-0 top-0 z-20 flex flex-col border-r border-zinc-200/80 dark:border-zinc-800 bg-white/90 dark:bg-zinc-950/90 backdrop-blur-xl transition-colors duration-200">
      {/* Logo Thương Hiệu với Gradient & Glow */}
      <div className="h-16 flex items-center px-6 border-b border-zinc-200/80 dark:border-zinc-800">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-md bg-gradient-to-tr from-indigo-600 via-violet-600 to-purple-600 text-white font-black text-base flex items-center justify-center shadow-lg shadow-indigo-500/25 group-hover:scale-105 transition-transform duration-200">
            EM
          </div>
          <div className="flex flex-col">
            <span className="font-black text-base tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400">
              EduMind
            </span>
            <span className="text-[9px] font-bold text-zinc-400 dark:text-zinc-500 tracking-wider uppercase -mt-0.5">
              AI Assistant Platform
            </span>
          </div>
        </Link>
      </div>

      {/* Thông tin vai trò (Role Badge) */}
      <div className="px-6 py-3.5 border-b border-zinc-150 dark:border-zinc-850 bg-gradient-to-r from-indigo-50/50 to-purple-50/30 dark:from-indigo-950/20 dark:to-purple-950/10">
        <div className="flex items-center gap-2">
          <Sparkles className="w-3.5 h-3.5 text-indigo-500 animate-pulse" />
          <span className="text-[10px] font-extrabold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
            Không gian {role === "admin" ? "Quản trị" : role === "teacher" ? "Giáo viên" : "Học sinh"}
          </span>
        </div>
      </div>

      {/* Menu liên kết */}
      <nav className="flex-1 px-3 py-6 space-y-1.5 overflow-y-auto">
        {menuItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3.5 py-3 text-xs font-bold rounded-md transition-all duration-200 relative group ${
                isActive
                  ? "text-indigo-600 dark:text-indigo-300 bg-gradient-to-r from-indigo-500/10 via-purple-500/5 to-transparent border border-indigo-200/60 dark:border-indigo-800/40 shadow-sm"
                  : "text-zinc-600 dark:text-zinc-400 hover:text-zinc-950 dark:hover:text-white hover:bg-zinc-100/70 dark:hover:bg-zinc-900/60"
              }`}
            >
              {/* Thanh Highlight Active bên cạnh */}
              {isActive && (
                <motion.div
                  layoutId="activeIndicator"
                  className="absolute left-0 top-2 bottom-2 w-1.5 rounded-r-full bg-gradient-to-b from-indigo-600 to-violet-600 shadow-sm"
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                />
              )}
              
              <div className={`p-1.5 rounded-md transition-all ${
                isActive 
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-500/20" 
                  : "bg-zinc-100 dark:bg-zinc-900 text-zinc-500 group-hover:text-zinc-900 dark:group-hover:text-white"
              }`}>
                <Icon className={`w-4 h-4 ${isActive ? "text-white" : item.color}`} />
              </div>

              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}

