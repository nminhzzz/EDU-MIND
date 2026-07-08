/** Matches Backend SubjectResponse. */
export interface Subject {
  id: number;
  name: string;
  code: string;
  description?: string | null;
  created_at: string;
}
