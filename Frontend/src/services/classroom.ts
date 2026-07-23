import { apiClient } from "./api-client";
import { Classroom } from "@/types/classroom";
import { User } from "@/types/user";

export interface ClassroomDetail extends Classroom {
  teacher?: User | null;
  students?: User[] | null;
  subject?: {
    id: number;
    name: string;
    code: string;
    description?: string | null;
    created_at: string;
  } | null;
}

export interface ClassroomStudentProgress {
  student_id: number;
  email: string;
  full_name?: string | null;
  total_goals: number;
  completed_goals: number;
  total_attempts: number;
  average_score?: number | null;
}

export interface ClassroomQuizAttempt {
  attempt_id: number;
  quiz_id: number;
  quiz_title: string;
  student_id: number;
  student_name: string;
  student_email: string;
  score: number;
  correct_count: number;
  wrong_count: number;
  duration_seconds: number;
  submitted_at: string;
}

export const classroomApi = {
  listMine: () => apiClient.get<Classroom[]>("/classrooms/"),

  join: (classCode: string) =>
    apiClient.post("/classrooms/join", { class_code: classCode }),

  getDetail: (classroomId: number) =>
    apiClient.get<ClassroomDetail>(`/classrooms/${classroomId}`),

  getStudentsProgress: (classroomId: number) =>
    apiClient.get<ClassroomStudentProgress[]>(
      `/classrooms/${classroomId}/students/progress`,
    ),

  addStudent: (classroomId: number, studentEmail: string) =>
    apiClient.post(`/classrooms/${classroomId}/students`, {
      student_email: studentEmail,
    }),

  removeStudent: (classroomId: number, studentId: number) =>
    apiClient.delete(`/classrooms/${classroomId}/students/${studentId}`),

  deleteClassroom: (classroomId: number) =>
    apiClient.delete(`/classrooms/${classroomId}`),

  getQuizAttempts: (classroomId: number) =>
    apiClient.get<ClassroomQuizAttempt[]>(
      `/quizzes/classroom/${classroomId}/attempts`,
    ),

  getQuizzes: (classroomId: number) =>
    apiClient.get<any[]>(`/quizzes/classrooms/${classroomId}`),

  generateQuiz: (
    classroomId: number,
    payload: {
      subject_id: number;
      topic: string;
      difficulty: string;
      total_questions: number;
      deadline?: string;
      include_essay?: boolean;
      essay_count?: number;
    },
  ) =>
    apiClient.post<any>(`/quizzes/classrooms/${classroomId}/generate`, payload, {
      timeout: 120_000,
    }),

  generateQuizFromFile: (
    classroomId: number,
    formData: FormData,
  ) =>
    apiClient.post<any>(`/quizzes/classrooms/${classroomId}/generate-from-file`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
      timeout: 180_000,
    }),

  getChatMessages: (classroomId: number) =>
    apiClient.get<ClassroomChatMessage[]>(`/classrooms/${classroomId}/chat/messages`),

  getUnreadCounts: () =>
    apiClient.get<Record<number, number>>("/classrooms/unread-counts"),

  markChatRead: (classroomId: number) =>
    apiClient.post<{ status: string; last_read_message_id: number }>(
      `/classrooms/${classroomId}/chat/mark-read`
    ),
};

export interface ClassroomChatMessage {
  id: number;
  classroom_id: number;
  sender_id: number;
  content: string;
  created_at: string;
  sender: User;
}

export default classroomApi;
