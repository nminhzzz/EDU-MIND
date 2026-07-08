"use client";

import { useCallback, useState } from "react";
import { chatService } from "@/features/student/services/chat";
import { ChatSession } from "@/features/student/types/chat";
import type { Subject } from "@/features/student/types";
import { toast } from "sonner";

export function useNewChatSession(
  subjects: Subject[],
  onCreated: (session: ChatSession) => void,
  onClose: () => void,
) {
  const [subjectId, setSubjectId] = useState("");
  const [title, setTitle] = useState("");
  const [creating, setCreating] = useState(false);

  const handleCreateSession = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!subjectId) {
        toast.error("Vui lòng chọn môn học.");
        return;
      }

      setCreating(true);
      try {
        const selectedSubj = subjects.find((s) => s.id === parseInt(subjectId, 10));
        const payload = {
          subject_id: parseInt(subjectId, 10),
          title: title.trim() || `Trò chuyện môn ${selectedSubj?.name || ""}`,
        };

        const res = await chatService.createSession(payload);
        const newSession: ChatSession = {
          session_id: res.data,
          title: payload.title,
          subject_id: payload.subject_id,
          created_at: new Date().toISOString(),
        };

        toast.success("Đã mở cuộc thảo luận mới cùng Gia sư AI!");
        onCreated(newSession);
        setSubjectId("");
        setTitle("");
        onClose();
      } catch {
        toast.error("Khởi tạo phiên trò chuyện thất bại.");
      } finally {
        setCreating(false);
      }
    },
    [subjectId, title, subjects, onCreated, onClose],
  );

  return {
    subjectId,
    setSubjectId,
    title,
    setTitle,
    creating,
    handleCreateSession,
  };
}
