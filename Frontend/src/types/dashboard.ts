/** Matches Backend build_dashboard_payload SSE snapshot. */
export interface StudentDashboardStats {
  timestamp: string;
  active_goals: number;
  today: {
    total_tasks: number;
    done: number;
    doing: number;
    remaining: number;
  };
  overall: {
    progress_pct: number;
    done_plans: number;
    total_plans: number;
  };
  quizzes: {
    total_attempts: number;
    avg_score: number;
  };
  next_task: {
    title: string;
    date: string;
    time: string;
  } | null;
  weak_areas: string[];
  unread_notifications: number;
}
