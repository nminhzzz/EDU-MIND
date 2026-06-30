"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { useRouter } from "next/navigation";
import { apiClient } from "@/services/api-client";
import { toast } from "sonner";
import { motion } from "framer-motion";
import Link from "next/link";

interface Classroom {
  id: number;
  teacher_id: number;
  subject_id: number;
  class_name: string;
  class_code: string;
  description: string | null;
  created_at: string;
}

export default function AdminClassroomsPage() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  const [classrooms, setClassrooms] = useState<Classroom[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [searchQuery, setSearchQuery] = useState("");

  const fetchClassrooms = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get<Classroom[]>("/classrooms/admin/all");
      setClassrooms(res.data);
    } catch (err: any) {
      console.error("Lỗi tải lớp học:", err);
      setError("Không thể tải danh sách lớp học từ hệ thống.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) {
        router.push("/login");
        return;
      }
      if (user?.role !== "admin") {
        setError("Bạn không có quyền truy cập trang quản trị này.");
        setLoading(false);
        return;
      }
      fetchClassrooms();
    }
  }, [isLoading, isAuthenticated, user, router]);

  const handleDeleteClassroom = async (c: Classroom) => {
    if (
      !confirm(
        `Bạn có chắc chắn muốn giải tán lớp học "${c.class_name}" (${c.class_code})? Học sinh trong lớp sẽ bị rời khỏi lớp học này!`,
      )
    )
      return;

    try {
      await apiClient.delete(`/classrooms/${c.id}`);
      toast.success("Giải tán lớp học thành công!");
      fetchClassrooms();
    } catch (err) {
      toast.error("Không thể giải tán lớp học này.");
    }
  };

  const filteredClassrooms = classrooms.filter((c) => {
    const query = searchQuery.toLowerCase().trim();
    if (!query) return true;
    return (
      c.class_name.toLowerCase().includes(query) ||
      c.class_code.toLowerCase().includes(query)
    );
  });

  if (isLoading || loading) {
    return (
      <div className="py-24 text-center space-y-4">
        <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400 font-mono">
          Đang tải danh sách lớp học...
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
    <div className="space-y-6 text-left">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-sans font-bold tracking-wider text-indigo-600 dark:text-indigo-400 block uppercase">
            Phân hệ Quản lý
          </span>
          <h1 className="text-2xl font-black text-zinc-900 dark:text-white tracking-tight">
            QUẢN LÝ LỚP HỌC
          </h1>
        </div>

        <Link
          href="/admin"
          className="px-6 py-3 bg-zinc-950 hover:bg-zinc-900 dark:bg-zinc-50 dark:hover:bg-zinc-100 text-zinc-50 dark:text-zinc-950 font-bold rounded-xl text-xs text-center transition-all cursor-pointer"
        >
          Quay lại Dashboard
        </Link>
      </div>

      {/* Thanh công cụ tìm kiếm */}
      <div className="flex flex-col md:flex-row gap-4 p-4 border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 rounded-2xl">
        <input
          type="text"
          placeholder="Tìm tên lớp học hoặc mã lớp học (class code)..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 px-4 py-2.5 text-xs border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white font-medium"
        />
      </div>

      {/* Bảng danh sách lớp học */}
      <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead>
              <tr className="border-b border-zinc-250 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/20 text-zinc-500 uppercase font-extrabold tracking-wider">
                <th className="px-6 py-4">Mã lớp</th>
                <th className="px-6 py-4">Tên lớp học</th>
                <th className="px-6 py-4">ID Giáo viên</th>
                <th className="px-6 py-4">Mô tả</th>
                <th className="px-6 py-4">Ngày mở lớp</th>
                <th className="px-6 py-4 text-right">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
              {filteredClassrooms.length === 0 ? (
                <tr>
                  <td
                    colSpan={6}
                    className="py-12 text-center text-zinc-400 font-mono"
                  >
                    Không tìm thấy lớp học nào trên hệ thống.
                  </td>
                </tr>
              ) : (
                filteredClassrooms.map((c) => (
                  <tr
                    key={c.id}
                    className="hover:bg-zinc-50/40 dark:hover:bg-zinc-950/10 transition-colors font-medium"
                  >
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-1 bg-zinc-100 dark:bg-zinc-800 text-zinc-850 dark:text-zinc-200 rounded-lg font-mono font-bold border border-zinc-200 dark:border-zinc-700">
                        {c.class_code}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-extrabold text-zinc-900 dark:text-white">
                        {c.class_name}
                      </div>
                    </td>
                    <td className="px-6 py-4 font-mono text-zinc-500">
                      ID: {c.teacher_id}
                    </td>
                    <td className="px-6 py-4 max-w-xs truncate text-zinc-500 dark:text-zinc-400">
                      {c.description || "--"}
                    </td>
                    <td className="px-6 py-4 text-zinc-400 dark:text-zinc-500 font-mono text-[10px]">
                      {new Date(c.created_at).toLocaleDateString("vi-VN")}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => handleDeleteClassroom(c)}
                        className="text-red-600 dark:text-red-450 hover:underline font-bold cursor-pointer"
                      >
                        Giải tán lớp
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
