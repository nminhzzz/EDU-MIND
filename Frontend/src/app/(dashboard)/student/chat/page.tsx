"use client";

import React from "react";
import { ChatLayout } from "@/features/student/components/chat/chat-layout";
import { useChat } from "@/features/student/hooks/use-chat";

export default function StudentChatPage() {
  const chat = useChat();

  return (
    <ChatLayout
      sessions={chat.sessions}
      subjects={chat.subjects}
      activeSession={chat.activeSession}
      messages={chat.messages}
      loadingSessions={chat.loadingSessions}
      loadingMessages={chat.loadingMessages}
      sending={chat.sending}
      input={chat.input}
      showNewChatModal={chat.showNewChatModal}
      messagesEndRef={chat.messagesEndRef}
      onSelectSession={chat.loadMessages}
      onDeleteSession={chat.handleDeleteSession}
      onInputChange={chat.setInput}
      onSendMessage={chat.handleSendMessage}
      onSessionCreated={chat.handleSessionCreated}
      onOpenNewChatModal={chat.openNewChatModal}
      onCloseNewChatModal={chat.closeNewChatModal}
    />
  );
}
