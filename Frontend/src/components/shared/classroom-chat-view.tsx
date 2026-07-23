"use client";

import React, { useState, useEffect, useRef } from "react";
import { useAuth } from "@/hooks/use-auth";
import { useClassroomChat } from "@/features/student/hooks/use-classroom-chat";
import { Send, Loader2, Sparkles, AlertCircle, Wifi, WifiOff } from "lucide-react";

interface ClassroomChatViewProps {
  classroomId: number;
}

export function ClassroomChatView({ classroomId }: ClassroomChatViewProps) {
  const { user: currentUser } = useAuth();
  const { messages, loading, connected, sendMessage } = useClassroomChat(classroomId);
  const [inputText, setInputText] = useState("");
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Auto-scroll to the bottom of the chat container
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = inputText.trim();
    if (!trimmed) return;
    sendMessage(trimmed);
    setInputText("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend(e);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[350px] space-y-3">
        <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
        <span className="text-xs font-semibold text-zinc-500">Đang tải lịch sử thảo luận...</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[480px] bg-zinc-50/50 dark:bg-zinc-950/20 border border-zinc-200 dark:border-zinc-800 rounded-2xl overflow-hidden text-left">
      {/* 1. Header Bar: Connection Status indicator */}
      <div className="px-4 py-2.5 bg-white dark:bg-zinc-900 border-b border-zinc-150 dark:border-zinc-800/80 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-zinc-700 dark:text-zinc-200">Phòng thảo luận lớp</span>
          {connected ? (
            <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded-full shrink-0">
              <Wifi className="w-3 h-3" />
              Kết nối trực tuyến
            </span>
          ) : (
            <span className="flex items-center gap-1 text-[10px] font-bold text-amber-600 bg-amber-50 dark:bg-amber-950/40 px-2 py-0.5 rounded-full shrink-0 animate-pulse">
              <WifiOff className="w-3 h-3" />
              Đang kết nối lại...
            </span>
          )}
        </div>
      </div>

      {/* 2. Messages List Workspace */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-6 text-zinc-400">
            <Sparkles className="w-8 h-8 text-zinc-300 mb-2" />
            <p className="text-xs font-bold">Chưa có cuộc hội thoại nào.</p>
            <p className="text-[10px] text-zinc-400 mt-1">Hãy gửi tin nhắn đầu tiên để bắt đầu thảo luận cùng cả lớp!</p>
          </div>
        ) : (
          messages.map((msg) => {
            const isMe = msg.sender_id === currentUser?.id;
            const isTeacher = msg.sender?.role === "teacher";
            
            return (
              <div
                key={msg.id}
                className={`flex gap-3 max-w-[85%] ${isMe ? "ml-auto flex-row-reverse" : "mr-auto"}`}
              >
                {/* Avatar Initial Badge */}
                <div className={`w-8 h-8 rounded-xl flex items-center justify-center font-bold text-[10px] shrink-0 shadow-sm ${
                  isMe 
                    ? "bg-indigo-600 text-white" 
                    : isTeacher 
                    ? "bg-violet-100 dark:bg-violet-950/50 text-violet-650 dark:text-violet-400 border border-violet-200/50 dark:border-violet-900/30" 
                    : "bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-zinc-650 dark:text-zinc-300"
                }`}>
                  {msg.sender?.full_name ? msg.sender.full_name.charAt(0).toUpperCase() : "U"}
                </div>

                <div className="space-y-1">
                  {/* Sender Details */}
                  {!isMe && (
                    <div className="flex items-center gap-1.5 px-0.5">
                      <span className="text-[10px] font-black text-zinc-700 dark:text-zinc-200">
                        {msg.sender?.full_name || "Thành viên"}
                      </span>
                      {isTeacher && (
                        <span className="text-[8px] font-black uppercase tracking-wider bg-violet-600 text-white px-1.5 py-0.5 rounded-md leading-none scale-[0.9]">
                          Giáo viên
                        </span>
                      )}
                    </div>
                  )}

                  {/* Bubble Chat content */}
                  <div className={`p-3 rounded-2xl text-xs leading-relaxed break-words font-medium shadow-sm border ${
                    isMe
                      ? "bg-indigo-600 text-white border-indigo-500 rounded-tr-none"
                      : isTeacher
                      ? "bg-violet-50/50 dark:bg-violet-950/20 border-violet-100 dark:border-violet-900/30 text-zinc-850 dark:text-zinc-150 rounded-tl-none"
                      : "bg-white dark:bg-zinc-900 border-zinc-150 dark:border-zinc-800 text-zinc-800 dark:text-zinc-200 rounded-tl-none"
                  }`}>
                    {msg.content}
                  </div>

                  {/* Time Stamp */}
                  <span className={`block text-[8px] text-zinc-400 px-1 ${isMe ? "text-right" : "text-left"}`}>
                    {new Date(msg.created_at).toLocaleTimeString("vi-VN", {
                      hour: "2-digit",
                      minute: "2-digit"
                    })}
                  </span>
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 3. Message Input Composer Form */}
      <form onSubmit={handleSend} className="p-3 bg-white dark:bg-zinc-900 border-t border-zinc-150 dark:border-zinc-800/80 flex items-end gap-2 shrink-0">
        <textarea
          rows={1}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Nhập nội dung thảo luận với lớp học..."
          className="flex-1 max-h-24 min-h-[38px] p-2.5 text-xs bg-zinc-50 dark:bg-zinc-950/40 border border-zinc-200 dark:border-zinc-800 rounded-xl focus:outline-none focus:ring-1 focus:ring-indigo-500 resize-none font-medium text-zinc-800 dark:text-zinc-100"
        />
        <button
          type="submit"
          disabled={!inputText.trim()}
          className="w-9 h-9 rounded-xl bg-indigo-650 hover:bg-indigo-600 active:bg-indigo-700 text-white flex items-center justify-center shrink-0 disabled:opacity-50 transition-colors shadow-md shadow-indigo-650/10 cursor-pointer"
        >
          <Send className="w-4.5 h-4.5" />
        </button>
      </form>
    </div>
  );
}
