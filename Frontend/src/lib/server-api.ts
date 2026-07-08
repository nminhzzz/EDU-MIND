import { cookies } from "next/headers";
import { apiUrl } from "@/config/api";
import { AUTH_COOKIES } from "@/lib/auth-cookies";

export type ServerFetchResult<T> =
  | { ok: true; data: T }
  | { ok: false; unauthorized: boolean };

function buildAuthCookieHeader(
  cookieStore: Awaited<ReturnType<typeof cookies>>,
): string | null {
  const accessToken = cookieStore.get(AUTH_COOKIES.ACCESS)?.value;
  if (!accessToken) return null;
  return `${AUTH_COOKIES.ACCESS}=${accessToken}`;
}

/**
 * Authenticated fetch for Server Components.
 * Forwards the HttpOnly access_token cookie to the internal API URL.
 */
export async function serverFetch<T>(
  path: string,
  init: RequestInit = {},
): Promise<ServerFetchResult<T>> {
  const cookieStore = await cookies();
  const cookieHeader = buildAuthCookieHeader(cookieStore);

  if (!cookieHeader) {
    return { ok: false, unauthorized: true };
  }

  try {
    const res = await fetch(apiUrl(path, true), {
      ...init,
      headers: {
        ...init.headers,
        Cookie: cookieHeader,
      },
      cache: "no-store",
    });

    if (res.status === 401) {
      return { ok: false, unauthorized: true };
    }

    if (!res.ok) {
      return { ok: false, unauthorized: false };
    }

    const data = (await res.json()) as T;
    return { ok: true, data };
  } catch (err) {
    console.error(`Server fetch failed for ${path}:`, err);
    return { ok: false, unauthorized: false };
  }
}

/** True when SSR could not load data and the client should retry via apiClient. */
export function needsClientFallback(
  results: ServerFetchResult<unknown>[],
): boolean {
  return results.some((r) => !r.ok);
}

export function unwrapServerData<T>(
  result: ServerFetchResult<T>,
  fallback: T,
): T {
  return result.ok ? result.data : fallback;
}
