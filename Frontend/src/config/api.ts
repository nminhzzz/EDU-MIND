/**
 * Central API URL configuration.
 *
 * NEXT_PUBLIC_API_URL — browser-facing base (Axios, EventSource).
 *   Dev/Docker:  http://localhost:8000/api/v1
 *   Prod/nginx:  https://localhost/api/v1  (or /api/v1 for same-origin)
 *
 * API_INTERNAL_URL — server-side only (SSR fetch inside Docker network).
 *   Docker:      http://backend:8000/api/v1
 *   Local dev:   falls back to NEXT_PUBLIC_API_URL
 */

const DEV_DEFAULT = "http://localhost:8000/api/v1";

function normalizeBaseUrl(url: string): string {
  return url.replace(/\/$/, "");
}

/** Base URL for all client-side API calls (browser). */
export function getApiBaseUrl(): string {
  const env = process.env.NEXT_PUBLIC_API_URL;
  if (env) return normalizeBaseUrl(env);
  return DEV_DEFAULT;
}

/** Base URL for server-side fetch (SSR / Server Components). */
export function getApiInternalUrl(): string {
  const internal = process.env.API_INTERNAL_URL;
  if (internal) return normalizeBaseUrl(internal);

  const publicUrl = process.env.NEXT_PUBLIC_API_URL;
  if (publicUrl) return normalizeBaseUrl(publicUrl);

  return DEV_DEFAULT;
}

/** Build a full API endpoint URL from a relative path. */
export function apiUrl(path: string, internal = false): string {
  const base = internal ? getApiInternalUrl() : getApiBaseUrl();
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${base}${normalizedPath}`;
}
