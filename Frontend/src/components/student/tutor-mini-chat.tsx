"use client";

import React, { useState, useEffect, useRef } from "react";
import { apiClient } from "@/services/api-client";
import { toast } from "sonner";
import { Send, Bot, User, Loader2 } from "lucide-react";
import { MarkdownText } from "./markdown-text";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface TutorMiniChatProps {
  subjectId: number;
  topic: string;
}

export function TutorMiniChat({ subjectId, topic }: TutorMiniChatProps) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loadingSession, setLoadingSession] = useState(true);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Chỉ hiển thị lời chào lúc mở modal, chưa lưu phiên vào database
  useEffect(() => {
    setMessages([
      {
        role: "assistant",
        content: `Chào bạn! Tôi là Gia sư AI. Hôm nay chúng ta sẽ cùng nghiên cứu về chủ đề **"${topic}"**. Bạn có thắc mắc gì cần tôi giải thích hay hướng dẫn không?`,
      },
    ]);
    setSessionId(null);
    setLoadingSession(false);
  }, [subjectId, topic]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || sending) return;

    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setSending(true);

    try {
      let currentSessionId = sessionId;
      if (!currentSessionId) {
        // Tạo phiên chat lười biếng khi học sinh thực sự gửi tin nhắn đầu tiên
        const resSession = await apiClient.post<string>("/chat/tutor/session", {
          subject_id: subjectId,
          title: `Học tập: ${topic}`,
        });
        currentSessionId = resSession.data;
        setSessionId(currentSessionId);
      }

      const res = await apiClient.post<{ reply: string }>("/chat/tutor/message", {
        session_id: currentSessionId,
        content: userMsg,
      });
      setMessages((prev) => [...prev, { role: "assistant", content: res.data.reply }]);
    } catch (err) {
      console.error("Lỗi gửi tin nhắn gia sư:", err);
      toast.error("Gia sư AI gặp sự cố khi trả lời.");
    } finally {
      setSending(false);
    }
  };

  if (loadingSession) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-zinc-400 dark:text-zinc-500 gap-2">
        <Loader2 className="w-6 h-6 animate-spin text-indigo-600" />
        <span className="text-xs">Đang kết nối với Gia sư AI...</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[400px] border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950/20 overflow-hidden">
      {/* Khung tin nhắn */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-2.5 ${
              msg.role === "user" ? "flex-row-reverse" : ""
            }`}
          >
            <div
              className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold border ${
                msg.role === "user"
                  ? "bg-indigo-600 border-indigo-700 text-white"
                  : "bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800 text-indigo-600"
              }`}
            >
              {msg.role === "user" ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
            </div>
            <div
              className={`max-w-[75%] p-3 rounded-xl text-xs leading-relaxed ${
                msg.role === "user"
                  ? "bg-indigo-600 text-white rounded-tr-none whitespace-pre-wrap break-words"
                  : "bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-zinc-800 dark:text-zinc-200 rounded-tl-none"
              }`}
            >
              {msg.role === "user" ? (
                msg.content
              ) : (
                <MarkdownText content={msg.content} />
              )}
            </div>
          </div>
        ))}
        {sending && (
          <div className="flex items-start gap-2.5">
            <div className="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-indigo-600">
              <Bot className="w-3.5 h-3.5" />
            </div>
            <div className="p-3 rounded-xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-tl-none flex items-center justify-center">
              <Loader2 className="w-3.5 h-3.5 animate-spin text-zinc-400" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSend} className="p-3 border-t border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Nhập câu hỏi thảo luận..."
          className="flex-1 px-3 py-2 text-xs border border-zinc-200 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-850 text-zinc-900 dark:text-white focus:outline-none focus:border-indigo-500"
          disabled={sending}
        />
        <button
          type="submit"
          disabled={sending || !input.trim()}
          className="p-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors cursor-pointer disabled:opacity-55"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
}
