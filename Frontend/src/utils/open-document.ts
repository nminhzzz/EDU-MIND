import { apiClient } from "@/services/api-client";
import { parseApiError } from "@/utils/api-error";

const LOADING_HTML =
  "<p style='font-family:system-ui,sans-serif;padding:24px;color:#52525b'>Đang mở tài liệu...</p>";

export async function openStudyDocument(docId: number): Promise<void> {
  const popup = window.open("about:blank", "_blank");
  if (!popup) {
    throw new Error("Trình duyệt đã chặn cửa sổ mới. Vui lòng cho phép popup cho trang này.");
  }

  popup.document.title = "Đang mở tài liệu...";
  popup.document.body.innerHTML = LOADING_HTML;

  try {
    const { data } = await apiClient.get<{ url: string }>(
      `/documents/${docId}/view-url`,
    );
    popup.opener = null;
    popup.location.replace(data.url);
  } catch (err) {
    popup.close();
    throw err;
  }
}

export function studyDocumentOpenError(err: unknown, fallback: string): string {
  return parseApiError(err, fallback);
}
