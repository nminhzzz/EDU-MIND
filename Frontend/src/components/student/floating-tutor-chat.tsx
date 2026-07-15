"use client";

import React, { useState, useEffect, useRef } from "react";
import { 
  MessageSquare, 
  X, 
  Send, 
  Bot, 
  User, 
  Loader2, 
  Plus, 
  History, 
  ChevronLeft, 
  Trash2 
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useChat } from "@/features/student/hooks/use-chat";
import { useNewChatSession } from "@/features/student/hooks/use-new-chat-session";
import { MarkdownText } from "@/components/student/markdown-text";
import { ChatSession } from "@/features/student/types/chat";

export function FloatingTutorChat() {
  const [isOpen, setIsOpen] = useState(false);
  const [showSessionsList, setShowSessionsList] = useState(false);
  const [showNewChatForm, setShowNewChatForm] = useState(false);
  
  const chat = useChat();
  const [subjectId, setSubjectId] = useState("");
  const [newTitle, setNewTitle] = useState("");
  const [creating, setCreating] = useState(false);

  const getSubjectName = (subId: number) => {
    const sub = chat.subjects.find((s) => s.id === subId);
    return sub ? sub.name : `Môn học #${subId}`;
  };

  const handleSessionCreated = (session: ChatSession) => {
    chat.handleSessionCreated(session);
    setShowNewChatForm(false);
    setShowSessionsList(false);
  };

  const handleCreateSession = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subjectId) return;
    setCreating(true);
    try {
      const selectedSub = chat.subjects.find((s) => s.id === Number(subjectId));
      const subName = selectedSub ? selectedSub.name : "";
      const finalTitle = newTitle.trim() || `Thảo luận môn ${subName}`;
      
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/chat/tutor/session`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token") || ""}`,
        },
        body: JSON.stringify({
          subject_id: Number(subjectId),
          title: finalTitle,
        }),
      });

      if (!res.ok) throw new Error();
      const data = await res.json();
      
      handleSessionCreated(data);
      setSubjectId("");
      setNewTitle("");
    } catch (err) {
      console.error(err);
    } finally {
      setCreating(false);
    }
  };

  // Tự động mở chat mới nếu chưa có phiên trò chuyện nào
  useEffect(() => {
    if (!chat.loadingSessions && chat.sessions.length === 0) {
      setShowNewChatForm(true);
    }
  }, [chat.loadingSessions, chat.sessions]);

  return (
    <div className="fixed bottom-6 right-6 z-50 font-sans">
      <AnimatePresence>
        {/* Nút Chat Bubble */}
        {!isOpen && (
          <motion.button
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            onClick={() => setIsOpen(true)}
            className="w-14 h-14 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white flex items-center justify-center shadow-lg shadow-indigo-500/30 cursor-pointer active:scale-95 transition-all relative group"
          >
            <MessageSquare className="w-6 h-6" />
            <span className="absolute -top-1 -right-1 w-3.5 h-3.5 bg-green-500 border-2 border-zinc-50 rounded-full animate-pulse" />
          </motion.button>
        )}

        {/* Khung Chat Floating Window */}
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="w-96 h-[550px] bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden backdrop-blur-md bg-white/95 dark:bg-zinc-900/95"
          >
            {/* Header */}
            <div className="h-14 px-4 border-b border-zinc-150 dark:border-zinc-850 bg-indigo-600 text-white flex items-center justify-between">
              <div className="flex items-center gap-2">
                {(showSessionsList || showNewChatForm) && chat.sessions.length > 0 && (
                  <button
                    onClick={() => {
                      setShowSessionsList(false);
                      setShowNewChatForm(false);
                    }}
                    className="p-1 hover:bg-white/10 rounded-lg cursor-pointer transition-colors"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                )}
                <div className="flex items-center gap-1.5">
                  <Bot className="w-5 h-5" />
                  <span className="font-extrabold text-xs tracking-wide uppercase">
                    {showNewChatForm
                      ? "Trò chuyện mới"
                      : showSessionsList
                      ? "Lịch sử trò chuyện"
                      : chat.activeSession?.title || "Gia sư ảo AI"}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-1">
                {!showSessionsList && !showNewChatForm && chat.sessions.length > 0 && (
                  <button
                    onClick={() => setShowSessionsList(true)}
                    className="p-1.5 hover:bg-white/10 rounded-lg cursor-pointer transition-colors"
                    title="Lịch sử chat"
                  >
                    <History className="w-4 h-4" />
                  </button>
                )}
                {!showNewChatForm && (
                  <button
                    onClick={() => setShowNewChatForm(true)}
                    className="p-1.5 hover:bg-white/10 rounded-lg cursor-pointer transition-colors"
                    title="Trò chuyện mới"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                )}
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1.5 hover:bg-white/10 rounded-lg cursor-pointer transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Body */}
            <div className="flex-1 overflow-y-auto p-4 bg-zinc-50 dark:bg-zinc-950/20">
              {showNewChatForm ? (
                /* Màn hình tạo phiên chat mới */
                <form onSubmit={handleCreateSession} className="space-y-4 pt-4">
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                      Môn học cần thảo luận
                    </label>
                    <select
                      value={subjectId}
                      onChange={(e) => setSubjectId(e.target.value)}
                      className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-850 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                      required
                    >
                      <option value="">-- Chọn môn học --</option>
                      {chat.subjects.map((s) => (
                        <option key={s.id} value={s.id}>
                          {s.name} ({s.code})
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                      Tiêu đề (tùy chọn)
                    </label>
                    <input
                      type="text"
                      value={newTitle}
                      onChange={(e) => setNewTitle(e.target.value)}
                      placeholder="VD: Hỏi bài tập Kế Thừa Java"
                      className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-850 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={creating || !subjectId}
                    className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold text-sm rounded-xl shadow-md cursor-pointer transition-all active:scale-[0.98] mt-4 flex items-center justify-center gap-1.5"
                  >
                    {creating && <Loader2 className="w-4 h-4 animate-spin" />}
                    Bắt đầu thảo luận
                  </button>
                </form>
              ) : showSessionsList ? (
                /* Màn hình danh sách cuộc trò chuyện */
                <div className="space-y-2">
                  {chat.sessions.length === 0 ? (
                    <div className="text-center py-12 text-zinc-400">
                      Chưa có cuộc hội thoại nào
                    </div>
                  ) : (
                    chat.sessions.map((session) => (
                      <div
                        key={session.session_id}
                        className={`flex items-center justify-between p-3 rounded-xl border transition-all cursor-pointer ${
                          chat.activeSession?.session_id === session.session_id
                            ? "bg-indigo-50 border-indigo-200 dark:bg-indigo-950/20 dark:border-indigo-800 text-indigo-950 dark:text-indigo-200"
                            : "bg-white border-zinc-200/80 dark:bg-zinc-900 dark:border-zinc-800 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800"
                        }`}
                        onClick={() => {
                          chat.loadMessages(session);
                          setShowSessionsList(false);
                        }}
                      >
                        <div className="flex-1 min-w-0 pr-2">
                          <p className="text-xs font-bold truncate">
                            {session.title}
                          </p>
                          <p className="text-[10px] text-zinc-400 mt-0.5">
                            Môn học: {getSubjectName(session.subject_id)}
                          </p>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            chat.handleDeleteSession(session.session_id);
                          }}
                          className="p-1 text-zinc-400 hover:text-red-500 rounded-lg transition-colors cursor-pointer"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    ))
                  )}
                </div>
              ) : (
                /* Màn hình nội dung tin nhắn chat */
                <div className="flex flex-col h-full space-y-4">
                  {chat.loadingMessages ? (
                    <div className="flex flex-col items-center justify-center py-20 text-zinc-400 gap-2">
                      <Loader2 className="w-6 h-6 animate-spin text-indigo-600" />
                      <span className="text-xs">Đang tải lịch sử...</span>
                    </div>
                  ) : (
                    <>
                      {chat.messages.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-16 text-center">
                          <Bot className="w-10 h-10 text-indigo-600 mb-2 animate-bounce" />
                          <p className="text-xs font-extrabold text-zinc-700 dark:text-zinc-300">
                            Chào bạn! Tôi là Gia sư ảo EduMind.
                          </p>
                          <p className="text-[11px] text-zinc-550 dark:text-zinc-500 mt-1 max-w-[80%]">
                            Tôi có thể giúp bạn giải đáp các thắc mắc về lý thuyết học tập. Hãy nhập câu hỏi dưới đây!
                          </p>
                        </div>
                      ) : (
                        chat.messages.map((msg, idx) => (
                          <div
                            key={idx}
                            className={`flex items-start gap-2.5 ${
                              msg.role === "user" ? "flex-row-reverse" : ""
                            }`}
                          >
                            <div
                              className={`w-7 h-7 rounded-lg flex items-center justify-center text-[10px] font-bold border shrink-0 ${
                                msg.role === "user"
                                  ? "bg-indigo-600 border-indigo-700 text-white"
                                  : "bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800 text-indigo-600"
                              }`}
                            >
                              {msg.role === "user" ? (
                                <User className="w-3.5 h-3.5" />
                              ) : (
                                <Bot className="w-3.5 h-3.5" />
                              )}
                            </div>
                            <div
                              className={`max-w-[78%] p-2.5 rounded-xl text-xs leading-relaxed ${
                                msg.role === "user"
                                  ? "bg-indigo-600 text-white rounded-tr-none whitespace-pre-wrap break-words"
                                  : "bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-zinc-800 dark:text-zinc-200 rounded-tl-none markdown-container"
                              }`}
                            >
                              {msg.role === "user" ? (
                                msg.content
                              ) : (
                                <MarkdownText content={msg.content} />
                              )}
                            </div>
                          </div>
                        ))
                      )}

                      {chat.sending && (
                        <div className="flex items-start gap-2.5">
                          <div className="w-7 h-7 rounded-lg flex items-center justify-center text-[10px] font-bold bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-indigo-600 shrink-0">
                            <Bot className="w-3.5 h-3.5" />
                          </div>
                          <div className="p-3 rounded-xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-tl-none flex items-center justify-center">
                            <Loader2 className="w-3.5 h-3.5 animate-spin text-zinc-400" />
                          </div>
                        </div>
                      )}
                      <div ref={chat.messagesEndRef} />
                    </>
                  )}
                </div>
              )}
            </div>

            {/* Footer Input */}
            {!showNewChatForm && !showSessionsList && chat.activeSession && (
              <form
                onSubmit={chat.handleSendMessage}
                className="p-3 border-t border-zinc-150 dark:border-zinc-850 bg-white dark:bg-zinc-900 flex gap-2"
              >
                <input
                  type="text"
                  value={chat.input}
                  onChange={(e) => chat.setInput(e.target.value)}
                  placeholder="Nhập câu hỏi thảo luận..."
                  className="flex-1 px-3 py-2 text-xs border border-zinc-200 dark:border-zinc-700 rounded-lg bg-zinc-50 dark:bg-zinc-800 text-zinc-900 dark:text-white focus:outline-none focus:border-indigo-500 focus:bg-white"
                  disabled={chat.sending || chat.loadingMessages}
                />
                <button
                  type="submit"
                  disabled={chat.sending || !chat.input.trim() || chat.loadingMessages}
                  className="p-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors cursor-pointer disabled:opacity-50"
                >
                  <Send className="w-3.5 h-3.5" />
                </button>
              </form>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
