import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import {
  AUTH_COOKIES,
  clearAuthCookies,
  decodeJwtPayload,
  isTokenExpired,
} from "@/lib/auth-cookies";

/**
 * Edge route guard — coarse UX-level protection only.
 * JWT payload is decoded without signature verification; the backend
 * enforces real authentication on every API request.
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const accessToken = request.cookies.get(AUTH_COOKIES.ACCESS)?.value;
  const payload = accessToken ? decodeJwtPayload(accessToken) : null;

  // Access cookie present (even if expired) — client can silently refresh via /auth/refresh.
  const hasSession = !!accessToken;
  const isAuthenticated = !!payload && !isTokenExpired(payload);
  const userRole = payload?.role;

  const isAuthPage = pathname === "/login" || pathname === "/register";
  const isStudentPage = pathname.startsWith("/student");
  const isTeacherPage = pathname.startsWith("/teacher");
  const isAdminPage = pathname.startsWith("/admin");
  const isProtectedPage = isStudentPage || isTeacherPage || isAdminPage;

  // No session at all → redirect to login.
  if (!hasSession && isProtectedPage) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);

    const response = NextResponse.redirect(loginUrl);
    clearAuthCookies(response);
    return response;
  }

  // Expired access cookie but still present → allow; AuthProvider + Axios refresh handle renewal.
  if (hasSession && !isAuthenticated && isProtectedPage) {
    return NextResponse.next();
  }

  // Valid session on auth pages → redirect to role dashboard.
  if (isAuthenticated && isAuthPage) {
    return NextResponse.redirect(new URL(`/${userRole}`, request.url));
  }

  // Auth pages: clear only malformed cookies (not merely expired ones).
  if (isAuthPage && accessToken && !payload) {
    const response = NextResponse.next();
    clearAuthCookies(response);
    return response;
  }

  // Role-based authorization (only when access token is still valid).
  if (isAuthenticated) {
    if (isStudentPage && userRole !== "student" && userRole !== "admin") {
      return NextResponse.redirect(new URL(`/${userRole}`, request.url));
    }
    if (isTeacherPage && userRole !== "teacher" && userRole !== "admin") {
      return NextResponse.redirect(new URL(`/${userRole}`, request.url));
    }
    if (isAdminPage && userRole !== "admin") {
      return NextResponse.redirect(new URL(`/${userRole}`, request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico|.*\\.(?:png|svg|jpg|jpeg|gif|webp)$).*)"],
};
