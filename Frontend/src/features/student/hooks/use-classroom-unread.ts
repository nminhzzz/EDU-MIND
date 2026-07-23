"use client";

import { useState, useEffect, useCallback } from "react";
import { classroomApi } from "@/services/classroom";

export function useClassroomUnread() {
  const [unreadCounts, setUnreadCounts] = useState<Record<number, number>>({});

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

  useEffect(() => {
    fetchUnread();
    // Poll unread counts every 30 seconds
    const interval = setInterval(fetchUnread, 30000);
    return () => clearInterval(interval);
  }, [fetchUnread]);

  const totalUnread = Object.values(unreadCounts).reduce((acc, count) => acc + count, 0);

  return {
    unreadCounts,
    totalUnread,
    markRead,
    refetchUnread: fetchUnread,
  };
}
