import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import {
  AUTH_COOKIES,
  clearAuthCookies,
  decodeJwtPayload,
  isTokenExpired,
} from "@/lib/auth-cookies";

/**
 * Real-world SaaS RBAC Middleware:
 * Enforces strict Role-Based Access Control (RBAC) at Edge level:
 * - /student/* → ONLY role 'student'
 * - /teacher/* → ONLY role 'teacher'
 * - /admin/*   → ONLY role 'admin'
 * Any unauthorized attempt is instantly redirected to the user's appropriate role dashboard.
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const accessToken = request.cookies.get(AUTH_COOKIES.ACCESS)?.value;
  const payload = accessToken ? decodeJwtPayload(accessToken) : null;

  const hasSession = !!accessToken;
  const isAuthenticated = !!payload && !isTokenExpired(payload);
  const userRole = payload?.role;

  const isAuthPage = pathname === "/login" || pathname === "/register";
  const isStudentPage = pathname.startsWith("/student");
  const isTeacherPage = pathname.startsWith("/teacher");
  const isAdminPage = pathname.startsWith("/admin");
  const isProtectedPage = isStudentPage || isTeacherPage || isAdminPage;

  // 1. Unauthenticated users accessing protected routes → redirect to /login
  if (!hasSession && isProtectedPage) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);

    const response = NextResponse.redirect(loginUrl);
    clearAuthCookies(response);
    return response;
  }

  // 2. Expired access cookie but still present → allow; AuthProvider handles renewal.
  if (hasSession && !isAuthenticated && isProtectedPage) {
    return NextResponse.next();
  }

  // 3. Visiting login page with redirect parameter after 401 → clear cookies
  if (isAuthPage && request.nextUrl.searchParams.has("redirect")) {
    const response = NextResponse.next();
    clearAuthCookies(response);
    return response;
  }

  // 4. Authenticated users visiting auth pages → redirect to their role home
  if (isAuthenticated && isAuthPage) {
    const defaultRoute = userRole ? `/${userRole}` : "/login";
    return NextResponse.redirect(new URL(defaultRoute, request.url));
  }

  // 5. Clear malformed cookies on auth pages
  if (isAuthPage && accessToken && !payload) {
    const response = NextResponse.next();
    clearAuthCookies(response);
    return response;
  }

  // 6. Strict Role-Based Access Control (RBAC)
  if (isAuthenticated && userRole) {
    if (isStudentPage && userRole !== "student") {
      return NextResponse.redirect(new URL(`/${userRole}`, request.url));
    }
    if (isTeacherPage && userRole !== "teacher") {
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
