/** Matches Backend ClassroomResponse. */
export interface Classroom {
  id: number;
  teacher_id: number;
  subject_id: number;
  class_name: string;
  class_code: string;
  description: string | null;
  created_at: string;
  student_count?: number;
  subject?: {
    id: number;
    name: string;
    code: string;
  } | null;
}

export interface ClassroomStudent {
  id: number;
  classroom_id: number;
  student_id: number;
  joined_at: string;
}
