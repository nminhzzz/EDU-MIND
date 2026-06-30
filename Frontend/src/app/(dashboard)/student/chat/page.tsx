"use client";

import React, { useEffect, useState, useRef } from "react";
import { apiClient } from "@/services/api-client";
import { toast } from "sonner";
import { MessageSquare, Send, Bot, User, Sparkles } from "lucide-react";
import { ChatSidebar } from "@/components/student/chat-sidebar";
import { NewChatModal } from "@/components/student/new-chat-modal";

interface Subject {
  id: number;
  name: string;
  code: string;
}

interface ChatSession {
  session_id: string;
  title: string;
  subject_id: number;
  created_at: string;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

export default function StudentChatPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [activeSession, setActiveSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  
  const [loadingSessions, setLoadingSessions] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [sending, setSending] = useState(false);
  const [input, setInput] = useState("");
  const [showNewChatModal, setShowNewChatModal] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initData = async () => {
    try {
      const [sessionsRes, subjectsRes] = await Promise.all([
        apiClient.get<ChatSession[]>("/chat/tutor/sessions"),
        apiClient.get<Subject[]>("/subjects/"),
      ]);
      setSessions(sessionsRes.data);
      setSubjects(subjectsRes.data);
      if (sessionsRes.data.length > 0) {
        handleSelectSession(sessionsRes.data[0]);
      }
    } catch (err) {
      console.error("Lỗi khởi tạo danh sách chat:", err);
      toast.error("Không thể tải lịch sử trò chuyện.");
    } finally {
      setLoadingSessions(false);
    }
  };

  useEffect(() => {
    initData();
  }, []);

  const handleSelectSession = async (session: ChatSession) => {
    setActiveSession(session);
    setLoadingMessages(true);
    try {
      const res = await apiClient.get<{ messages: ChatMessage[] }>(`/chat/tutor/messages/${session.session_id}`);
      setMessages(res.data.messages || []);
    } catch (err) {
      console.error("Lỗi khi tải lịch sử tin nhắn:", err);
      toast.error("Không thể tải tin nhắn của cuộc hội thoại.");
    } finally {
      setLoadingMessages(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !activeSession || sending) return;

    const userMsgText = input.trim();
    setInput("");
    
    const userMsg: ChatMessage = { role: "user", content: userMsgText };
    setMessages(prev => [...prev, userMsg]);
    setSending(true);

    try {
      const payload = {
        session_id: activeSession.session_id,
        content: userMsgText,
      };

      const res = await apiClient.post<{ reply: string }>(
        "/chat/tutor/message",
        payload
      );
      
      const aiReply: ChatMessage = { role: "assistant", content: res.data.reply };
      setMessages(prev => [...prev, aiReply]);
    } catch (err) {
      console.error("Lỗi gửi tin nhắn:", err);
      toast.error("Gia sư AI gặp sự cố kết nối. Vui lòng gửi lại.");
    } finally {
      setSending(false);
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    if (!confirm("Bạn có chắc muốn xóa cuộc thảo luận này?")) return;
    try {
      await apiClient.delete(`/chat/tutor/session/${sessionId}`);
      toast.success("Đã xóa cuộc thảo luận thành công.");
      
      const remaining = sessions.filter((s) => s.session_id !== sessionId);
      setSessions(remaining);
      
      if (activeSession?.session_id === sessionId) {
        if (remaining.length > 0) {
          handleSelectSession(remaining[0]);
        } else {
          setActiveSession(null);
          setMessages([]);
        }
      }
    } catch (err) {
      console.error("Lỗi khi xóa phiên chat:", err);
      toast.error("Không thể xóa cuộc thảo luận. Vui lòng thử lại.");
    }
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex border border-zinc-200/80 dark:border-zinc-800 rounded-2xl overflow-hidden bg-white dark:bg-zinc-950 text-left">
      {/* ── CỘT TRÁI: DANH SÁCH LỊCH SỬ CHAT ── */}
      <ChatSidebar
        sessions={sessions}
        activeSession={activeSession}
        onSelectSession={handleSelectSession}
        onDeleteSession={handleDeleteSession}
        onNewChatClick={() => setShowNewChatModal(true)}
        loading={loadingSessions}
      />

      {/* ── KHUNG BÊN PHẢI: CHI TIẾT CUỘC TRÒ CHUYỆN ── */}
      <div className="flex-1 flex flex-col justify-between bg-white dark:bg-zinc-950">
        {activeSession ? (
          <>
            {/* Header */}
            <div className="px-6 py-4 border-b border-zinc-200/80 dark:border-zinc-800 flex items-center justify-between bg-zinc-50/30 dark:bg-zinc-900/10">
              <div>
                <h3 className="font-extrabold text-sm text-zinc-900 dark:text-white">{activeSession.title}</h3>
                <span className="text-[10px] text-zinc-400 font-medium block mt-0.5">
                  Mã phiên: {activeSession.session_id.substring(0, 8)}...
                </span>
              </div>
              <div className="flex items-center gap-1.5 text-[10px] font-bold text-indigo-650 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 px-2.5 py-1 rounded-lg">
                <Sparkles className="w-3.5 h-3.5" />
                AI Tutor Active
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {loadingMessages ? (
                <div className="h-full flex items-center justify-center">
                  <div className="w-8 h-8 border-4 border-indigo-650 border-t-transparent rounded-full animate-spin" />
                </div>
              ) : messages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-zinc-400 space-y-3">
                  <Bot className="w-12 h-12 opacity-30 text-indigo-450" />
                  <p className="text-sm font-semibold">Chào bạn! Hãy đặt câu hỏi để cùng thảo luận bài học nhé.</p>
                </div>
              ) : (
                messages.map((msg, idx) => {
                  const isAI = msg.role === "assistant";
                  return (
                    <div
                      key={idx}
                      className={`flex gap-4 max-w-[85%] ${isAI ? "mr-auto text-left" : "ml-auto flex-row-reverse text-right"}`}
                    >
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 border ${
                        isAI
                          ? "bg-indigo-50 border-indigo-100 text-indigo-600 dark:bg-indigo-950/50 dark:border-zinc-800 dark:text-indigo-400"
                          : "bg-zinc-100 border-zinc-200 text-zinc-655 dark:bg-zinc-800 dark:border-zinc-700 dark:text-zinc-200"
                      }`}>
                        {isAI ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
                      </div>
                      <div className={`p-4 rounded-2xl text-xs font-semibold leading-relaxed border ${
                        isAI
                          ? "bg-zinc-50/50 dark:bg-zinc-900/30 border-zinc-200 dark:border-zinc-850 text-zinc-800 dark:text-zinc-200"
                          : "bg-indigo-600 text-white border-transparent"
                      }`}>
                        {msg.content}
                      </div>
                    </div>
                  );
                })
              )}
              {sending && (
                <div className="flex gap-4 max-w-[80%] mr-auto text-left animate-pulse">
                  <div className="w-8 h-8 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-600 flex items-center justify-center">
                    <Bot className="w-4 h-4" />
                  </div>
                  <div className="p-4 rounded-2xl bg-zinc-50 border border-zinc-200 text-zinc-400 text-xs font-medium">
                    Gia sư AI đang lập luận câu trả lời...
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input form */}
            <form onSubmit={handleSendMessage} className="p-4 border-t border-zinc-200/80 dark:border-zinc-800 flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Nhập câu hỏi của bạn về lý thuyết, bài tập hoặc đề bài..."
                disabled={sending}
                className="flex-1 px-4 py-3 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-900 text-zinc-900 dark:text-white text-xs font-semibold focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
              />
              <button
                type="submit"
                disabled={!input.trim() || sending}
                className="px-5 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white rounded-xl font-bold text-xs flex items-center gap-1.5 transition-all shadow-md active:scale-95 cursor-pointer"
              >
                <Send className="w-3.5 h-3.5" />
                Gửi
              </button>
            </form>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-zinc-400 space-y-4">
            <MessageSquare className="w-16 h-16 opacity-20 text-indigo-400" />
            <div className="text-center space-y-1.5">
              <h3 className="text-sm font-bold text-zinc-700 dark:text-zinc-300">Không có cuộc trò chuyện nào</h3>
              <p className="text-xs text-zinc-400 max-w-xs">Hãy khởi tạo cuộc hội thoại mới cùng Trợ lý Gia sư AI để bắt đầu học tập.</p>
            </div>
            <button
              onClick={() => setShowNewChatModal(true)}
              className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold shadow-md transition-all active:scale-[0.98] cursor-pointer"
            >
              Tạo cuộc thảo luận mới
            </button>
          </div>
        )}
      </div>

      {/* New chat modal */}
      <NewChatModal
        isOpen={showNewChatModal}
        onClose={() => setShowNewChatModal(false)}
        subjects={subjects}
        onCreated={(newSession) => {
          setSessions(prev => [newSession, ...prev]);
          setActiveSession(newSession);
          setMessages([]);
        }}
      />
    </div>
  );
}
