"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "@/hooks/use-auth";
import { useRouter, usePathname } from "next/navigation";
import { Sidebar } from "@/components/shared/sidebar";
import { Header } from "@/components/shared/header";
import { X, Loader2, ShieldAlert } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { FloatingTutorChat } from "@/components/student/floating-tutor-chat";
import { FloatingClassroomChat } from "@/components/student/floating-classroom-chat";

export function DashboardLayoutClient({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, isLoading, user } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Check if currently on a quiz attempt page (/student/quizzes/[id])
  const isQuizPage = pathname.startsWith("/student/quizzes/") && pathname !== "/student/quizzes";

  // 1. Unauthenticated Guard
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      const params = new URLSearchParams({ redirect: pathname });
      router.push(`/login?${params.toString()}`);
    }
  }, [isLoading, isAuthenticated, pathname, router]);

  // 2. Strict Client-Side Role Guard (RBAC)
  const isStudentRoute = pathname.startsWith("/student");
  const isTeacherRoute = pathname.startsWith("/teacher");
  const isAdminRoute = pathname.startsWith("/admin");

  const isRoleAuthorized = React.useMemo(() => {
    if (!user?.role) return true; // still loading or unauthenticated
    if (isStudentRoute && user.role !== "student") return false;
    if (isTeacherRoute && user.role !== "teacher") return false;
    if (isAdminRoute && user.role !== "admin") return false;
    return true;
  }, [user?.role, isStudentRoute, isTeacherRoute, isAdminRoute]);

  useEffect(() => {
    if (!isLoading && isAuthenticated && user?.role && !isRoleAuthorized) {
      // Instantly redirect unauthorized user to their correct role home dashboard
      router.replace(`/${user.role}`);
    }
  }, [isLoading, isAuthenticated, user?.role, isRoleAuthorized, router]);

  // Close Mobile menu on route change
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [pathname]);

  // Loading state screen
  if (isLoading) {
    return (
      <div className="w-screen h-screen flex flex-col items-center justify-center bg-zinc-50 dark:bg-zinc-950">
        <Loader2 className="w-10 h-10 text-indigo-600 dark:text-indigo-400 animate-spin" />
        <span className="text-sm font-semibold text-zinc-500 dark:text-zinc-400 mt-4">
          Đang xác thực quyền truy cập...
        </span>
      </div>
    );
  }

  // Not authenticated or Role Unauthorized → Return null while redirecting
  if (!isAuthenticated || !isRoleAuthorized) {
    return (
      <div className="w-screen h-screen flex flex-col items-center justify-center bg-zinc-50 dark:bg-zinc-950 space-y-3">
        <ShieldAlert className="w-10 h-10 text-rose-500 animate-pulse" />
        <span className="text-sm font-semibold text-zinc-600 dark:text-zinc-400">
          Chuyển hướng về trang của vai trò phù hợp...
        </span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-50 transition-colors duration-200">
      {/* 1. Desktop Sidebar (md and above) */}
      <div className="hidden lg:block">
        <Sidebar />
      </div>

      {/* 2. Mobile Drawer Sidebar */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.5 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsMobileMenuOpen(false)}
              className="fixed inset-0 z-30 bg-black lg:hidden"
            />
            {/* Sliding Mobile Sidebar */}
            <motion.div
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", bounce: 0, duration: 0.3 }}
              className="fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-white shadow-2xl dark:bg-zinc-900 lg:hidden"
            >
              <div className="h-16 flex items-center justify-end px-6 border-b border-zinc-200 dark:border-zinc-800">
                <button
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="p-2 text-zinc-500 hover:text-zinc-950 dark:hover:text-white cursor-pointer"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              <div className="flex-1 overflow-y-auto">
                <Sidebar />
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* 3. Main Content Area */}
      <div className="flex min-h-screen flex-col lg:pl-64">
        {/* Header */}
        <Header onMenuToggle={() => setIsMobileMenuOpen(true)} />

        {/* Page Content */}
        <main className="flex-1 overflow-x-hidden px-4 py-5 sm:px-6 sm:py-6 xl:px-8">
          <div className="mx-auto w-full max-w-[1440px]">{children}</div>
        </main>
      </div>

      {/* Floating Chat Widgets — Hide during active quiz attempts & for non-student roles */}
      {!isQuizPage && user?.role === "student" && <FloatingTutorChat />}
      {!isQuizPage && (user?.role === "student" || user?.role === "teacher") && (
        <FloatingClassroomChat />
      )}
    </div>
  );
}
