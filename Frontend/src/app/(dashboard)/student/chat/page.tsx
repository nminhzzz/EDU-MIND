"use client";

import { useChat } from "@/features/student/hooks/use-chat";
import { ChatLayout } from "@/features/student/components/chat";

export default function StudentChatPage() {
  const chat = useChat();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-black text-zinc-900 dark:text-zinc-50 tracking-tight">
          Trợ lý Gia sư AI
        </h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
          Thảo luận trực tiếp cùng Gia sư AI để giải đáp thắc mắc bài học, giải toán, viết văn và định hướng học tập.
        </p>
      </div>

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
    </div>
  );
}
