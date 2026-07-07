"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "@/hooks/use-auth";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/shared/sidebar";
import { Header } from "@/components/shared/header";
import { X, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export function DashboardLayoutClient({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Chặn truy cập phía Client nếu không được xác thực
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  // Đóng Mobile menu khi chuyển trang
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, []);

  // Màn hình chờ tải thông tin đăng nhập
  if (isLoading) {
    return (
      <div className="w-screen h-screen flex flex-col items-center justify-center bg-zinc-50 dark:bg-zinc-950">
        <Loader2 className="w-10 h-10 text-indigo-600 dark:text-indigo-400 animate-spin" />
        <span className="text-sm font-semibold text-zinc-500 dark:text-zinc-400 mt-4">
          Đang tải dữ liệu phiên đăng nhập...
        </span>
      </div>
    );
  }

  // Nếu không được xác thực, không hiển thị gì trong lúc chuyển hướng
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-50 transition-colors duration-200">
      {/* 1. Sidebar cố định cho màn hình Desktop (md trở lên) */}
      <div className="hidden md:block">
        <Sidebar />
      </div>

      {/* 2. Menu Sidebar ngăn kéo cho thiết bị di động (Mobile Drawer) */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <>
            {/* Backdrop làm mờ */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.5 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsMobileMenuOpen(false)}
              className="fixed inset-0 bg-black z-30 md:hidden"
            />
            {/* Thanh Sidebar di động trượt từ bên trái */}
            <motion.div
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", bounce: 0, duration: 0.3 }}
              className="fixed inset-y-0 left-0 w-64 bg-white dark:bg-zinc-900 z-40 md:hidden flex flex-col"
            >
              {/* Nút đóng Sidebar di động */}
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

      {/* 3. Phần nội dung chính (Main Content Area) */}
      <div className="md:pl-64 flex flex-col min-h-screen">
        {/* Header trên cùng */}
        <Header onMenuToggle={() => setIsMobileMenuOpen(true)} />
        
        {/* Vùng chứa Page nội dung */}
        <main className="flex-1 p-6 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
