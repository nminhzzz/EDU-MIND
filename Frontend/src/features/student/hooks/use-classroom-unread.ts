"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { classroomApi } from "@/services/classroom";
import { getApiBaseUrl } from "@/config/api";
import { useAuth } from "@/hooks/use-auth";
import type { Classroom } from "@/types/classroom";

export function useClassroomUnread(classrooms?: Classroom[]) {
  const { user } = useAuth();
  const [unreadCounts, setUnreadCounts] = useState<Record<number, number>>({});
  const socketsRef = useRef<{ [classroomId: number]: WebSocket }>({});

  // 1. Initial fetch ONCE from DB (Zero periodic polling API calls!)
  const fetchUnread = useCallback(async () => {
    try {
      const res = await classroomApi.getUnreadCounts();
      if (res.data) {
        setUnreadCounts(res.data);
      }
    } catch (err) {
      console.error("Lỗi khi lấy số tin nhắn chưa đọc:", err);
    }
  }, []);

  const markRead = useCallback(async (classroomId: number) => {
    try {
      // Optimistic update locally
      setUnreadCounts((prev) => ({
        ...prev,
        [classroomId]: 0,
      }));
      await classroomApi.markChatRead(classroomId);
    } catch (err) {
      console.error(`Lỗi khi đánh dấu đã đọc cho lớp ${classroomId}:`, err);
    }
  }, []);

  // 2. Fetch initial unread counts ONCE on mount
  useEffect(() => {
    fetchUnread();
  }, [fetchUnread]);

  // 3. Realtime WebSocket unread listener for all user's classrooms
  useEffect(() => {
    if (!classrooms || classrooms.length === 0 || !user?.id) return;

    const apiBase = getApiBaseUrl();
    const wsBase = apiBase.replace(/^http/, "ws");

    classrooms.forEach((cls) => {
      const cid = cls.id;
      if (socketsRef.current[cid]) return;

      const wsUrl = `${wsBase}/classrooms/${cid}/chat/ws`;
      const ws = new WebSocket(wsUrl);

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          // If a new chat message arrives and sender is NOT the current user
          if (
            payload &&
            (payload.type === "chat_message" || payload.id) &&
            payload.sender_id &&
            payload.sender_id !== user.id
          ) {
            setUnreadCounts((prev) => ({
              ...prev,
              [cid]: (prev[cid] || 0) + 1,
            }));
          }
        } catch (e) {
          // ignore
        }
      };

      socketsRef.current[cid] = ws;
    });

    return () => {
      Object.values(socketsRef.current).forEach((ws) => {
        ws.close(1000, "Unread listener unmounted");
      });
      socketsRef.current = {};
    };
  }, [classrooms, user?.id]);

  const totalUnread = Object.values(unreadCounts).reduce((acc, count) => acc + count, 0);

  return {
    unreadCounts,
    totalUnread,
    markRead,
    refetchUnread: fetchUnread,
  };
}

