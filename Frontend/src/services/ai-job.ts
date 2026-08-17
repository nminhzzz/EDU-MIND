import { apiClient } from "./api-client";

export type AIJobStatus = "queued" | "running" | "completed" | "failed" | "cancelled";

export interface AIJob<T = Record<string, unknown>> {
  id: string;
  job_type: string;
  status: AIJobStatus;
  result: T | null;
  error: string | null;
}

export const aiJobApi = {
  get: <T>(id: string) => apiClient.get<AIJob<T>>(`/ai-jobs/${id}`),
  cancel: (id: string) => apiClient.post<AIJob>(`/ai-jobs/${id}/cancel`),
};

export async function waitForAIJob<T>(id: string, intervalMs = 1200): Promise<AIJob<T>> {
  for (;;) {
    const { data } = await aiJobApi.get<T>(id);
    if (["completed", "failed", "cancelled"].includes(data.status)) return data;
    await new Promise((resolve) => window.setTimeout(resolve, intervalMs));
  }
}
