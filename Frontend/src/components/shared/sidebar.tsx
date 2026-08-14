"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { ROUTES } from "@/constants/routes";
import {
  LayoutDashboard,
  CheckSquare,
  Map,
  Award,
  BookOpen,
  Users,
  FolderKanban,
  BrainCircuit,
} from "lucide-react";

interface SidebarItem {
  label: string;
  href: string;
  icon: React.ElementType;
}

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuth();

  const role = user?.role || "student";

  const studentItems: SidebarItem[] = [
    { label: "Tổng quan", href: ROUTES.STUDENT_DASHBOARD, icon: LayoutDashboard },
    { label: "Nhiệm vụ hôm nay", href: ROUTES.STUDENT_TASKS, icon: CheckSquare },
    { label: "Lộ trình học", href: ROUTES.STUDENT_GOALS, icon: Map },
    { label: "Bài kiểm tra", href: ROUTES.STUDENT_QUIZZES, icon: Award },
  ];

  const teacherItems: SidebarItem[] = [
    { label: "Tổng quan", href: ROUTES.TEACHER_DASHBOARD, icon: LayoutDashboard },
    { label: "Quản lý lớp học", href: ROUTES.TEACHER_CLASSROOMS, icon: Users },
    { label: "Tài liệu & đề thi", href: ROUTES.TEACHER_DOCUMENTS, icon: BookOpen },
  ];

  const adminItems: SidebarItem[] = [
    { label: "Tổng quan", href: "/admin", icon: LayoutDashboard },
    { label: "Người dùng", href: "/admin/users", icon: Users },
    { label: "Lớp học", href: "/admin/classrooms", icon: FolderKanban },
    { label: "Môn học", href: "/admin/subjects", icon: BookOpen },
  ];

  const menuItems = role === "admin" ? adminItems : role === "teacher" ? teacherItems : studentItems;

  return (
    <aside className="flex h-full w-64 flex-col border-r border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950 lg:fixed lg:inset-y-0 lg:left-0 lg:z-20">
      {/* Logo Thương Hiệu với Gradient & Glow */}
      <div className="flex h-16 items-center border-b border-zinc-200 px-5 dark:border-zinc-800">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="flex size-9 items-center justify-center rounded-lg bg-indigo-600 text-sm font-black text-white shadow-sm">
            EM
          </div>
          <div className="flex flex-col">
            <span className="text-base font-bold tracking-tight text-zinc-950 dark:text-white">
              EduMind
            </span>
            <span className="-mt-0.5 text-[10px] font-medium text-zinc-500 dark:text-zinc-400">
              Nền tảng học tập AI
            </span>
          </div>
        </Link>
      </div>

      {/* Thông tin vai trò (Role Badge) */}
      <div className="border-b border-zinc-100 px-5 py-3 dark:border-zinc-800">
        <div className="flex items-center gap-2">
          <BrainCircuit className="size-4 text-indigo-600 dark:text-indigo-400" />
          <span className="text-xs font-semibold text-zinc-600 dark:text-zinc-300">
            Không gian {role === "admin" ? "Quản trị" : role === "teacher" ? "Giáo viên" : "Học sinh"}
          </span>
        </div>
      </div>

      {/* Menu liên kết */}
      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-5">
        {menuItems.map((item) => {
          const isRoleHome = [
            ROUTES.STUDENT_DASHBOARD,
            ROUTES.TEACHER_DASHBOARD,
            "/admin",
          ].includes(item.href);
          const isActive = isRoleHome
            ? pathname === item.href
            : pathname === item.href || pathname.startsWith(item.href + "/");
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-950/50 dark:text-indigo-300"
                  : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-950 dark:text-zinc-400 dark:hover:bg-zinc-900 dark:hover:text-white"
              }`}
            >
              <Icon className={`size-5 ${isActive ? "text-indigo-600 dark:text-indigo-400" : "text-zinc-400 group-hover:text-zinc-700 dark:group-hover:text-zinc-200"}`} />

              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}

