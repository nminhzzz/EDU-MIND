import { apiClient } from "@/services/api-client";
import { getApiBaseUrl } from "@/config/api";
import { parseApiError } from "@/utils/api-error";

export async function openStudyDocument(docId: number): Promise<void> {
  const res = await apiClient.get<{ url: string }>(`/documents/${docId}/view-url`);
  let url = res.data.url;
  if (url.startsWith("/static/")) {
    url = `${getApiBaseUrl().replace(/\/api\/v1$/, "")}${url}`;
  }
  window.open(url, "_blank", "noopener,noreferrer");
}

export function studyDocumentOpenError(err: unknown, fallback: string): string {
  return parseApiError(err, fallback);
}
