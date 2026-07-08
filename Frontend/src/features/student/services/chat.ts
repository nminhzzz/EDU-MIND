import { apiClient } from "@/services/api-client";
import {
  ChatMessageReply,
  ChatMessagesResponse,
  ChatSession,
  CreateChatSessionPayload,
  SendChatMessagePayload,
} from "@/features/student/types/chat";

export const chatService = {
  listSessions: () => apiClient.get<ChatSession[]>("/chat/tutor/sessions"),

  createSession: (payload: CreateChatSessionPayload) =>
    apiClient.post<string>("/chat/tutor/session", payload),

  getMessages: (sessionId: string) =>
    apiClient.get<ChatMessagesResponse>(`/chat/tutor/messages/${sessionId}`),

  sendMessage: (payload: SendChatMessagePayload) =>
    apiClient.post<ChatMessageReply>("/chat/tutor/message", payload),

  deleteSession: (sessionId: string) =>
    apiClient.delete(`/chat/tutor/session/${sessionId}`),
};

export default chatService;
