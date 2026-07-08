"use client";

import { useAuth } from "@/hooks/use-auth";

/** Derived admin role check — auth redirect is handled by middleware + dashboard layout. */
export function useAdminAccess() {
  const { user, isLoading } = useAuth();
  const denied = !isLoading && user?.role !== "admin";

  return { isLoading, denied, user };
}
