"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AdminUser } from "@/types/admin";

interface UserModalProps {
  isOpen: boolean;
  onClose: () => void;
  editingUser: AdminUser | null;
  onSubmit: (payload: any) => Promise<void>;
  formLoading: boolean;
}

export function UserModal({ isOpen, onClose, editingUser, onSubmit, formLoading }: UserModalProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState("student");
  const [grade, setGrade] = useState("");
  const [isActive, setIsActive] = useState(true);

  // Đồng bộ hóa form fields khi mở/chuyển đổi modal
  useEffect(() => {
    if (isOpen) {
      if (editingUser) {
        setEmail(editingUser.email);
        setPassword("");
        setFullName(editingUser.full_name || "");
        setRole(editingUser.role);
        setGrade(editingUser.grade || "");
        setIsActive(editingUser.is_active);
      } else {
        setEmail("");
        setPassword("");
        setFullName("");
        setRole("student");
        setGrade("");
        setIsActive(true);
      }
    }
  }, [isOpen, editingUser]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload: Record<string, any> = {
      email,
      full_name: fullName || null,
      role,
      grade: role === "student" ? (grade || null) : null,
      is_active: isActive,
    };
    if (password) payload.password = password;
    onSubmit(payload);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-black"
          />

          {/* Modal Body */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-xl w-full max-w-md p-6 z-10 text-left relative"
          >
            <h3 className="text-sm font-black uppercase text-zinc-900 dark:text-white border-b border-zinc-200 dark:border-zinc-800 pb-3 mb-4">
              {editingUser ? "CHỈNH SỬA THÀNH VIÊN" : "THÊM THÀNH VIÊN MỚI"}
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Email */}
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-zinc-400 uppercase">Email:</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-bold focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white text-xs"
                />
              </div>

              {/* Password */}
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-zinc-400 uppercase">
                  Mật khẩu {editingUser && "(Để trống nếu không muốn đổi)"}:
                </label>
                <input
                  type="password"
                  required={!editingUser}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-3 py-2 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-bold focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white text-xs"
                />
              </div>

              {/* Full name */}
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-zinc-400 uppercase">Họ và tên:</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full px-3 py-2 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-bold focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white text-xs"
                />
              </div>

              {/* Role */}
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-zinc-400 uppercase">Vai trò:</label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full px-3 py-2 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-bold focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white text-xs cursor-pointer"
                >
                  <option value="student">Học sinh (Student)</option>
                  <option value="teacher">Giáo viên (Teacher)</option>
                  <option value="admin">Quản trị viên (Admin)</option>
                </select>
              </div>

              {/* Grade (If student) */}
              {role === "student" && (
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-zinc-400 uppercase">Khối lớp học:</label>
                  <select
                    value={grade}
                    onChange={(e) => setGrade(e.target.value)}
                    className="w-full px-3 py-2 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-bold focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white text-xs cursor-pointer"
                  >
                    <option value="">Chưa cấu hình</option>
                    <option value="grade_6">Lớp 6</option>
                    <option value="grade_7">Lớp 7</option>
                    <option value="grade_8">Lớp 8</option>
                    <option value="grade_9">Lớp 9</option>
                    <option value="grade_10">Lớp 10</option>
                    <option value="grade_11">Lớp 11</option>
                    <option value="grade_12">Lớp 12</option>
                    <option value="uni_year_1">Sinh viên năm 1</option>
                    <option value="uni_year_2">Sinh viên năm 2</option>
                    <option value="uni_year_3">Sinh viên năm 3</option>
                    <option value="uni_year_4">Sinh viên năm 4</option>
                  </select>
                </div>
              )}

              {/* Active Status (Only when editing) */}
              {editingUser && (
                <div className="flex items-center gap-3 pt-2">
                  <input
                    type="checkbox"
                    id="isActiveCheckbox"
                    checked={isActive}
                    onChange={(e) => setIsActive(e.target.checked)}
                    className="w-4 h-4 rounded text-indigo-600 border-zinc-300 focus:ring-indigo-500"
                  />
                  <label
                    htmlFor="isActiveCheckbox"
                    className="text-xs font-bold text-zinc-600 dark:text-zinc-400 cursor-pointer"
                  >
                    Tài khoản hoạt động bình thường (Mở khóa)
                  </label>
                </div>
              )}

              {/* Buttons */}
              <div className="pt-4 border-t border-zinc-200 dark:border-zinc-800 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 border border-zinc-200 dark:border-zinc-800 rounded-xl text-xs font-bold text-zinc-650 hover:bg-zinc-50 cursor-pointer"
                >
                  Hủy bỏ
                </button>
                <button
                  type="submit"
                  disabled={formLoading}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all disabled:opacity-50 cursor-pointer"
                >
                  {formLoading ? "Đang xử lý..." : editingUser ? "Cập nhật" : "Tạo mới"}
                </button>

              </div>
            </form>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
