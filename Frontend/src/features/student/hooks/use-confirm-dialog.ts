"use client";

import { useCallback } from "react";

export function useConfirmDialog() {
  return useCallback((message: string): boolean => {
    return window.confirm(message);
  }, []);
}
