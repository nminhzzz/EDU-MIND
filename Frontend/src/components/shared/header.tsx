"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { toast } from "sonner";
import Link from "next/link";
import { ChevronDown, LogOut, Menu, UserRound } from "lucide-react";

interface HeaderProps {
  onMenuToggle: () => void;
}

export function Header({ onMenuToggle }: HeaderProps) {
  const { user, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  // The product now uses one consistent light appearance.
  useEffect(() => {
    document.documentElement.classList.remove("dark");
    localStorage.removeItem("theme");
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
      toast.success("Đăng xuất thành công!");
    } catch {
      toast.error("Không thể đăng xuất.");
    }
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-zinc-200 bg-white/95 px-4 backdrop-blur-md dark:border-zinc-800 dark:bg-zinc-950/95 sm:px-6">
      {/* Nút Toggle Sidebar (Chỉ ẩn hiện trên Mobile) */}
      <button
        onClick={onMenuToggle}
        className="rounded-lg p-2 text-zinc-600 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-900 lg:hidden"
        aria-label="Mở menu điều hướng"
      >
        <Menu className="size-5" />
      </button>

      <div className="flex-1" />

      <div className="flex items-center gap-2 sm:gap-3">
        {/* Khung User Profile Dropdown */}
        <div className="relative">
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2 rounded-lg p-1.5 hover:bg-zinc-100 focus-visible:outline-2 focus-visible:outline-indigo-600 dark:hover:bg-zinc-900"
          >
            {user?.avatar_url ? (
              <img
                src={user.avatar_url}
                alt={user.full_name || "Avatar"}
                className="w-8 h-8 rounded-md object-cover border border-zinc-200 dark:border-zinc-800 shrink-0"
              />
            ) : (
              <div className="w-8 h-8 rounded-md bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold text-xs shrink-0">
                {user?.full_name ? user.full_name.charAt(0).toUpperCase() : "U"}
              </div>
            )}
            <div className="hidden lg:flex flex-col text-left">
              <span className="text-xs font-bold text-zinc-800 dark:text-zinc-100 max-w-[120px] truncate">
                {user?.full_name || "User"}
              </span>

              <span className="text-[10px] text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">
                {user?.role === "teacher" ? "Giáo viên" : "Học sinh"}
              </span>
            </div>
            <ChevronDown className="hidden size-4 text-zinc-400 sm:block" />
          </button>

          {dropdownOpen && (
            <>
              {/* Overlay để đóng dropdown */}
              <div
                className="fixed inset-0 z-40"
                onClick={() => setDropdownOpen(false)}
              />
              <div className="absolute right-0 mt-2.5 w-48 bg-white dark:bg-zinc-950 border border-zinc-150 dark:border-zinc-800/80 rounded-md shadow-xl z-50 p-2 py-1.5 animate-fadeIn">
                {user?.role === "student" && (
                  <Link
                    href="/student/profile"
                    onClick={() => setDropdownOpen(false)}
                    className="flex items-center gap-2 px-3 py-2 text-xs font-bold text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-900 rounded-md transition-colors"
                  >
                    <UserRound className="size-4" /> Hồ sơ cá nhân
                  </Link>
                )}
                <button
                  onClick={() => {
                    setDropdownOpen(false);
                    handleLogout();
                  }}
                  className="w-full text-left flex items-center gap-2 px-3 py-2 text-xs font-bold text-red-600 dark:text-red-400 hover:bg-red-50/50 dark:hover:bg-red-950/20 rounded-md transition-colors cursor-pointer"
                >
                  <LogOut className="size-4" /> Đăng xuất
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
