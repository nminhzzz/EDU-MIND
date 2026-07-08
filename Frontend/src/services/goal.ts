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

  deleteGoal: (id: number) =>
    apiClient.delete<ApiMessageResponse>(`/goals/${id}`),

  createDraft: (data: DraftRequest) =>
    apiClient.post<DraftResponse>("/goals/unified/draft", data),

  confirmDraft: (data: ConfirmRequest) =>
    apiClient.post<ConfirmDraftResponse>("/goals/unified/confirm", data),
};

export default goalApi;
