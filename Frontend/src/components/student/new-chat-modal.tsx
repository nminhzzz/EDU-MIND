"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import { toast } from "sonner";
import { apiClient } from "@/services/api-client";

interface Subject {
  id: number;
  name: string;
  code: string;
}

interface NewChatModalProps {
  isOpen: boolean;
  onClose: () => void;
  subjects: Subject[];
  onCreated: (session: { session_id: string; title: string; subject_id: number; created_at: string }) => void;
}

export function NewChatModal({ isOpen, onClose, subjects, onCreated }: NewChatModalProps) {
  const [newChatSubject, setNewChatSubject] = useState("");
  const [newChatTitle, setNewChatTitle] = useState("");
  const [creatingSession, setCreatingSession] = useState(false);

  const handleCreateSession = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newChatSubject) {
      toast.error("Vui lòng chọn môn học.");
      return;
    }
    setCreatingSession(true);
    try {
      const selectedSubj = subjects.find(s => s.id === parseInt(newChatSubject));
      const payload = {
        subject_id: parseInt(newChatSubject),
        title: newChatTitle.trim() || `Trò chuyện môn ${selectedSubj?.name || ""}`,
      };

      const res = await apiClient.post<string>("/chat/tutor/session", payload);
      const newSessionId = res.data;

      const newSessionObj = {
        session_id: newSessionId,
        title: payload.title,
        subject_id: payload.subject_id,
        created_at: new Date().toISOString(),
      };

      toast.success("Đã mở cuộc thảo luận mới cùng Gia sư AI!");
      onCreated(newSessionObj);
      setNewChatSubject("");
      setNewChatTitle("");
      onClose();
    } catch (err: any) {
      toast.error("Khởi tạo phiên trò chuyện thất bại.");
    } finally {
      setCreatingSession(false);
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
                <h2 className="text-xl font-black text-zinc-900 dark:text-white">Tạo cuộc thảo luận AI mới</h2>
                <button
                  onClick={onClose}
                  className="p-2 rounded-lg text-zinc-400 hover:text-zinc-650 dark:hover:text-white hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleCreateSession} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-zinc-550 dark:text-zinc-400 uppercase tracking-wider mb-2">Môn học thảo luận *</label>
                  <select
                    value={newChatSubject}
                    onChange={(e) => setNewChatSubject(e.target.value)}
                    className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-850 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  >
                    <option value="">-- Chọn môn học --</option>
                    {subjects.map((s) => (
                      <option key={s.id} value={s.id}>{s.name} ({s.code})</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-bold text-zinc-555 dark:text-zinc-400 uppercase tracking-wider mb-2">Tiêu đề cuộc trò chuyện</label>
                  <input
                    type="text"
                    value={newChatTitle}
                    onChange={(e) => setNewChatTitle(e.target.value)}
                    placeholder="VD: Thảo luận Lý thuyết hàm số (Để trống để tự tạo)"
                    className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-850 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  />
                </div>
                <button
                  type="submit"
                  disabled={creatingSession}
                  className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold text-sm rounded-xl shadow-md transition-all active:scale-[0.98] cursor-pointer"
                >
                  {creatingSession ? "Đang khởi tạo..." : "Bắt đầu thảo luận"}
                </button>
              </form>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
