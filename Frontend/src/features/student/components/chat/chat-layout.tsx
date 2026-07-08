"use client";

import React from "react";
import { ChatMessage, ChatSession } from "@/features/student/types/chat";
import type { Subject } from "@/features/student/types";
import { ChatEmptyState } from "./chat-empty-state";
import { ChatInput } from "./chat-input";
import { ChatMessageList } from "./chat-message-list";
import { ChatSessionHeader } from "./chat-session-header";
import { ChatSidebar } from "./chat-sidebar";
import { NewChatModal } from "./new-chat-modal";

interface ChatLayoutProps {
  sessions: ChatSession[];
  subjects: Subject[];
  activeSession: ChatSession | null;
  messages: ChatMessage[];
  loadingSessions: boolean;
  loadingMessages: boolean;
  sending: boolean;
  input: string;
  showNewChatModal: boolean;
  messagesEndRef: React.RefObject<HTMLDivElement | null>;
  onSelectSession: (session: ChatSession) => void;
  onDeleteSession: (sessionId: string) => void;
  onInputChange: (value: string) => void;
  onSendMessage: (e: React.FormEvent) => void;
  onSessionCreated: (session: ChatSession) => void;
  onOpenNewChatModal: () => void;
  onCloseNewChatModal: () => void;
}

export function ChatLayout({
  sessions,
  subjects,
  activeSession,
  messages,
  loadingSessions,
  loadingMessages,
  sending,
  input,
  showNewChatModal,
  messagesEndRef,
  onSelectSession,
  onDeleteSession,
  onInputChange,
  onSendMessage,
  onSessionCreated,
  onOpenNewChatModal,
  onCloseNewChatModal,
}: ChatLayoutProps) {
  return (
    <div className="h-[calc(100vh-8rem)] flex border border-zinc-200/80 dark:border-zinc-800 rounded-2xl overflow-hidden bg-white dark:bg-zinc-950 text-left">
      <ChatSidebar
        sessions={sessions}
        activeSession={activeSession}
        onSelectSession={onSelectSession}
        onDeleteSession={onDeleteSession}
        onNewChatClick={onOpenNewChatModal}
        loading={loadingSessions}
      />

      <div className="flex-1 flex flex-col justify-between bg-white dark:bg-zinc-950">
        {activeSession ? (
          <>
            <ChatSessionHeader session={activeSession} />
            <ChatMessageList
              messages={messages}
              loading={loadingMessages}
              sending={sending}
              messagesEndRef={messagesEndRef}
            />
            <ChatInput
              value={input}
              sending={sending}
              onChange={onInputChange}
              onSubmit={onSendMessage}
            />
          </>
        ) : (
          <ChatEmptyState onNewChatClick={onOpenNewChatModal} />
        )}
      </div>

      <NewChatModal
        isOpen={showNewChatModal}
        onClose={onCloseNewChatModal}
        subjects={subjects}
        onCreated={onSessionCreated}
      />
    </div>
  );
}
