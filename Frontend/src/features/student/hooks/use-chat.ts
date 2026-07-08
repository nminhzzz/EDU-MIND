"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { chatService } from "@/features/student/services/chat";
import { useConfirmDialog } from "@/features/student/hooks/use-confirm-dialog";
import { useSubjects } from "@/features/student/hooks/use-subjects";
import { ChatMessage, ChatSession } from "@/features/student/types/chat";
import { toast } from "sonner";

export function useChat() {
  const confirm = useConfirmDialog();
  const { subjects, fetchSubjects } = useSubjects();
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSession, setActiveSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loadingSessions, setLoadingSessions] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [sending, setSending] = useState(false);
  const [input, setInput] = useState("");
  const [showNewChatModal, setShowNewChatModal] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  const loadMessages = useCallback(async (session: ChatSession) => {
    setActiveSession(session);
    setLoadingMessages(true);
    try {
      const res = await chatService.getMessages(session.session_id);
      setMessages(res.data.messages || []);
    } catch (err) {
      console.error("Lỗi khi tải lịch sử tin nhắn:", err);
      toast.error("Không thể tải tin nhắn của cuộc hội thoại.");
    } finally {
      setLoadingMessages(false);
    }
  }, []);

  useEffect(() => {
    const initData = async () => {
      try {
        const [sessionsRes] = await Promise.all([
          chatService.listSessions(),
          fetchSubjects(),
        ]);
        setSessions(sessionsRes.data);
        if (sessionsRes.data.length > 0) {
          await loadMessages(sessionsRes.data[0]);
        }
      } catch (err) {
        console.error("Lỗi khởi tạo danh sách chat:", err);
        toast.error("Không thể tải lịch sử trò chuyện.");
      } finally {
        setLoadingSessions(false);
      }
    };

    initData();
  }, [loadMessages, fetchSubjects]);

  const handleSendMessage = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!input.trim() || !activeSession || sending) return;

      const userMsgText = input.trim();
      setInput("");

      const userMsg: ChatMessage = { role: "user", content: userMsgText };
      setMessages((prev) => [...prev, userMsg]);
      setSending(true);

      try {
        const res = await chatService.sendMessage({
          session_id: activeSession.session_id,
          content: userMsgText,
        });
        const aiReply: ChatMessage = { role: "assistant", content: res.data.reply };
        setMessages((prev) => [...prev, aiReply]);
      } catch (err) {
        console.error("Lỗi gửi tin nhắn:", err);
        toast.error("Gia sư AI gặp sự cố kết nối. Vui lòng gửi lại.");
      } finally {
        setSending(false);
      }
    },
    [input, activeSession, sending],
  );

  const handleDeleteSession = useCallback(
    async (sessionId: string) => {
      if (!confirm("Bạn có chắc muốn xóa cuộc thảo luận này?")) return;
      try {
        await chatService.deleteSession(sessionId);
        toast.success("Đã xóa cuộc thảo luận thành công.");

        const remaining = sessions.filter((s) => s.session_id !== sessionId);
        setSessions(remaining);

        if (activeSession?.session_id === sessionId) {
          if (remaining.length > 0) {
            await loadMessages(remaining[0]);
          } else {
            setActiveSession(null);
            setMessages([]);
          }
        }
      } catch (err) {
        console.error("Lỗi khi xóa phiên chat:", err);
        toast.error("Không thể xóa cuộc thảo luận. Vui lòng thử lại.");
      }
    },
    [sessions, activeSession, loadMessages, confirm],
  );

  const handleSessionCreated = useCallback((newSession: ChatSession) => {
    setSessions((prev) => [newSession, ...prev]);
    setActiveSession(newSession);
    setMessages([]);
  }, []);

  const openNewChatModal = useCallback(() => setShowNewChatModal(true), []);
  const closeNewChatModal = useCallback(() => setShowNewChatModal(false), []);

  return {
    sessions,
    subjects,
    activeSession,
    messages,
    loadingSessions,
    loadingMessages,
    sending,
    input,
    setInput,
    showNewChatModal,
    messagesEndRef,
    loadMessages,
    handleSendMessage,
    handleDeleteSession,
    handleSessionCreated,
    openNewChatModal,
    closeNewChatModal,
  };
}
