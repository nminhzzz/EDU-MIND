"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { ROUTES } from "@/constants/routes";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  ListChecks,
  Route,
  FileQuestion,
  Users,
  School,
  BookOpen,
  FolderOpen,
  ShieldCheck,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/utils/cn";

interface SidebarItem {
  label: string;
  href: string;
  icon: LucideIcon;
}

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuth();

  const role = user?.role || "student";

  const studentItems: SidebarItem[] = [
    { label: "Tổng quan", href: ROUTES.STUDENT_DASHBOARD, icon: LayoutDashboard },
    { label: "Nhiệm vụ hôm nay", href: ROUTES.STUDENT_TASKS, icon: ListChecks },
    { label: "Lộ trình học", href: ROUTES.STUDENT_GOALS, icon: Route },
    { label: "Bài kiểm tra", href: ROUTES.STUDENT_QUIZZES, icon: FileQuestion },
  ];

  const teacherItems: SidebarItem[] = [
    { label: "Tổng quan", href: ROUTES.TEACHER_DASHBOARD, icon: LayoutDashboard },
    { label: "Quản lý Lớp học", href: ROUTES.TEACHER_CLASSROOMS, icon: School },
    { label: "Tài liệu & Đề thi", href: ROUTES.TEACHER_DOCUMENTS, icon: FolderOpen },
  ];

  const adminItems: SidebarItem[] = [
    { label: "Tổng quan Admin", href: "/admin", icon: LayoutDashboard },
    { label: "Quản lý Người dùng", href: "/admin/users", icon: Users },
    { label: "Quản lý Lớp học", href: "/admin/classrooms", icon: School },
    { label: "Quản lý Môn học", href: "/admin/subjects", icon: BookOpen },
  ];

  const menuItems =
    role === "admin" ? adminItems : role === "teacher" ? teacherItems : studentItems;

  const roleLabel =
    role === "admin" ? "Quản trị" : role === "teacher" ? "Giáo viên" : "Học sinh";
  const RoleIcon = role === "admin" ? ShieldCheck : role === "teacher" ? School : BookOpen;

  return (
    <aside className="w-64 h-screen fixed left-0 top-0 z-20 flex flex-col border-r border-border bg-card">
      {/* Brand */}
      <div className="h-16 flex items-center px-5 border-b border-border">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-xl bg-primary text-primary-foreground font-black text-sm flex items-center justify-center shadow-sm logo-em">
            EM
          </div>
          <span className="font-bold text-[15px] tracking-tight text-foreground">
            EduMind
          </span>
        </Link>
      </div>

      {/* Role badge */}
      <div className="px-4 pt-4 pb-2">
        <div className="flex items-center gap-2.5 rounded-lg bg-muted px-3 py-2.5">
          <span className="flex h-7 w-7 items-center justify-center rounded-md bg-card text-primary shadow-sm">
            <RoleIcon className="h-4 w-4" />
          </span>
          <div className="flex flex-col">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              Không gian
            </span>
            <span className="text-xs font-bold text-foreground">{roleLabel}</span>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-3 space-y-1 overflow-y-auto">
        <span className="px-3 pb-1 pt-2 block text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
          Menu
        </span>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive =
            pathname === item.href || pathname.startsWith(item.href + "/");

          return (
            <Link
              key={item.href}
              href={item.href}
              aria-current={isActive ? "page" : undefined}
              className={cn(
                "group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary-muted text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              {isActive && (
                <motion.span
                  layoutId="activeIndicator"
                  className="absolute left-0 top-1.5 bottom-1.5 w-1 rounded-full bg-primary"
                  transition={{ type: "spring", stiffness: 350, damping: 30 }}
                />
              )}
              <Icon
                className={cn(
                  "h-[18px] w-[18px] shrink-0 transition-colors",
                  isActive
                    ? "text-primary"
                    : "text-muted-foreground group-hover:text-foreground"
                )}
              />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-border">
        <p className="text-[11px] text-muted-foreground">
          EduMind · Học tập thông minh
        </p>
      </div>
    </aside>
  );
}
