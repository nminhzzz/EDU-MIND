import { useAuthContext } from "@/providers/auth-provider";

/**
 * Access authentication state and actions (login, logout, register).
 * Session is cookie-based — tokens are never stored in localStorage.
 */
export const useAuth = useAuthContext;
