export type UserRole = "student" | "teacher" | "admin";

export type StudentGrade =
  | "grade_6"
  | "grade_7"
  | "grade_8"
  | "grade_9"
  | "grade_10"
  | "grade_11"
  | "grade_12"
  | "uni_year_1"
  | "uni_year_2"
  | "uni_year_3"
  | "uni_year_4";

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  avatar_url: string | null;
  role: UserRole;
  grade: StudentGrade | null;
  is_active: boolean;
  created_at: string;
}

export interface AuthMessageResponse {
  message: string;
  token_type: "bearer";
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  role: UserRole;
  grade: StudentGrade | null;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
