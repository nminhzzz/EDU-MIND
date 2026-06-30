"use client";

import React from "react";
import { MessageSquare, Plus, Trash2 } from "lucide-react";

interface ChatSession {
  session_id: string;
  title: string;
  subject_id: number;
  created_at: string;
}

interface ChatSidebarProps {
  sessions: ChatSession[];
  activeSession: ChatSession | null;
  onSelectSession: (session: ChatSession) => void;
  onDeleteSession: (sessionId: string) => void;
  onNewChatClick: () => void;
  loading: boolean;
}

export function ChatSidebar({
  sessions,
  activeSession,
  onSelectSession,
  onDeleteSession,
  onNewChatClick,
  loading,
}: ChatSidebarProps) {
  return (
    <div className="w-80 border-r border-zinc-200/80 dark:border-zinc-800 flex flex-col justify-between bg-zinc-50/50 dark:bg-zinc-900/10 h-full text-left">
      <div className="p-4 border-b border-zinc-200/80 dark:border-zinc-800 flex items-center justify-between">
        <h2 className="font-extrabold text-sm text-zinc-900 dark:text-white">Lịch sử thảo luận</h2>
        <button
          onClick={onNewChatClick}
          className="p-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl shadow-sm transition-all active:scale-95 cursor-pointer"
          title="Cuộc trò chuyện mới"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-1.5">
        {loading ? (
          <div className="py-8 text-center text-xs font-mono text-zinc-400">Đang tải lịch sử...</div>
        ) : sessions.length === 0 ? (
          <div className="py-12 text-center text-xs text-zinc-400 dark:text-zinc-500 font-medium">
            Chưa có phiên hội thoại nào.
          </div>
        ) : (
          sessions.map((s) => {
            const isActive = activeSession?.session_id === s.session_id;
            return (
              <div
                key={s.session_id}
                className={`group w-full flex items-center justify-between p-1 rounded-xl transition-all ${
                  isActive
                    ? "bg-indigo-50/60 dark:bg-indigo-950/20 border border-indigo-100/50 dark:border-zinc-800"
                    : "hover:bg-zinc-100/60 dark:hover:bg-zinc-900/30 border border-transparent"
                }`}
              >
                <button
                  onClick={() => onSelectSession(s)}
                  className={`flex-1 flex items-center gap-3 p-2 text-left text-xs font-bold ${
                    isActive ? "text-indigo-600 dark:text-indigo-400" : "text-zinc-650 dark:text-zinc-400"
                  } truncate`}
                >
                  <MessageSquare className="w-4 h-4 shrink-0 text-zinc-400" />
                  <span className="truncate">{s.title}</span>
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(s.session_id);
                  }}
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-2 text-zinc-400 hover:text-red-500 rounded-lg hover:bg-red-50 dark:hover:bg-red-950/30 shrink-0 cursor-pointer"
                  title="Xóa phiên thảo luận"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
