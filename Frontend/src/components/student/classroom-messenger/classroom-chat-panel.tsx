"use client";

import React, { useEffect } from "react";
import { ChevronLeft, X } from "lucide-react";
import { Classroom } from "@/types/classroom";
import { ClassroomChatView } from "@/components/shared/classroom-chat-view";

interface ClassroomChatPanelProps {
  classroom: Classroom;
  onBack: () => void;
  onClose: () => void;
  onMarkRead: (classroomId: number) => void;
}

export function ClassroomChatPanel({
  classroom,
  onBack,
  onClose,
  onMarkRead,
}: ClassroomChatPanelProps) {
  useEffect(() => {
    onMarkRead(classroom.id);
  }, [classroom.id, onMarkRead]);

  return (
    <div className="flex flex-col h-full bg-white dark:bg-zinc-900 overflow-hidden">
      {/* Classroom Chat Header Bar */}
      <div className="h-14 px-3.5 border-b border-zinc-200 dark:border-zinc-800 bg-violet-600 text-white flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2 min-w-0">
          <button
            onClick={onBack}
            className="p-1.5 hover:bg-white/10 rounded-md cursor-pointer transition-colors"
            title="Quay lại danh sách lớp"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2 min-w-0">
            <span className="font-extrabold text-sm tracking-tight truncate">
              {classroom.class_name}
            </span>
            <span className="text-[10px] font-mono bg-white/20 px-2 py-0.5 rounded-md text-white/90 shrink-0 font-bold">
              {classroom.class_code}
            </span>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 hover:bg-white/10 rounded-md cursor-pointer transition-colors"
          title="Đóng"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Chat Messages Workspace */}
      <div className="flex-1 overflow-hidden">
        <ClassroomChatView classroomId={classroom.id} />
      </div>
    </div>
  );
}
