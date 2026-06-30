export const ROUTES = {
  HOME: "/",
  LOGIN: "/login",
  REGISTER: "/register",
  
  // Student Workspace
  STUDENT_DASHBOARD: "/student",
  STUDENT_GOALS: "/student/goals",
  STUDENT_QUIZ: (id: string | number) => `/student/quizzes/${id}`,
  STUDENT_CHAT: "/student/chat",
  
  // Teacher Workspace
  TEACHER_DASHBOARD: "/teacher",
  TEACHER_DOCUMENTS: "/teacher/documents",
  TEACHER_CLASSROOMS: "/teacher/classrooms",
  
  // Admin Panel
  ADMIN: "/admin",
};
