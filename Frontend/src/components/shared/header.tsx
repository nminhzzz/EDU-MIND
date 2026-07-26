"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { toast } from "sonner";
import Link from "next/link";
import { Menu, Sun, Moon, Bell, ChevronDown, User, LogOut } from "lucide-react";
import { cn } from "@/utils/cn";

interface HeaderProps {
  onMenuToggle: () => void;
}

export function Header({ onMenuToggle }: HeaderProps) {
  const { user, logout } = useAuth();
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [dropdownOpen, setDropdownOpen] = useState(false);

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
      localStorage.setItem("theme", "light");
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
      toast.success("Đăng xuất thành công!");
    } catch {
      toast.error("Không thể đăng xuất.");
    }
  };

  const roleLabel =
    user?.role === "admin"
      ? "Quản trị viên"
      : user?.role === "teacher"
        ? "Giáo viên"
        : "Học sinh";

  const iconBtn =
    "flex h-9 w-9 items-center justify-center rounded-lg border border-border text-muted-foreground hover:text-foreground hover:bg-muted transition-colors cursor-pointer";

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-border bg-card/80 backdrop-blur-md px-4 md:px-6">
      {/* Mobile menu toggle */}
      <button
        onClick={onMenuToggle}
        aria-label="Mở menu"
        className={cn(iconBtn, "md:hidden")}
      >
        <Menu className="h-5 w-5" />
      </button>

      <div className="flex-1" />

      <div className="flex items-center gap-2 md:gap-3">
        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          className={iconBtn}
          aria-label="Chuyển chế độ Sáng/Tối"
          title="Chuyển chế độ Sáng/Tối"
        >
          {theme === "light" ? (
            <Moon className="h-[18px] w-[18px]" />
          ) : (
            <Sun className="h-[18px] w-[18px]" />
          )}
        </button>

        {/* Notifications */}
        <button className={cn(iconBtn, "relative")} aria-label="Thông báo" title="Thông báo">
          <Bell className="h-[18px] w-[18px]" />
          <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-destructive ring-2 ring-card" />
        </button>

        {/* Profile dropdown */}
        <div className="relative pl-1 md:pl-2 md:ml-1 md:border-l md:border-border">
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2.5 rounded-lg py-1 pl-1 pr-2 hover:bg-muted transition-colors cursor-pointer focus:outline-none"
            aria-haspopup="menu"
            aria-expanded={dropdownOpen}
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-muted text-primary font-bold text-xs">
              {user?.full_name ? user.full_name.charAt(0).toUpperCase() : "U"}
            </div>
            <div className="hidden lg:flex flex-col text-left leading-tight">
              <span className="max-w-[130px] truncate text-xs font-semibold text-foreground">
                {user?.full_name || "User"}
              </span>
              <span className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground">
                {roleLabel}
              </span>
            </div>
            <ChevronDown className="hidden lg:block h-4 w-4 text-muted-foreground" />
          </button>

          {dropdownOpen && (
            <>
              <div className="fixed inset-0 z-40" onClick={() => setDropdownOpen(false)} />
              <div
                role="menu"
                className="absolute right-0 z-50 mt-2 w-52 origin-top-right rounded-xl border border-border bg-popover p-1.5 shadow-lg animate-scale-in"
              >
                <div className="px-3 py-2 border-b border-border mb-1">
                  <p className="truncate text-sm font-semibold text-popover-foreground">
                    {user?.full_name || "User"}
                  </p>
                  <p className="truncate text-xs text-muted-foreground">{roleLabel}</p>
                </div>
                {user?.role === "student" && (
                  <Link
                    href="/student/profile"
                    onClick={() => setDropdownOpen(false)}
                    role="menuitem"
                    className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium text-popover-foreground hover:bg-muted transition-colors"
                  >
                    <User className="h-4 w-4 text-muted-foreground" />
                    Xem Profile
                  </Link>
                )}
                <button
                  onClick={() => {
                    setDropdownOpen(false);
                    handleLogout();
                  }}
                  role="menuitem"
                  className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-left text-sm font-medium text-destructive hover:bg-destructive/10 transition-colors cursor-pointer"
                >
                  <LogOut className="h-4 w-4" />
                  Đăng xuất
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
