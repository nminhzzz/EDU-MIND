export type StudyPlanStatus = "todo" | "in_progress" | "done";
export type StudyPlanContentType = "theory" | "practice" | "exam" | "revision";

export interface StudyPlan {
  id: number;
  student_id: number;
  study_goal_id: number;
  title: string;
  description: string | null;
  day_number: number;
  status: StudyPlanStatus;
  content_type: StudyPlanContentType;
  is_ai_recommended: boolean;
  created_at: string;
  updated_at: string;
}

export type StudyGoalStatus = "active" | "completed";

export interface StudyGoal {
  id: number;
  student_id: number;
  title: string;
  description: string | null;
  subject_name: string;
  total_days: number;
  status: StudyGoalStatus;
  created_at: string;
}
