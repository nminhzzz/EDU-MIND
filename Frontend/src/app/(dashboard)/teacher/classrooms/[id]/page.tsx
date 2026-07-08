"use client";

import React, { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  BarChart3,
  BookOpen,
  Loader2,
  Trash2,
  Trophy,
  UserMinus,
  UserPlus,
  Users,
} from "lucide-react";
import { toast } from "sonner";
import { ROUTES } from "@/constants/routes";
import { AddStudentModal } from "@/components/teacher/add-student-modal";
import { QuizResultTable } from "@/components/teacher/quiz-result-table";
import { StudentProgressTable } from "@/components/teacher/student-progress-table";
import classroomApi, {
  ClassroomDetail,
  ClassroomQuizAttempt,
  ClassroomStudentProgress,
} from "@/services/classroom";
import { parseApiError } from "@/utils/api-error";
import { User } from "@/types/user";

type TabId = "students" | "progress" | "quizzes";

const TABS: { id: TabId; label: string; icon: React.ElementType }[] = [
  { id: "students", label: "Danh sách học sinh", icon: Users },
  { id: "progress", label: "Tiến độ học tập", icon: BarChart3 },
  { id: "quizzes", label: "Kết quả bài thi", icon: Trophy },
];

export default function ClassroomDetailPage() {
  const params = useParams();
  const router = useRouter();
  const classroomId = Number(params.id);

  const [classroom, setClassroom] = useState<ClassroomDetail | null>(null);
  const [progress, setProgress] = useState<ClassroomStudentProgress[]>([]);
  const [quizAttempts, setQuizAttempts] = useState<ClassroomQuizAttempt[]>([]);
  const [activeTab, setActiveTab] = useState<TabId>("students");
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [removingId, setRemovingId] = useState<number | null>(null);
  const [deleting, setDeleting] = useState(false);

  const fetchClassroom = useCallback(async () => {
    const res = await classroomApi.getDetail(classroomId);
    setClassroom(res.data);
  }, [classroomId]);

  const fetchProgress = useCallback(async () => {
    const res = await classroomApi.getStudentsProgress(classroomId);
    setProgress(res.data);
  }, [classroomId]);

  const fetchQuizAttempts = useCallback(async () => {
    const res = await classroomApi.getQuizAttempts(classroomId);
    setQuizAttempts(res.data);
  }, [classroomId]);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchClassroom(),
        fetchProgress(),
        fetchQuizAttempts(),
      ]);
    } catch (err) {
      console.error("Lỗi tải chi tiết lớp học:", err);
      toast.error("Không thể tải thông tin lớp học.");
    } finally {
      setLoading(false);
    }
  }, [fetchClassroom, fetchProgress, fetchQuizAttempts]);

  useEffect(() => {
    if (!classroomId || Number.isNaN(classroomId)) return;
    fetchAll();
  }, [classroomId, fetchAll]);

  const handleAddStudent = async (email: string) => {
    await classroomApi.addStudent(classroomId, email);
    toast.success("Đã thêm học sinh vào lớp.");
    await fetchAll();
  };

  const handleRemoveStudent = async (studentId: number) => {
    if (!confirm("Bạn có chắc muốn xóa học sinh này khỏi lớp?")) return;

    setRemovingId(studentId);
    try {
      await classroomApi.removeStudent(classroomId, studentId);
      toast.success("Đã xóa học sinh khỏi lớp.");
      await fetchAll();
    } catch (err) {
      toast.error(parseApiError(err, "Không thể xóa học sinh."));
    } finally {
      setRemovingId(null);
    }
  };

  const handleDeleteClassroom = async () => {
    if (
      !confirm(
        "Bạn có chắc muốn giải tán lớp học này? Hành động này không thể hoàn tác.",
      )
    ) {
      return;
    }

    setDeleting(true);
    try {
      await classroomApi.deleteClassroom(classroomId);
      toast.success("Đã giải tán lớp học.");
      router.push(ROUTES.TEACHER_CLASSROOMS);
    } catch (err) {
      toast.error(parseApiError(err, "Không thể giải tán lớp học."));
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="py-24 text-center space-y-4">
        <div className="w-10 h-10 border-4 border-violet-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400">
          Đang tải thông tin lớp học...
        </p>
      </div>
    );
  }

  if (!classroom) {
    return (
      <div className="text-center py-24">
        <p className="text-sm text-zinc-500">Không tìm thấy lớp học.</p>
        <Link
          href={ROUTES.TEACHER_CLASSROOMS}
          className="text-sm font-bold text-violet-600 hover:underline mt-4 inline-block"
        >
          Quay lại danh sách lớp
        </Link>
      </div>
    );
  }

  const students = classroom.students ?? [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
        <div className="space-y-3">
          <Link
            href={ROUTES.TEACHER_CLASSROOMS}
            className="inline-flex items-center gap-1.5 text-xs font-bold text-zinc-500 hover:text-violet-600 dark:hover:text-violet-400 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Quay lại danh sách lớp
          </Link>
          <div>
            <h1 className="text-2xl font-black text-zinc-900 dark:text-white">
              {classroom.class_name}
            </h1>
            <div className="flex flex-wrap items-center gap-3 mt-2">
              <span className="text-xs font-mono text-violet-600 dark:text-violet-400 bg-violet-50 dark:bg-violet-950/40 px-2.5 py-1 rounded-md">
                {classroom.class_code}
              </span>
              {classroom.subject && (
                <span className="text-xs text-zinc-500 dark:text-zinc-400 flex items-center gap-1">
                  <BookOpen className="w-3.5 h-3.5" />
                  {classroom.subject.name}
                </span>
              )}
              <span className="text-xs text-zinc-500 dark:text-zinc-400 flex items-center gap-1">
                <Users className="w-3.5 h-3.5" />
                {students.length} học sinh
              </span>
            </div>
            {classroom.description && (
              <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-2 max-w-2xl">
                {classroom.description}
              </p>
            )}
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2.5 bg-violet-600 hover:bg-violet-500 text-white font-bold text-sm rounded-xl shadow-md shadow-violet-500/20 transition-all active:scale-[0.98] flex items-center gap-2 cursor-pointer"
          >
            <UserPlus className="w-4 h-4" />
            Thêm học sinh
          </button>
          <button
            type="button"
            onClick={handleDeleteClassroom}
            disabled={deleting}
            className="px-4 py-2.5 border border-red-200 dark:border-red-900/50 hover:bg-red-50 dark:hover:bg-red-950/30 text-red-600 dark:text-red-400 font-bold text-sm rounded-xl transition-all active:scale-[0.98] flex items-center gap-2 cursor-pointer disabled:opacity-50"
          >
            {deleting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Trash2 className="w-4 h-4" />
            )}
            Giải tán lớp
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 border-b border-zinc-200 dark:border-zinc-800 pb-1">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2.5 text-sm font-bold rounded-t-xl transition-colors flex items-center gap-2 cursor-pointer ${
                isActive
                  ? "text-violet-600 dark:text-violet-400 bg-violet-50 dark:bg-violet-950/30 border-b-2 border-violet-600"
                  : "text-zinc-500 dark:text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-300"
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-6 shadow-sm"
      >
        {activeTab === "students" && (
          <>
            {students.length === 0 ? (
              <div className="text-center py-12 text-zinc-400 dark:text-zinc-500">
                <Users className="w-10 h-10 mx-auto mb-3 opacity-40" />
                <p className="text-sm font-medium">Chưa có học sinh nào trong lớp.</p>
                <button
                  type="button"
                  onClick={() => setShowAddModal(true)}
                  className="mt-4 text-sm font-bold text-violet-600 dark:text-violet-400 hover:underline cursor-pointer"
                >
                  Thêm học sinh đầu tiên
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {students.map((student: User, idx: number) => (
                  <motion.div
                    key={student.id}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.04 }}
                    className="flex items-center justify-between gap-4 p-4 border border-zinc-100 dark:border-zinc-800 rounded-xl hover:bg-zinc-50 dark:hover:bg-zinc-800/30 transition-colors"
                  >
                    <div>
                      <p className="text-sm font-bold text-zinc-800 dark:text-zinc-200">
                        {student.full_name || `Học sinh #${student.id}`}
                      </p>
                      <p className="text-xs text-zinc-400 mt-0.5">{student.email}</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleRemoveStudent(student.id)}
                      disabled={removingId === student.id}
                      className="p-2 rounded-lg text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors cursor-pointer disabled:opacity-50"
                      title="Xóa khỏi lớp"
                    >
                      {removingId === student.id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <UserMinus className="w-4 h-4" />
                      )}
                    </button>
                  </motion.div>
                ))}
              </div>
            )}
          </>
        )}

        {activeTab === "progress" && (
          <StudentProgressTable students={progress} />
        )}

        {activeTab === "quizzes" && (
          <QuizResultTable attempts={quizAttempts} />
        )}
      </motion.div>

      <AddStudentModal
        open={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSubmit={handleAddStudent}
      />
    </div>
  );
}
