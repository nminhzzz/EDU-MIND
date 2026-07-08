export interface ChatSession {
  session_id: string;
  title: string;
  subject_id: number;
  created_at: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

export interface CreateChatSessionPayload {
  subject_id: number;
  title: string;
}

export interface SendChatMessagePayload {
  session_id: string;
  content: string;
}

export interface ChatMessageReply {
  reply: string;
}

export interface ChatMessagesResponse {
  messages: ChatMessage[];
}
