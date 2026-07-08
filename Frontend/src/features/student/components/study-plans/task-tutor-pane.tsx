"use client";

import React from "react";
import { MessageSquare } from "lucide-react";
import { TutorMiniChat } from "@/features/student/components/chat/tutor-mini-chat";

interface TaskTutorPaneProps {
  subjectId: number;
  topic: string;
}

export function TaskTutorPane({ subjectId, topic }: TaskTutorPaneProps) {
  return (
    <div className="flex flex-col h-full overflow-hidden p-6 space-y-4">
      <div className="flex items-center gap-2 pb-2 border-b border-zinc-100 dark:border-zinc-800/80 text-left">
        <MessageSquare className="w-4.5 h-4.5 text-indigo-500" />
        <h4 className="text-xs font-extrabold text-zinc-850 dark:text-zinc-200 uppercase tracking-wide">
          Gia sư AI 24/7
        </h4>
      </div>
      <div className="flex-1 overflow-hidden">
        <TutorMiniChat subjectId={subjectId} topic={topic} />
      </div>
    </div>
  );
}
