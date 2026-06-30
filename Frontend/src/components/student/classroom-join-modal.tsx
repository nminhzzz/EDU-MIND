"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import { toast } from "sonner";
import { apiClient } from "@/services/api-client";

interface ClassroomJoinModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function ClassroomJoinModal({ isOpen, onClose, onSuccess }: ClassroomJoinModalProps) {
  const [classCode, setClassCode] = useState("");
  const [joining, setJoining] = useState(false);

  const handleJoinClass = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!classCode.trim()) {
      toast.error("Vui lòng điền mã lớp học.");
      return;
    }
    setJoining(true);
    try {
      await apiClient.post("/classrooms/join", { class_code: classCode.trim() });
      toast.success("Tham gia lớp học thành công!");
      setClassCode("");
      onSuccess();
      onClose();
    } catch (err: any) {
      const errMsg = err?.response?.data?.detail || "Gia nhập lớp học thất bại.";
      toast.error(errMsg);
    } finally {
      setJoining(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black z-45"
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-2xl w-full max-w-md p-8 text-left">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-black text-zinc-900 dark:text-white">Gia nhập lớp học mới</h2>
                <button
                  onClick={onClose}
                  className="p-2 rounded-lg text-zinc-400 hover:text-zinc-650 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleJoinClass} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-zinc-550 dark:text-zinc-400 uppercase tracking-wider mb-2">
                    Mã lớp học (Do giáo viên cung cấp) *
                  </label>
                  <input
                    type="text"
                    value={classCode}
                    onChange={(e) => setClassCode(e.target.value.toUpperCase())}
                    placeholder="VD: CLASS-TEST243"
                    className="w-full px-4 py-3 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-850 text-zinc-900 dark:text-white font-mono text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none uppercase"
                  />
                </div>
                <button
                  type="submit"
                  disabled={joining}
                  className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold text-sm rounded-xl shadow-md transition-all active:scale-[0.98] cursor-pointer"
                >
                  {joining ? "Đang xử lý..." : "Xác nhận gia nhập"}
                </button>
              </form>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
