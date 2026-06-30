export interface Classroom {
  id: number;
  name: string;
  code: string;
  teacher_id: number;
  created_at: string;
}

export interface ClassroomStudent {
  id: number;
  classroom_id: number;
  student_id: number;
  joined_at: string;
}

export interface Subject {
  id: number;
  name: string;
  code: string;
  description: string | null;
  grade: string | null;
}
