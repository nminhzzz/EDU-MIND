import { apiClient } from "@/services/api-client";
import { parseApiError } from "@/utils/api-error";

const LOADING_HTML =
  "<p style='font-family:system-ui,sans-serif;padding:24px;color:#52525b'>Đang tải tài liệu...</p>";

export async function openStudyDocument(docId: number): Promise<void> {
  const popup = window.open("about:blank", "_blank");
  if (!popup) {
    throw new Error("Trình duyệt đã chặn cửa sổ mới. Vui lòng cho phép popup cho trang này.");
  }

  popup.document.title = "Đang tải tài liệu...";
  popup.document.body.innerHTML = LOADING_HTML;

  try {
    const res = await apiClient.get(`/documents/${docId}/file`, {
      responseType: "blob",
    });
    const contentType =
      (res.headers["content-type"] as string | undefined) ?? "application/pdf";
    const blob = new Blob([res.data], { type: contentType });
    const blobUrl = URL.createObjectURL(blob);

    popup.location.href = blobUrl;
    popup.opener = null;
    window.setTimeout(() => URL.revokeObjectURL(blobUrl), 120_000);
  } catch (err) {
    popup.close();
    throw err;
  }
}

export function studyDocumentOpenError(err: unknown, fallback: string): string {
  return parseApiError(err, fallback);
}
