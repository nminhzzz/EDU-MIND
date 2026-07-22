export const ROUTES = {
  HOME: "/",
  LOGIN: "/login",
  REGISTER: "/register",
  
  // Student Workspace
  STUDENT_DASHBOARD: "/student",
  STUDENT_TASKS: "/student/tasks",
  STUDENT_TASK: (id: string | number) => `/student/tasks/${id}`,
  STUDENT_GOALS: "/student/goals",
  STUDENT_GOAL_DETAIL: (id: string | number) => `/student/goals/${id}`,
  STUDENT_QUIZZES: "/student/quizzes",
  STUDENT_QUIZ: (id: string | number) => `/student/quizzes/${id}`,
  STUDENT_CHAT: "/student/chat",
  
  // Teacher Workspace
  TEACHER_DASHBOARD: "/teacher",
  TEACHER_DOCUMENTS: "/teacher/documents",
  TEACHER_CLASSROOMS: "/teacher/classrooms",
  TEACHER_CLASSROOM_DETAIL: (id: string | number) => `/teacher/classrooms/${id}`,
  
  // Admin Panel
  ADMIN: "/admin",
};
