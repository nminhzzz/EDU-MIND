"use client";

import React from "react";
import { Bot, User } from "lucide-react";
import { ChatMessage } from "@/features/student/types/chat";

interface ChatMessageBubbleProps {
  message: ChatMessage;
}

export function ChatMessageBubble({ message }: ChatMessageBubbleProps) {
  const isAI = message.role === "assistant";

  return (
    <div
      className={`flex gap-4 max-w-[85%] ${isAI ? "mr-auto text-left" : "ml-auto flex-row-reverse text-right"}`}
    >
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 border ${
          isAI
            ? "bg-indigo-50 border-indigo-100 text-indigo-600 dark:bg-indigo-950/50 dark:border-zinc-800 dark:text-indigo-400"
            : "bg-zinc-100 border-zinc-200 text-zinc-655 dark:bg-zinc-800 dark:border-zinc-700 dark:text-zinc-200"
        }`}
      >
        {isAI ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
      </div>
      <div
        className={`p-4 rounded-2xl text-xs font-semibold leading-relaxed border ${
          isAI
            ? "bg-zinc-50/50 dark:bg-zinc-900/30 border-zinc-200 dark:border-zinc-850 text-zinc-800 dark:text-zinc-200"
            : "bg-indigo-600 text-white border-transparent"
        }`}
      >
        {message.content}
      </div>
    </div>
  );
}

interface ChatMessageListProps {
  messages: ChatMessage[];
  loading: boolean;
  sending: boolean;
  messagesEndRef: React.RefObject<HTMLDivElement | null>;
}

export function ChatMessageList({
  messages,
  loading,
  sending,
  messagesEndRef,
}: ChatMessageListProps) {
  if (loading) {
    return (
      <div className="flex-1 overflow-y-auto p-6">
        <div className="h-full flex items-center justify-center">
          <div className="w-8 h-8 border-4 border-indigo-650 border-t-transparent rounded-full animate-spin" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4">
      {messages.length === 0 ? (
        <div className="h-full flex flex-col items-center justify-center text-zinc-400 space-y-3">
          <Bot className="w-12 h-12 opacity-30 text-indigo-450" />
          <p className="text-sm font-semibold">
            Chào bạn! Hãy đặt câu hỏi để cùng thảo luận bài học nhé.
          </p>
        </div>
      ) : (
        messages.map((msg, idx) => <ChatMessageBubble key={idx} message={msg} />)
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
  );
}
