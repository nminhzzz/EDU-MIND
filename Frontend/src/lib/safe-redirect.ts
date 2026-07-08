import { UserRole } from "@/types/user";

const PROTECTED_PREFIXES = ["/student", "/teacher", "/admin"] as const;

/**
 * Validate a post-login redirect path against open-redirect attacks
 * and the authenticated user's role.
 */
export function getSafeRedirectPath(
  redirect: string | null | undefined,
  role: UserRole,
): string | null {
  if (!redirect) return null;

  const path = redirect.trim();
  if (!path.startsWith("/") || path.startsWith("//")) return null;
  if (path.includes("://") || path.includes("\\")) return null;

  const prefix = PROTECTED_PREFIXES.find((p) => path === p || path.startsWith(`${p}/`));
  if (!prefix) return null;

  if (prefix === "/admin" && role !== "admin") return null;
  if (prefix === "/teacher" && role !== "teacher" && role !== "admin") return null;
  if (prefix === "/student" && role !== "student" && role !== "admin") return null;

  return path;
}
