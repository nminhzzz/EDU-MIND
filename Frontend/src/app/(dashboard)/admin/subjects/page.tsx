"use client";

import React, { useEffect, useState } from "react";
import { apiClient } from "@/services/api-client";
import { parseApiError } from "@/utils/api-error";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { Subject } from "@/types/subject";
import { ADMIN_ACCESS_DENIED } from "@/constants/admin";
import { useAdminAccess } from "@/hooks/use-admin-access";

export default function AdminSubjectsPage() {
  const { isLoading, denied } = useAdminAccess();

  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingSubject, setEditingSubject] = useState<Subject | null>(null);

  // Form Fields
  const [name, setName] = useState("");
  const [code, setCode] = useState("");
  const [description, setDescription] = useState("");
  const [formLoading, setFormLoading] = useState(false);

  const [searchQuery, setSearchQuery] = useState("");

  const fetchSubjects = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get<Subject[]>("/subjects/");
      setSubjects(res.data);
    } catch (err: unknown) {
      console.error("Lỗi tải môn học:", err);
      setError(parseApiError(err, "Không thể tải danh sách môn học từ hệ thống."));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isLoading) return;

    if (denied) {
      setError(ADMIN_ACCESS_DENIED);
      setLoading(false);
      return;
    }

    fetchSubjects();
  }, [isLoading, denied]);

  const handleOpenAddModal = () => {
    setEditingSubject(null);
    setName("");
    setCode("");
    setDescription("");
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (s: Subject) => {
    setEditingSubject(s);
    setName(s.name);
    setCode(s.code);
    setDescription(s.description || "");
    setIsModalOpen(true);
  };

  const handleSubmitForm = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormLoading(true);

    try {
      const payload = {
        name,
        code: code.toUpperCase().trim(),
        description: description || null,
      };

      if (editingSubject) {
        await apiClient.patch(`/subjects/${editingSubject.id}`, payload);
        toast.success("Cập nhật thông tin môn học thành công!");
      } else {
        await apiClient.post("/subjects/", payload);
        toast.success("Thêm môn học mới thành công!");
      }
      setIsModalOpen(false);
      fetchSubjects();
    } catch (err: unknown) {
      toast.error(parseApiError(err, "Thao tác thất bại."));
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteSubject = async (s: Subject) => {
    if (
      !confirm(
        `Bạn có chắc chắn muốn xóa môn học "${s.name}" (${s.code})? Hành động này không thể hoàn tác!`,
      )
    )
      return;

    try {
      await apiClient.delete(`/subjects/${s.id}`);
      toast.success("Đã xóa môn học thành công.");
      fetchSubjects();
    } catch (err: unknown) {
      toast.error(parseApiError(err, "Không thể xóa môn học này."));
    }
  };

  const filteredSubjects = subjects.filter((s) => {
    const query = searchQuery.toLowerCase().trim();
    if (!query) return true;
    return (
      s.name.toLowerCase().includes(query) ||
      s.code.toLowerCase().includes(query)
    );
  });

  if (isLoading || loading) {
    return (
      <div className="py-24 text-center space-y-4">
        <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400 font-mono">
          Đang tải danh mục môn học...
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
          <h1 className="text-2xl font-black text-zinc-900 dark:text-white tracking-tight animate-fade-in">
            DANH MỤC MÔN HỌC
          </h1>
        </div>

        <button
          onClick={handleOpenAddModal}
          className="px-5 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold text-xs tracking-wider transition-all shadow-lg shadow-indigo-500/15 cursor-pointer flex items-center justify-center"
        >
          Tạo môn học mới +
        </button>
      </div>

      {/* Thanh công cụ tìm kiếm */}
      <div className="flex flex-col md:flex-row gap-4 p-4 border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 rounded-2xl">
        <input
          type="text"
          placeholder="Tìm tên môn học hoặc mã môn học (code)..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 px-4 py-2.5 text-xs border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white font-medium"
        />

        <Link
          href="/admin"
          className="px-6 py-2.5 border border-zinc-300 dark:border-zinc-700 hover:border-zinc-900 dark:hover:border-zinc-100 text-zinc-650 dark:text-zinc-350 hover:text-zinc-900 dark:hover:text-white text-xs font-bold rounded-xl flex items-center justify-center"
        >
          Quay lại Dashboard
        </Link>
      </div>

      {/* Bảng danh sách môn học */}
      <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead>
              <tr className="border-b border-zinc-250 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-950/20 text-zinc-500 uppercase font-extrabold tracking-wider">
                <th className="px-6 py-4">Mã môn</th>
                <th className="px-6 py-4">Tên môn học</th>
                <th className="px-6 py-4">Mô tả</th>
                <th className="px-6 py-4">Ngày tạo</th>
                <th className="px-6 py-4 text-right">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
              {filteredSubjects.length === 0 ? (
                <tr>
                  <td
                    colSpan={5}
                    className="py-12 text-center text-zinc-400 font-mono"
                  >
                    Không tìm thấy môn học nào.
                  </td>
                </tr>
              ) : (
                filteredSubjects.map((s) => (
                  <tr
                    key={s.id}
                    className="hover:bg-zinc-50/40 dark:hover:bg-zinc-950/10 transition-colors font-medium"
                  >
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-1 bg-zinc-100 dark:bg-zinc-800 text-zinc-850 dark:text-zinc-200 rounded-lg font-mono font-bold border border-zinc-200 dark:border-zinc-700">
                        {s.code}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-extrabold text-zinc-900 dark:text-white">
                        {s.name}
                      </div>
                    </td>
                    <td className="px-6 py-4 max-w-sm truncate text-zinc-500 dark:text-zinc-400">
                      {s.description || "--"}
                    </td>
                    <td className="px-6 py-4 text-zinc-400 dark:text-zinc-500 font-mono text-[10px]">
                      {new Date(s.created_at).toLocaleDateString("vi-VN")}
                    </td>
                    <td className="px-6 py-4 text-right space-x-3">
                      <button
                        onClick={() => handleOpenEditModal(s)}
                        className="text-indigo-600 dark:text-indigo-450 hover:underline font-bold cursor-pointer"
                      >
                        Sửa
                      </button>
                      <button
                        onClick={() => handleDeleteSubject(s)}
                        className="text-red-600 dark:text-red-450 hover:underline font-bold cursor-pointer"
                      >
                        Xóa
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* MODAL THÊM / SỬA MÔN HỌC */}
      <AnimatePresence>
        {isModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.5 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsModalOpen(false)}
              className="absolute inset-0 bg-black"
            />

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-xl w-full max-w-md p-6 z-10 text-left relative"
            >
              <h3 className="text-sm font-black uppercase text-zinc-900 dark:text-white border-b border-zinc-200 dark:border-zinc-800 pb-3 mb-4">
                {editingSubject ? "CẬP NHẬT MÔN HỌC" : "THÊM MÔN HỌC MỚI"}
              </h3>

              <form onSubmit={handleSubmitForm} className="space-y-4">
                {/* Code */}
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-zinc-400 uppercase">
                    Mã môn học (Code):
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="Ví dụ: MATH10, PHYS11, ENG12..."
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    disabled={!!editingSubject} // Không cho phép đổi mã môn khi chỉnh sửa
                    className="w-full px-3 py-2 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-bold focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white text-xs font-mono uppercase disabled:opacity-50"
                  />
                </div>

                {/* Name */}
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-zinc-400 uppercase">
                    Tên môn học:
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="Ví dụ: Toán Đại Số lớp 10, Vật Lý 11..."
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full px-3 py-2 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-bold focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white text-xs"
                  />
                </div>

                {/* Description */}
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-zinc-400 uppercase">
                    Mô tả chi tiết:
                  </label>
                  <textarea
                    rows={3}
                    placeholder="Nhập mô tả tóm tắt nội dung học tập..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="w-full px-3 py-2 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-medium focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white text-xs"
                  />
                </div>

                {/* Buttons */}
                <div className="pt-4 border-t border-zinc-200 dark:border-zinc-800 flex justify-end gap-3">
                  <button
                    type="button"
                    onClick={() => setIsModalOpen(false)}
                    className="px-4 py-2 border border-zinc-200 dark:border-zinc-800 rounded-xl text-xs font-bold text-zinc-650 hover:bg-zinc-50 cursor-pointer"
                  >
                    Hủy bỏ
                  </button>
                  <button
                    type="submit"
                    disabled={formLoading}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all disabled:opacity-50 cursor-pointer"
                  >
                    {formLoading
                      ? "Đang xử lý..."
                      : editingSubject
                        ? "Cập nhật"
                        : "Tạo mới"}
                  </button>

                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
