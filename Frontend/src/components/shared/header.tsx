"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { toast } from "sonner";

interface HeaderProps {
  onMenuToggle: () => void;
}

export function Header({ onMenuToggle }: HeaderProps) {
  const { user, logout } = useAuth();
  const [theme, setTheme] = useState<"light" | "dark">("light");

  // Đọc theme từ localStorage khi load trang
  useEffect(() => {
    const savedTheme = localStorage.getItem("theme");
    const isDarkSystem = window.matchMedia("(prefers-color-scheme: dark)").matches;
    
    if (savedTheme === "dark" || (!savedTheme && isDarkSystem)) {
      setTheme("dark");
      document.documentElement.classList.add("dark");
    } else {
      setTheme("light");
      document.documentElement.classList.remove("dark");
    }
  }, []);

  // Chuyển đổi Dark/Light mode
  const toggleTheme = () => {
    if (theme === "light") {
      setTheme("dark");
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      setTheme("light");
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      toast.success("Đã đăng xuất thành công.");
    } catch (e) {
      toast.error("Có lỗi xảy ra khi đăng xuất.");
    }
  };

  return (
    <header className="h-16 border-b border-zinc-200/80 dark:border-zinc-800 bg-white dark:bg-zinc-950 px-6 flex items-center justify-between sticky top-0 z-10 transition-colors duration-200">
      {/* Nút Hamburger cho Mobile & Title */}
      <div className="flex items-center gap-4">
        <button 
          onClick={onMenuToggle}
          className="md:hidden px-3.5 py-1.5 border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-900 rounded-xl text-xs font-bold text-zinc-600 dark:text-zinc-400 cursor-pointer"
        >
          Menu
        </button>
        <span className="font-bold text-xs tracking-wider text-zinc-400 dark:text-zinc-500 hidden md:inline uppercase">
          • Hệ thống học tập thông minh
        </span>
      </div>

      {/* Các chức năng bên phải */}
      <div className="flex items-center gap-3">
        {/* Nút chuyển Light/Dark Mode */}
        <button 
          onClick={toggleTheme}
          className="px-3.5 py-1.5 border border-zinc-200 dark:border-zinc-800 rounded-xl text-xs font-semibold text-zinc-600 dark:text-zinc-400 hover:text-zinc-950 dark:hover:text-white hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-colors cursor-pointer"
          title="Chuyển chế độ Sáng/Tối"
        >
          {theme === "light" ? "Giao diện: Tối" : "Giao diện: Sáng"}
        </button>

        {/* Nút Thông báo */}
        <button 
          className="px-3.5 py-1.5 border border-zinc-200 dark:border-zinc-800 rounded-xl text-xs font-semibold text-zinc-600 dark:text-zinc-400 hover:text-zinc-950 dark:hover:text-white hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-colors cursor-pointer relative"
          title="Thông báo"
        >
          Thông báo
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
        </button>

        {/* Khung User Profile */}
        <div className="flex items-center gap-3 pl-3 border-l border-zinc-200 dark:border-zinc-800">
          <div className="w-8 h-8 rounded-xl bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold text-xs">
            {user?.full_name ? user.full_name.charAt(0).toUpperCase() : "U"}
          </div>
          <div className="hidden lg:flex flex-col text-left">
            <span className="text-xs font-bold text-zinc-800 dark:text-zinc-100 max-w-[120px] truncate">
              {user?.full_name || "User"}
            </span>
            <span className="text-[10px] text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">
              {user?.role === "teacher" ? "Giáo viên" : "Học sinh"}
            </span>
          </div>
        </div>

        {/* Nút Đăng xuất */}
        <button 
          onClick={handleLogout}
          className="px-3.5 py-1.5 border border-zinc-200 dark:border-zinc-800 hover:border-red-200 dark:hover:border-red-950 hover:bg-red-50/50 dark:hover:bg-red-950/20 rounded-xl text-xs font-bold text-zinc-500 hover:text-red-600 dark:hover:text-red-400 transition-colors ml-1 cursor-pointer"
          title="Đăng xuất"
        >
          Đăng xuất
        </button>
      </div>
    </header>
  );
}
