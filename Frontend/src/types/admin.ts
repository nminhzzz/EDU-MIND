import { StudentGrade, UserRole } from "./user";

/** Matches Backend AdminUserResponse. */
export interface AdminUser {
  id: number;
  email: string;
  full_name: string | null;
  role: UserRole | string;
  is_active: boolean;
  created_at: string;
  grade: StudentGrade | string | null;
}

/** Matches Backend AdminAnalyticsResponse. */
export interface AdminAnalytics {
  total_students: number;
  total_teachers: number;
  total_admins: number;
  total_classrooms: number;
  total_active_goals: number;
  total_study_plans: number;
  total_quizzes: number;
}
