"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { classroomApi, ClassroomChatMessage } from "@/services/classroom";
import { getApiBaseUrl } from "@/config/api";
import { toast } from "sonner";

export function useClassroomChat(classroomId: number) {
  const [messages, setMessages] = useState<ClassroomChatMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectDelayRef = useRef(1000); // Start reconnect delay at 1s

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

    // Build the dynamic WebSocket URL
    const apiBase = getApiBaseUrl();
    const wsBase = apiBase.replace(/^http/, "ws");
    const wsUrl = `${wsBase}/classrooms/${classroomId}/chat/ws`;

    const ws = new WebSocket(wsUrl);
    socketRef.current = ws;

    ws.onopen = () => {
      if (socketRef.current !== ws) return;
      console.log("WebSocket Classroom Chat Connected!");
      setConnected(true);
      reconnectDelayRef.current = 1000; // Reset delay on success

      // Heartbeat every 30 seconds to keep connection alive through reverse proxies
      heartbeatIntervalRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: "ping" }));
        }
      }, 30000);
    };

    ws.onmessage = (event) => {
      if (socketRef.current !== ws) return;
      try {
        const message = JSON.parse(event.data);
        // Append new broadcasted message to list
        if (message && message.id) {
          setMessages((prev) => {
            // Avoid duplicates
            if (prev.some((m) => m.id === message.id)) return prev;
            return [...prev, message];
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

      // Clean up heartbeat
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
        heartbeatIntervalRef.current = null;
      }

      // Exponential backoff reconnect
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
      ws.send(JSON.stringify({ content }));
    } else {
      toast.error("Không có kết nối mạng. Đang tự động kết nối lại...");
    }
  }, []);

  useEffect(() => {
    // Initial fetch and ws connection
    fetchHistory();
    connectWs();

    return () => {
      // Clean up connection and timeouts on unmount
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
    };
  }, [classroomId, fetchHistory, connectWs]);

  return {
    messages,
    loading,
    connected,
    sendMessage,
    refetchHistory: fetchHistory,
  };
}
