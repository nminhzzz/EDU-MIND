import { apiClient } from "./api-client";
import { ApiMessageResponse } from "@/types/api";
import {
  ConfirmDraftResponse,
  ConfirmRequest,
  DraftRequest,
  DraftResponse,
  StudentPreference,
  StudyGoal,
} from "@/types/goal";
import { Subject } from "@/types/subject";

export type {
  ConfirmDraftResponse,
  ConfirmRequest,
  DraftRequest,
  DraftResponse,
  StudentPreference,
  StudyGoal,
} from "@/types/goal";
export type { Subject } from "@/types/subject";

/** @deprecated Use StudyGoal */
export type StudyGoalResponse = StudyGoal;

/** AI roadmap generation can take 30–90s (LLM + RAG). Default axios timeout is 30s. */
const AI_DRAFT_TIMEOUT_MS = 120_000;
const AI_CONFIRM_TIMEOUT_MS = 60_000;

import { StudyPlan } from "./study-plan";

export const goalApi = {
  getPreferences: () =>
    apiClient.get<StudentPreference>("/users/preferences"),

  updatePreferences: (data: {
    study_hours_per_day: number;
    preferred_study_time: string;
    available_schedule: Record<string, unknown>;
  }) => apiClient.put<StudentPreference>("/users/preferences", data),

  getSubjects: () => apiClient.get<Subject[]>("/subjects/"),

  getGoals: () => apiClient.get<StudyGoal[]>("/goals/"),

  getGoal: (id: number) => apiClient.get<StudyGoal>(`/goals/${id}`),

  getGoalPlans: (id: number) => apiClient.get<StudyPlan[]>(`/goals/${id}/plans`),

  deleteGoal: (id: number) =>
    apiClient.delete<ApiMessageResponse>(`/goals/${id}`),

  createDraft: (data: DraftRequest) =>
    apiClient.post<DraftResponse>("/goals/unified/draft", data, {
      timeout: AI_DRAFT_TIMEOUT_MS,
    }),

  confirmDraft: (data: ConfirmRequest) =>
    apiClient.post<ConfirmDraftResponse>("/goals/unified/confirm", data, {
      timeout: AI_CONFIRM_TIMEOUT_MS,
    }),
};

export default goalApi;
