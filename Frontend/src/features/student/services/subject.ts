import { apiClient } from "@/services/api-client";
import type { Subject } from "@/features/student/types";

export const subjectService = {
  list: () => apiClient.get<Subject[]>("/subjects/"),
};

export default subjectService;
