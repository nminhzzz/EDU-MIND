import React from "react";
import { cookies } from "next/headers";
import { QuizzesClient } from "./quizzes-client";

interface Subject {
  id: number;
  name: string;
  code: string;
}

interface Attempt {
  attempt_id: number;
  quiz_id: number;
  quiz_title: string;
  score: number;
  correct_count: number;
  wrong_count: number;
  duration_seconds: number;
  submitted_at: string;
}

const BACKEND_INTERNAL_URL = "http://localhost:8000/api/v1";

async function getQuizzesHistory(token?: string): Promise<Attempt[]> {
  if (!token) return [];
  try {
    const res = await fetch(`${BACKEND_INTERNAL_URL}/quizzes/student/history`, {
      headers: {
        Cookie: `access_token=${token}`,
        "X-Requested-With": "XMLHttpRequest",
      },
      cache: "no-store",
    });
    if (!res.ok) return [];
    return await res.json();
  } catch (err) {
    console.error("Lỗi tải lịch sử bài làm phía Server Component:", err);
    return [];
  }
}

async function getSubjects(token?: string): Promise<Subject[]> {
  if (!token) return [];
  try {
    const res = await fetch(`${BACKEND_INTERNAL_URL}/subjects/`, {
      headers: {
        Cookie: `access_token=${token}`,
        "X-Requested-With": "XMLHttpRequest",
      },
      cache: "no-store",
    });
    if (!res.ok) return [];
    return await res.json();
  } catch (err) {
    console.error("Lỗi tải danh sách môn học phía Server Component:", err);
    return [];
  }
}

export default async function StudentQuizzesPage() {
  const cookieStore = await cookies();
  const token = cookieStore.get("access_token")?.value;

  const [attempts, subjects] = await Promise.all([
    getQuizzesHistory(token),
    getSubjects(token),
  ]);

  return <QuizzesClient initialAttempts={attempts} initialSubjects={subjects} />;
}
