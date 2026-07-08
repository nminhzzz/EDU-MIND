"use client";

import { useCallback } from "react";
import { apiUrl } from "@/config/api";

export interface UseSSEOptions<T> {
  path: string;
  withCredentials?: boolean;
  onMessage: (data: T, event: MessageEvent) => void;
  onError?: (event: Event) => void;
  parse?: (raw: string) => T;
}

function defaultParse<T>(raw: string): T {
  return JSON.parse(raw) as T;
}

export function useSSE<T>({
  path,
  withCredentials = true,
  onMessage,
  onError,
  parse = defaultParse,
}: UseSSEOptions<T>) {
  const connect = useCallback(() => {
    const eventSource = new EventSource(apiUrl(path), { withCredentials });

    eventSource.onmessage = (event) => {
      try {
        const parsed = parse(event.data);
        onMessage(parsed, event);
      } catch (err) {
        console.error("Lỗi phân tích cú pháp dữ liệu SSE:", err);
      }
    };

    eventSource.onerror = (event) => {
      console.error("EventSource gặp lỗi kết nối:", event);
      onError?.(event);
    };

    return () => {
      eventSource.close();
    };
  }, [path, withCredentials, onMessage, onError, parse]);

  return { connect };
}
