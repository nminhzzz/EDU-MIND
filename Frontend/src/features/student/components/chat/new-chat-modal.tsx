"use client";

import React from "react";
import type { Subject } from "@/features/student/types";
import { ChatSession } from "@/features/student/types/chat";
import { StudentModal } from "@/features/student/components/common/student-modal";
import { useNewChatSession } from "@/features/student/hooks/use-new-chat-session";

interface NewChatModalProps {
  isOpen: boolean;
  onClose: () => void;
  subjects: Subject[];
  onCreated: (session: ChatSession) => void;
}

export function NewChatModal({ isOpen, onClose, subjects, onCreated }: NewChatModalProps) {
  const { subjectId, setSubjectId, title, setTitle, creating, handleCreateSession } =
    useNewChatSession(subjects, onCreated, onClose);

  return (
    <StudentModal
      isOpen={isOpen}
      onClose={onClose}
      title="Tạo cuộc thảo luận AI mới"
    >
      <form onSubmit={handleCreateSession} className="space-y-4">
        <div>
          <label className="block text-xs font-bold text-zinc-550 dark:text-zinc-400 uppercase tracking-wider mb-2">
            Môn học thảo luận *
          </label>
          <select
            value={subjectId}
            onChange={(e) => setSubjectId(e.target.value)}
            className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-850 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
          >
            <option value="">-- Chọn môn học --</option>
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name} ({s.code})
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-bold text-zinc-555 dark:text-zinc-400 uppercase tracking-wider mb-2">
            Tiêu đề cuộc trò chuyện
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="VD: Thảo luận Lý thuyết hàm số (Để trống để tự tạo)"
            className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-850 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
          />
        </div>
        <button
          type="submit"
          disabled={creating}
          className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold text-sm rounded-xl shadow-md transition-all active:scale-[0.98] cursor-pointer"
        >
          {creating ? "Đang khởi tạo..." : "Bắt đầu thảo luận"}
        </button>
      </form>
    </StudentModal>
  );
}
