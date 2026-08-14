"use client";

import { useChat } from "@/features/student/hooks/use-chat";
import { ChatLayout } from "@/features/student/components/chat";
import { PageHeader } from "@/components/ui";

export default function StudentChatPage() {
  const chat = useChat();

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="AI Tutor" title="Trợ lý gia sư AI" description="Trao đổi về bài học, giải đáp thắc mắc và nhận gợi ý học tập phù hợp với bạn." />

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
