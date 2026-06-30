"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { useRouter } from "next/navigation";
import { apiClient } from "@/services/api-client";
import Link from "next/link";
import { toast } from "sonner";
import { motion } from "framer-motion";

export default function AdminDashboard() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  const [analytics, setAnalytics] = useState<any>(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // ── GIẢI THÍCH CHI TIẾT CSR VÀ SSR ──
  // 1. Tại sao dùng Client-Side Rendering (CSR) ở đây?
  // - Bảo mật và Phân quyền: Cần kiểm tra vai trò (role) của người dùng hiện tại (useAuth) trên trình duyệt trước khi render dữ liệu nhạy cảm.
  // - Tránh lỗi phân giải Docker: Nếu gọi API ở Server Component (SSR), `localhost` sẽ trỏ vào chính container frontend thay vì host máy của bạn, dẫn đến lỗi kết nối. Gọi ở Client Component sẽ chạy trên trình duyệt của người dùng nên phân giải localhost chính xác.
  // - Trải nghiệm tương tác: Hỗ trợ skeleton loading mượt mà, toast báo lỗi thời gian thực và chuyển trang nhanh.

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) {
        router.push("/login");
        return;
      }
      if (user?.role !== "admin") {
        setError("Bạn không có quyền truy cập trang quản trị này.");
        setAnalyticsLoading(false);
        return;
      }

      // Tải báo cáo thống kê từ Backend
      apiClient
        .get("/analytics/admin/system")
        .then((res) => {
          setAnalytics(res.data);
          setError(null);
        })
        .catch((err) => {
          console.error("Lỗi tải báo cáo admin:", err);
          setError("Không thể kết nối đến API thống kê của hệ thống.");
        })
        .finally(() => {
          setAnalyticsLoading(false);
        });
    }
  }, [isLoading, isAuthenticated, user, router]);

  if (isLoading || analyticsLoading) {
    return (
      <div className="py-24 text-center space-y-4">
        <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400 font-mono">
          Đang tải dữ liệu báo cáo hệ thống...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-md mx-auto text-center py-20 space-y-6">
        <div className="w-16 h-16 bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20 rounded-full flex items-center justify-center text-2xl font-black mx-auto">
          !
        </div>
        <div className="space-y-2">
          <h2 className="text-lg font-black text-zinc-950 dark:text-white uppercase">
            TRUY CẬP BỊ TỪ CHỐI
          </h2>
          <p className="text-xs text-zinc-500 dark:text-zinc-400 font-medium">
            {error}
          </p>
        </div>
        <Link
          href="/"
          className="inline-block px-6 py-3 bg-zinc-950 hover:bg-zinc-900 dark:bg-zinc-50 dark:hover:bg-zinc-100 text-zinc-50 dark:text-zinc-950 font-bold rounded-xl text-xs"
        >
          Quay lại Trang chủ
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 text-left">
      {/* Lời chào mừng của Admin */}
      <div className="bg-gradient-to-tr from-indigo-500/10 via-violet-500/5 to-transparent border border-zinc-200/80 dark:border-zinc-800 p-8 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-sm">
        <div className="space-y-2">
          <span className="text-[10px] font-sans font-bold tracking-wider text-indigo-600 dark:text-indigo-400 block uppercase">
            Trang Quản trị Hệ Thống
          </span>
          <h1 className="text-2xl font-black text-zinc-900 dark:text-white tracking-tight">
            Xin chào Quản trị viên, {user?.full_name || "Admin"}!
          </h1>
          <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed font-medium">
            Giám sát các chỉ số vận hành, quản lý người dùng, bộ môn học tập và
            xử lý cấu hình toàn bộ hệ thống EduMind.
          </p>
        </div>
      </div>

      {/* Grid thống kê KPI */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        {/* KPI Học sinh */}
        <motion.div
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-850 p-6 rounded-2xl shadow-sm"
        >
          <span className="text-[10px] font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider block">
            Học sinh hệ thống
          </span>
          <div className="text-3xl font-black text-zinc-900 dark:text-white mt-1">
            {analytics?.total_students || 0}
          </div>
          <span className="text-[10px] text-zinc-450 dark:text-zinc-500 mt-2 block font-medium">
            Tài khoản học sinh đã kích hoạt.
          </span>
        </motion.div>

        {/* KPI Giáo viên */}
        <motion.div
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-850 p-6 rounded-2xl shadow-sm"
        >
          <span className="text-[10px] font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider block">
            Giáo viên giảng dạy
          </span>
          <div className="text-3xl font-black text-zinc-900 dark:text-white mt-1">
            {analytics?.total_teachers || 0}
          </div>
          <span className="text-[10px] text-zinc-450 dark:text-zinc-500 mt-2 block font-medium">
            Giáo viên phụ trách các lớp học.
          </span>
        </motion.div>

        {/* KPI Lớp học */}
        <motion.div
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-850 p-6 rounded-2xl shadow-sm"
        >
          <span className="text-[10px] font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider block">
            Tổng số lớp học
          </span>
          <div className="text-3xl font-black text-zinc-900 dark:text-white mt-1">
            {analytics?.total_classrooms || 0}
          </div>
          <span className="text-[10px] text-zinc-450 dark:text-zinc-500 mt-2 block font-medium">
            Lớp học đang diễn ra.
          </span>
        </motion.div>

        {/* KPI Lộ trình */}
        <motion.div
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-850 p-6 rounded-2xl shadow-sm"
        >
          <span className="text-[10px] font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider block">
            Mục tiêu đang chạy
          </span>
          <div className="text-3xl font-black text-zinc-900 dark:text-white mt-1">
            {analytics?.total_active_goals || 0}
          </div>
          <span className="text-[10px] text-zinc-450 dark:text-zinc-500 mt-2 block font-medium">
            Lộ trình học tập AI đang hoạt động.
          </span>
        </motion.div>
      </div>

      {/* Phân khu quản lý nhanh */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Card Quản lý User */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm flex flex-col justify-between">
          <div className="space-y-3">
            <h3 className="font-bold text-sm tracking-wide text-zinc-900 dark:text-white uppercase">
              Quản lý người dùng
            </h3>
            <p className="text-xs text-zinc-500 leading-relaxed">
              Kiểm soát tài khoản học sinh, giáo viên và admin. Hỗ trợ tạo mới
              giáo viên, sửa quyền hạn, khóa/mở khóa tài khoản hoặc reset mật
              khẩu.
            </p>
          </div>
          <Link
            href="/admin/users"
            className="mt-6 inline-block w-full py-3.5 bg-zinc-950 hover:bg-zinc-900 dark:bg-zinc-50 dark:hover:bg-zinc-100 text-zinc-50 dark:text-zinc-950 font-bold rounded-xl text-xs text-center transition-all cursor-pointer"
          >
            Quản lý Thành viên
          </Link>
        </div>

        {/* Card Quản lý Lớp học */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm flex flex-col justify-between">
          <div className="space-y-3">
            <h3 className="font-bold text-sm tracking-wide text-zinc-900 dark:text-white uppercase">
              Quản lý lớp học
            </h3>
            <p className="text-xs text-zinc-500 leading-relaxed">
              Theo dõi và kiểm soát toàn bộ danh sách lớp học do giáo viên khởi
              tạo. Giải tán lớp học vi phạm chính sách hoặc hết hạn sử dụng.
            </p>
          </div>
          <Link
            href="/admin/classrooms"
            className="mt-6 inline-block w-full py-3.5 bg-zinc-950 hover:bg-zinc-900 dark:bg-zinc-50 dark:hover:bg-zinc-100 text-zinc-50 dark:text-zinc-950 font-bold rounded-xl text-xs text-center transition-all cursor-pointer"
          >
            Quản lý Lớp học
          </Link>
        </div>

        {/* Card Quản lý Môn học */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm flex flex-col justify-between">
          <div className="space-y-3">
            <h3 className="font-bold text-sm tracking-wide text-zinc-900 dark:text-white uppercase">
              Danh mục môn học
            </h3>
            <p className="text-xs text-zinc-500 leading-relaxed">
              Quản trị hệ thống môn học của trường (Toán, Lý, Hóa, Văn, Anh...).
              Thêm bộ môn mới, cấu hình mã môn học duy nhất phục vụ lộ trình học
              tập AI.
            </p>
          </div>
          <Link
            href="/admin/subjects"
            className="mt-6 inline-block w-full py-3.5 bg-zinc-950 hover:bg-zinc-900 dark:bg-zinc-50 dark:hover:bg-zinc-100 text-zinc-50 dark:text-zinc-950 font-bold rounded-xl text-xs text-center transition-all cursor-pointer"
          >
            Quản lý Môn học
          </Link>
        </div>
      </div>
    </div>
  );
}
