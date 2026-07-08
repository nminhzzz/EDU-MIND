"use client";

import React from "react";
import { Sparkles } from "lucide-react";
import { ChatSession } from "@/features/student/types/chat";

interface ChatSessionHeaderProps {
  session: ChatSession;
}

export function ChatSessionHeader({ session }: ChatSessionHeaderProps) {
  return (
    <div className="px-6 py-4 border-b border-zinc-200/80 dark:border-zinc-800 flex items-center justify-between bg-zinc-50/30 dark:bg-zinc-900/10">
      <div>
        <h3 className="font-extrabold text-sm text-zinc-900 dark:text-white">{session.title}</h3>
        <span className="text-[10px] text-zinc-400 font-medium block mt-0.5">
          Mã phiên: {session.session_id.substring(0, 8)}...
        </span>
      </div>
      <div className="flex items-center gap-1.5 text-[10px] font-bold text-indigo-650 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 px-2.5 py-1 rounded-lg">
        <Sparkles className="w-3.5 h-3.5" />
        AI Tutor Active
      </div>
    </div>
  );
}
