import { apiClient } from "@/services/api-client";
import { StudyDocument } from "@/types/document";

export const documentService = {
  listBySubject: (subjectId: number) =>
    apiClient.get<StudyDocument[]>(`/documents/?subject_id=${subjectId}`),
};

export default documentService;
