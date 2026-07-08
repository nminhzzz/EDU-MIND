"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { chatService } from "@/features/student/services/chat";
import { ChatMessage } from "@/features/student/types/chat";
import { toast } from "sonner";

interface UseTutorChatOptions {
  subjectId: number;
  topic: string;
}

export function useTutorChat({ subjectId, topic }: UseTutorChatOptions) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loadingSession, setLoadingSession] = useState(true);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

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

  const handleSend = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!input.trim() || sending) return;

      const userMsg = input.trim();
      setInput("");
      setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
      setSending(true);

      try {
        let currentSessionId = sessionId;
        if (!currentSessionId) {
          const resSession = await chatService.createSession({
            subject_id: subjectId,
            title: `Học tập: ${topic}`,
          });
          currentSessionId = resSession.data;
          setSessionId(currentSessionId);
        }

        const res = await chatService.sendMessage({
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
    },
    [input, sending, sessionId, subjectId, topic],
  );

  return {
    messages,
    input,
    setInput,
    loadingSession,
    sending,
    messagesEndRef,
    handleSend,
  };
}
