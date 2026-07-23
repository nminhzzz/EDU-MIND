"use client";

import React, { useEffect } from "react";
import { ChevronLeft, MessageSquare } from "lucide-react";
import { Classroom } from "@/types/classroom";
import { ClassroomChatView } from "@/components/shared/classroom-chat-view";

interface ClassroomChatPanelProps {
  classroom: Classroom;
  onBack: () => void;
  onMarkRead: (classroomId: number) => void;
}

export function ClassroomChatPanel({
  classroom,
  onBack,
  onMarkRead,
}: ClassroomChatPanelProps) {
  useEffect(() => {
    // Automatically mark classroom messages as read when opening panel
    onMarkRead(classroom.id);
  }, [classroom.id, onMarkRead]);

  return (
    <div className="flex flex-col h-full bg-white dark:bg-zinc-900 rounded-2xl overflow-hidden">
      {/* Classroom Chat Header */}
      <div className="h-12 px-3 border-b border-zinc-200 dark:border-zinc-800 bg-indigo-600 text-white flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2 min-w-0">
          <button
            onClick={onBack}
            className="p-1 hover:bg-white/10 rounded-lg cursor-pointer transition-colors"
            title="Quay lại danh sách lớp"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2 min-w-0">
            <MessageSquare className="w-4 h-4 shrink-0" />
            <span className="font-extrabold text-xs tracking-wide truncate">
              {classroom.class_name}
            </span>
            <span className="text-[10px] font-mono bg-white/20 px-1.5 py-0.5 rounded text-white/90 shrink-0">
              {classroom.class_code}
            </span>
          </div>
        </div>
      </div>

      {/* Chat Messages Workspace */}
      <div className="flex-1 overflow-hidden">
        <ClassroomChatView classroomId={classroom.id} />
      </div>
    </div>
  );
}
