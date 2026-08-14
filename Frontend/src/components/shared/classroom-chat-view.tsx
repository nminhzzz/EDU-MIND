"use client";

import React, { useState, useEffect, useRef } from "react";
import { useAuth } from "@/hooks/use-auth";
import { useClassroomChat } from "@/features/student/hooks/use-classroom-chat";
import { Send, Loader2, Sparkles, Wifi, WifiOff, Users, MessageSquare } from "lucide-react";

interface ClassroomChatViewProps {
  classroomId: number;
}

export function ClassroomChatView({ classroomId }: ClassroomChatViewProps) {
  const { user: currentUser } = useAuth();
  const {
    messages,
    loading,
    connected,
    onlineCount,
    typingUsers,
    sendMessage,
    sendTyping,
  } = useClassroomChat(classroomId);

  const [inputText, setInputText] = useState("");
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading, typingUsers]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = inputText.trim();
    if (!trimmed) return;
    sendMessage(trimmed);
    setInputText("");
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputText(e.target.value);
    sendTyping();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend(e);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full space-y-3 p-6 text-center">
        <Loader2 className="w-8 h-8 text-violet-600 animate-spin" />
        <span className="text-xs font-semibold text-zinc-500">Đang tải lịch sử thảo luận...</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-zinc-50/50 dark:bg-zinc-950/20 text-left">
      {/* 1. Subheader: Connection Status & Online Count */}
      <div className="px-3.5 py-2 bg-white dark:bg-zinc-900 border-b border-zinc-200/80 dark:border-zinc-800 flex items-center justify-between shrink-0 text-xs">
        <div className="flex items-center gap-1.5">
          {connected ? (
            <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded-md">
              <Wifi className="w-3 h-3" />
              Trực tuyến
            </span>
          ) : (
            <span className="flex items-center gap-1 text-[10px] font-bold text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/40 px-2 py-0.5 rounded-md animate-pulse">
              <WifiOff className="w-3 h-3" />
              Kết nối lại...
            </span>
          )}
        </div>

        <div className="flex items-center gap-1 text-[10px] font-bold text-violet-600 dark:text-violet-400 bg-violet-50 dark:bg-violet-950/50 px-2.5 py-0.5 rounded-md border border-violet-100 dark:border-violet-900/30">
          <span className="w-1.5 h-1.5 rounded-md bg-emerald-500 animate-ping inline-block" />
          <Users className="w-3 h-3" />
          <span>{onlineCount > 0 ? `${onlineCount} online` : "Chờ kết nối"}</span>
        </div>
      </div>

      {/* 2. Messages List Workspace */}
      <div className="flex-1 overflow-y-auto p-3.5 space-y-3.5">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-6 text-zinc-400">
            <Sparkles className="w-8 h-8 text-violet-400/60 mb-2" />
            <p className="text-xs font-bold text-zinc-600 dark:text-zinc-300">Chưa có thảo luận nào trong lớp.</p>
            <p className="text-[10px] text-zinc-400 mt-1">Hãy gửi tin nhắn đầu tiên để bắt đầu thảo luận cùng cả lớp!</p>
          </div>
        ) : (
          messages.map((msg) => {
            const isMe = msg.sender_id === currentUser?.id;
            const isTeacher = msg.sender?.role === "teacher";
            
            return (
              <div
                key={msg.id}
                className={`flex items-end gap-2 max-w-[85%] ${isMe ? "ml-auto flex-row-reverse" : "mr-auto"}`}
              >
                {/* Avatar Initial Badge */}
                <div className={`w-7 h-7 rounded-md flex items-center justify-center font-bold text-[10px] shrink-0 shadow-xs ${
                  isMe 
                    ? "bg-violet-600 text-white" 
                    : isTeacher 
                    ? "bg-violet-100 dark:bg-violet-950/50 text-violet-700 dark:text-violet-300 border border-violet-200 dark:border-violet-800" 
                    : "bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300"
                }`}>
                  {msg.sender?.full_name ? msg.sender.full_name.charAt(0).toUpperCase() : "U"}
                </div>

                <div className="space-y-1 max-w-full min-w-0">
                  {/* Sender Name & Role (Only shown for others) */}
                  {!isMe && (
                    <div className="flex items-center gap-1.5 px-0.5">
                      <span className="text-[10px] font-bold text-zinc-700 dark:text-zinc-300 truncate">
                        {msg.sender?.full_name || "Thành viên"}
                      </span>
                      {isTeacher && (
                        <span className="text-[8px] font-black uppercase tracking-wider bg-violet-600 text-white px-1.5 py-0.5 rounded-md leading-none">
                          Giáo viên
                        </span>
                      )}
                    </div>
                  )}

                  {/* Bubble Chat Content */}
                  <div className={`px-3.5 py-2.5 rounded-md text-xs leading-relaxed break-words font-medium shadow-xs ${
                    isMe
                      ? "bg-violet-600 text-white rounded-br-xs"
                      : isTeacher
                      ? "bg-violet-50 dark:bg-violet-950/40 border border-violet-100 dark:border-violet-900/40 text-zinc-900 dark:text-zinc-100 rounded-bl-xs"
                      : "bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 text-zinc-900 dark:text-zinc-100 rounded-bl-xs"
                  }`}>
                    {msg.content}
                  </div>

                  {/* Time Stamp */}
                  <span className={`block text-[9px] text-zinc-400 px-1 ${isMe ? "text-right" : "text-left"}`}>
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

        {/* Typing indicator */}
        {typingUsers.length > 0 && (
          <div className="flex items-center gap-2 text-[10px] text-violet-600 dark:text-violet-400 font-semibold italic animate-pulse px-1">
            <MessageSquare className="w-3 h-3 animate-bounce" />
            <span>{typingUsers.join(", ")} đang gõ...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 3. Message Input Composer Form */}
      <form onSubmit={handleSend} className="p-2.5 bg-white dark:bg-zinc-900 border-t border-zinc-200/80 dark:border-zinc-800 flex items-center gap-2 shrink-0">
        <textarea
          rows={1}
          value={inputText}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Nhập nội dung thảo luận với lớp..."
          className="flex-1 max-h-24 min-h-[38px] px-3 py-2 text-xs bg-zinc-100 dark:bg-zinc-800/80 border border-transparent focus:border-violet-500 rounded-md focus:outline-none resize-none font-medium text-zinc-800 dark:text-zinc-100"
        />
        <button
          type="submit"
          disabled={!inputText.trim()}
          className="w-9 h-9 rounded-md bg-violet-600 hover:bg-violet-500 active:scale-95 text-white flex items-center justify-center shrink-0 disabled:opacity-40 transition-all shadow-sm shadow-violet-600/20 cursor-pointer"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
