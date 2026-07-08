import type { NextResponse } from "next/server";

/** Auth cookie names and paths — must mirror Backend/app/api/v1/auth.py */

export const AUTH_COOKIES = {
  ACCESS: "access_token",
  REFRESH: "refresh_token",
  REFRESH_PATH: "/api/v1/auth/refresh",
} as const;

export interface JwtPayload {
  sub?: string;
  role?: string;
  exp?: number;
}

/** Decode JWT payload without verifying signature (UX routing only — not a security boundary). */
export function decodeJwtPayload(token: string): JwtPayload | null {
  try {
    const base64Url = token.split(".")[1];
    if (!base64Url) return null;
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(base64)) as JwtPayload;
  } catch {
    return null;
  }
}

export function isTokenExpired(payload: JwtPayload | null): boolean {
  if (!payload?.exp) return true;
  return payload.exp < Date.now() / 1000;
}

/** Remove auth cookies from a Next.js middleware response. */
export function clearAuthCookies(response: NextResponse): void {
  response.cookies.delete(AUTH_COOKIES.ACCESS);
  response.cookies.delete({
    name: AUTH_COOKIES.REFRESH,
    path: AUTH_COOKIES.REFRESH_PATH,
  });
}
