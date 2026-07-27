"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { classroomApi, ClassroomChatMessage } from "@/services/classroom";
import { getApiBaseUrl } from "@/config/api";
import { toast } from "sonner";

export function useClassroomChat(classroomId: number) {
  const [messages, setMessages] = useState<ClassroomChatMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);
  const [onlineUserIds, setOnlineUserIds] = useState<number[]>([]);
  const [onlineCount, setOnlineCount] = useState<number>(0);
  const [typingUsers, setTypingUsers] = useState<string[]>([]);

  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const typingTimerRef = useRef<{ [name: string]: NodeJS.Timeout }>({});
  const lastTypingSentRef = useRef<number>(0);
  const reconnectDelayRef = useRef(1000);

  // 1. Fetch Chat History
  const fetchHistory = useCallback(async () => {
    try {
      const res = await classroomApi.getChatMessages(classroomId);
      setMessages(res.data);
    } catch (err) {
      console.error("Lỗi khi tải lịch sử tin nhắn:", err);
      toast.error("Không thể tải lịch sử thảo luận của lớp.");
    } finally {
      setLoading(false);
    }
  }, [classroomId]);

  // 2. Connect WebSocket with Keep-Alive Heartbeat & Reconnection
  const connectWs = useCallback(() => {
    if (socketRef.current) return;

    const apiBase = getApiBaseUrl();
    const wsBase = apiBase.replace(/^http/, "ws");
    const wsUrl = `${wsBase}/classrooms/${classroomId}/chat/ws`;

    const ws = new WebSocket(wsUrl);
    socketRef.current = ws;

    ws.onopen = () => {
      if (socketRef.current !== ws) return;
      console.log("WebSocket Classroom Chat Connected!");
      setConnected(true);
      reconnectDelayRef.current = 1000;

      heartbeatIntervalRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: "ping" }));
        }
      }, 30000);
    };

    ws.onmessage = (event) => {
      if (socketRef.current !== ws) return;
      try {
        const payload = JSON.parse(event.data);

        // Handle online presence payload
        if (payload && payload.type === "online_presence") {
          setOnlineUserIds(payload.online_user_ids || []);
          setOnlineCount(payload.online_count || 0);
          return;
        }

        // Handle typing status payload
        if (payload && payload.type === "typing") {
          const userName = payload.user_name;
          if (userName) {
            setTypingUsers((prev) => Array.from(new Set([...prev, userName])));
            
            if (typingTimerRef.current[userName]) {
              clearTimeout(typingTimerRef.current[userName]);
            }
            typingTimerRef.current[userName] = setTimeout(() => {
              setTypingUsers((prev) => prev.filter((name) => name !== userName));
              delete typingTimerRef.current[userName];
            }, 2500);
          }
          return;
        }

        // Handle chat message payload
        if (payload && payload.id) {
          setMessages((prev) => {
            if (prev.some((m) => m.id === payload.id)) return prev;
            return [...prev, payload];
          });
        }
      } catch (err) {
        console.error("Lỗi phân tích tin nhắn nhận được:", err);
      }
    };

    ws.onclose = (event) => {
      if (socketRef.current !== ws) return;
      console.log("WebSocket Classroom Chat Closed:", event.reason);
      setConnected(false);
      socketRef.current = null;

      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
        heartbeatIntervalRef.current = null;
      }

      if (event.code !== 1000) {
        const delay = reconnectDelayRef.current;
        console.log(`Reconnecting to room chat in ${delay}ms...`);
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectDelayRef.current = Math.min(reconnectDelayRef.current * 2, 16000);
          connectWs();
        }, delay);
      }
    };

    ws.onerror = (event) => {
      if (socketRef.current !== ws) return;
      console.error("WebSocket Classroom Chat Error:", event);
      ws.close();
    };
  }, [classroomId]);

  // 3. Send Message
  const sendMessage = useCallback((content: string) => {
    const ws = socketRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "message", content }));
    } else {
      toast.error("Không có kết nối mạng. Đang tự động kết nối lại...");
    }
  }, []);

  // 4. Send Typing signal (throttled to 1.5s)
  const sendTyping = useCallback(() => {
    const now = Date.now();
    if (now - lastTypingSentRef.current < 1500) return;
    lastTypingSentRef.current = now;

    const ws = socketRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "typing" }));
    }
  }, []);

  useEffect(() => {
    fetchHistory();
    connectWs();

    return () => {
      if (socketRef.current) {
        socketRef.current.close(1000, "Component unmounted");
        socketRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
      }
      Object.values(typingTimerRef.current).forEach(clearTimeout);
    };
  }, [classroomId, fetchHistory, connectWs]);

  return {
    messages,
    loading,
    connected,
    onlineUserIds,
    onlineCount,
    typingUsers,
    sendMessage,
    sendTyping,
    refetchHistory: fetchHistory,
  };
}

