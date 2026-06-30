"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { ROUTES } from "@/constants/routes";
import { motion } from "framer-motion";

interface SidebarItem {
  label: string;
  href: string;
}

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuth();
  
  const role = user?.role || "student";

  const studentItems: SidebarItem[] = [
    { label: "Tổng quan", href: ROUTES.STUDENT_DASHBOARD },
    { label: "Lộ trình học", href: ROUTES.STUDENT_GOALS },
    { label: "Gia sư AI", href: ROUTES.STUDENT_CHAT },
    { label: "Luyện đề", href: "/student/quizzes" },
  ];

  const teacherItems: SidebarItem[] = [
    { label: "Tổng quan", href: ROUTES.TEACHER_DASHBOARD },
    { label: "Quản lý Lớp học", href: ROUTES.TEACHER_CLASSROOMS },
    { label: "Tài liệu & Đề thi", href: ROUTES.TEACHER_DOCUMENTS },
  ];

  const adminItems: SidebarItem[] = [
    { label: "Tổng quan Admin", href: "/admin" },
    { label: "Quản lý Người dùng", href: "/admin/users" },
    { label: "Quản lý Lớp học", href: "/admin/classrooms" },
    { label: "Quản lý Môn học", href: "/admin/subjects" },
  ];

  const menuItems = role === "admin" ? adminItems : role === "teacher" ? teacherItems : studentItems;

  return (
    <aside className="w-64 h-screen fixed left-0 top-0 z-20 flex flex-col border-r border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-950 transition-colors duration-200">
      {/* Logo Thương Hiệu */}
      <div className="h-16 flex items-center px-6 border-b border-zinc-200/80 dark:border-zinc-800">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-xl bg-indigo-600 text-white font-black text-sm flex items-center justify-center shadow-md shadow-indigo-500/20 logo-em">
            EM
          </div>
          <span className="font-extrabold text-sm tracking-wider text-zinc-900 dark:text-zinc-50 font-sans">
            EduMind
          </span>
        </Link>
      </div>

      {/* Thông tin vai trò (Role Badge) */}
      <div className="px-6 py-4 border-b border-zinc-200/80 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/10">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-sans font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500">
            • Không gian {role === "admin" ? "Quản trị" : role === "teacher" ? "Giáo viên" : "Học sinh"}
          </span>
        </div>
      </div>


      {/* Menu liên kết */}
      <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
        {menuItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center px-4 py-3 text-sm font-semibold rounded-xl transition-all duration-150 relative ${
                isActive
                  ? "text-indigo-600 dark:text-indigo-400 bg-indigo-50/60 dark:bg-indigo-950/20"
                  : "text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white hover:bg-zinc-50 dark:hover:bg-zinc-900/30"
              }`}
            >
              {/* Thanh Highlight Active bên cạnh */}
              {isActive && (
                <motion.div
                  layoutId="activeIndicator"
                  className="absolute left-0 top-2 bottom-2 w-1 rounded-full bg-indigo-600 dark:bg-indigo-400"
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                />
              )}
              <span className="mr-3 text-xs select-none">
                {isActive ? "●" : "○"}
              </span>
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
