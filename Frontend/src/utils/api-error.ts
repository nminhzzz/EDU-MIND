import { isAxiosError } from "axios";

interface ValidationErrorItem {
  loc?: (string | number)[];
  msg?: string;
}

/**
 * Extract a user-facing message from a FastAPI / Axios error response.
 * Handles string details, Pydantic 422 arrays, CSRF 403, and rate-limit 429.
 */
export function parseApiError(
  err: unknown,
  fallback = "Đã xảy ra lỗi. Vui lòng thử lại.",
): string {
  if (!isAxiosError(err)) {
    if (err instanceof Error && err.message) return err.message;
    return fallback;
  }

  const status = err.response?.status;
  const detail = err.response?.data?.detail;

  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    return detail
      .map((item: ValidationErrorItem) => {
        const field =
          item.loc?.filter((part) => part !== "body").join(".") || "Lỗi";
        return `${field}: ${item.msg || "dữ liệu không hợp lệ"}`;
      })
      .join("; ");
  }

  if (status === 403) {
    return "Bạn không có quyền thực hiện thao tác này.";
  }

  if (status === 429) {
    return "Tần suất gọi quá nhanh. Vui lòng thử lại sau.";
  }

  if (err.message && !err.message.startsWith("Request failed with status")) {
    return err.message;
  }

  return fallback;
}

/** HTTP status from an Axios error, if present. */
export function getApiErrorStatus(err: unknown): number | undefined {
  return isAxiosError(err) ? err.response?.status : undefined;
}
