"use client";

import React from "react";
import { MessageSquare } from "lucide-react";
import { StudentEmptyState } from "@/features/student/components/common/student-empty-state";

interface ChatEmptyStateProps {
  onNewChatClick: () => void;
}

export function ChatEmptyState({ onNewChatClick }: ChatEmptyStateProps) {
  return (
    <StudentEmptyState
      icon={MessageSquare}
      title="Không có cuộc trò chuyện nào"
      description="Hãy khởi tạo cuộc hội thoại mới cùng Trợ lý Gia sư AI để bắt đầu học tập."
      variant="center"
      action={{ label: "Tạo cuộc thảo luận mới", onClick: onNewChatClick }}
    />
  );
}
