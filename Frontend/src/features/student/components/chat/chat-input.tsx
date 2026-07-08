"use client";

import React from "react";
import { Send } from "lucide-react";

interface ChatInputProps {
  value: string;
  sending: boolean;
  onChange: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
}

export function ChatInput({ value, sending, onChange, onSubmit }: ChatInputProps) {
  return (
    <form onSubmit={onSubmit} className="p-4 border-t border-zinc-200/80 dark:border-zinc-800 flex gap-3">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Nhập câu hỏi của bạn về lý thuyết, bài tập hoặc đề bài..."
        disabled={sending}
        className="flex-1 px-4 py-3 border border-zinc-200 dark:border-zinc-700 rounded-xl bg-white dark:bg-zinc-900 text-zinc-900 dark:text-white text-xs font-semibold focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
      />
      <button
        type="submit"
        disabled={!value.trim() || sending}
        className="px-5 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white rounded-xl font-bold text-xs flex items-center gap-1.5 transition-all shadow-md active:scale-95 cursor-pointer"
      >
        <Send className="w-3.5 h-3.5" />
        Gửi
      </button>
    </form>
  );
}
