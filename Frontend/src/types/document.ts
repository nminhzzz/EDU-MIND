export interface StudyDocument {
  id: number;
  title: string;
  description: string | null;
  file_url: string;
  file_type: string; // e.g., "pdf", "docx", "txt"
  teacher_id: number;
  subject_id: number | null;
  created_at: string;
  updated_at: string;
}
