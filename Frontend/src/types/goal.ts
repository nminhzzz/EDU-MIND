export interface StudentPreference {
  id: number;
  student_id: number;
  study_hours_per_day: number;
  preferred_study_time: "morning" | "afternoon" | "evening";
  available_schedule: Record<string, unknown>;
}

export interface DraftRequest {
  subject_id: number;
  target_score: number;
  deadline: string;
}

export interface RoadmapPlan {
  weeks: Array<{ week: number; tasks: string[] }>;
  daily_schedule: Array<{
    date: string;
    start_time: string;
    end_time: string;
    task: string;
    description: string;
  }>;
  curriculum_materials?: Array<{ topic: string; content: string }>;
  quizzes?: Array<{ title: string; questions: unknown[] }>;
}

export interface DraftResponse {
  message: string;
  plan: RoadmapPlan;
}

export interface ConfirmRequest {
  subject_id: number;
  target_score: number;
  deadline: string;
  plan: RoadmapPlan;
}

/** Matches Backend StudyGoalResponse. */
export interface StudyGoal {
  id: number;
  student_id: number;
  subject_id: number;
  title: string;
  target_score: number;
  deadline: string;
  status: "active" | "completed" | "cancelled" | string;
  created_at: string;
}

/** Matches Backend unified confirm response. */
export interface ConfirmDraftResponse {
  message: string;
  goal: {
    id: number;
    title: string;
    subject_id: number;
    target_score: number;
    deadline: string;
    status: string;
    created_at: string;
  };
  total_plans: number;
  total_quizzes: number;
}
