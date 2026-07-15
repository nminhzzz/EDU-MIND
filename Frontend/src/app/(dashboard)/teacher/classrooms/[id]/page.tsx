"use client";

import React, { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  BarChart3,
  BookOpen,
  ClipboardList,
  BrainCircuit,
  Eye,
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
import { quizService } from "@/features/student/services/quiz";
import type { StudentQuiz } from "@/features/student/types/quiz";
import classroomApi, {
  ClassroomDetail,
  ClassroomQuizAttempt,
  ClassroomStudentProgress,
} from "@/services/classroom";
import { parseApiError } from "@/utils/api-error";
import { User } from "@/types/user";

type TabId = "students" | "progress" | "quizzes" | "classroom_quizzes";

const TABS: { id: TabId; label: string; icon: React.ElementType }[] = [
  { id: "students", label: "Danh sách học sinh", icon: Users },
  { id: "progress", label: "Tiến độ học tập", icon: BarChart3 },
  { id: "quizzes", label: "Kết quả bài thi", icon: Trophy },
  { id: "classroom_quizzes", label: "Đề thi & Bài tập", icon: ClipboardList },
];

export default function ClassroomDetailPage() {
  const params = useParams();
  const router = useRouter();
  const classroomId = Number(params.id);

  const [classroom, setClassroom] = useState<ClassroomDetail | null>(null);
  const [progress, setProgress] = useState<ClassroomStudentProgress[]>([]);
  const [quizAttempts, setQuizAttempts] = useState<ClassroomQuizAttempt[]>([]);
  const [quizzes, setQuizzes] = useState<any[]>([]);
  const [previewQuiz, setPreviewQuiz] = useState<StudentQuiz | null>(null);
  const [loadingPreviewId, setLoadingPreviewId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<TabId>("students");
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [removingId, setRemovingId] = useState<number | null>(null);
  const [deleting, setDeleting] = useState(false);

  // Modal tạo đề thi AI:
  const [showGenModal, setShowGenModal] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState("medium");
  const [totalQuestions, setTotalQuestions] = useState(5);
  const [deadline, setDeadline] = useState("");
  const [includeEssay, setIncludeEssay] = useState(false);
  const [essayCount, setEssayCount] = useState(2);

  const handlePreviewQuiz = async (quizId: number) => {
    setLoadingPreviewId(quizId);
    try {
      const res = await quizService.getReview(quizId);
      setPreviewQuiz(res.data);
    } catch (err) {
      toast.error(parseApiError(err, "Không thể tải chi tiết đề thi."));
    } finally {
      setLoadingPreviewId(null);
    }
  };

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

  const fetchQuizzes = useCallback(async () => {
    const res = await classroomApi.getQuizzes(classroomId);
    setQuizzes(res.data);
  }, [classroomId]);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchClassroom(),
        fetchProgress(),
        fetchQuizAttempts(),
        fetchQuizzes(),
      ]);
    } catch (err) {
      console.error("Lỗi tải chi tiết lớp học:", err);
      toast.error("Không thể tải thông tin lớp học.");
    } finally {
      setLoading(false);
    }
  }, [fetchClassroom, fetchProgress, fetchQuizAttempts, fetchQuizzes]);

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

  const handleGenerateQuiz = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) {
      toast.error("Vui lòng nhập chủ đề kiểm tra.");
      return;
    }
    if (!classroom?.subject?.id) {
      toast.error("Lớp học này chưa được gắn môn học nào.");
      return;
    }

    setGenerating(true);
    try {
      const res = await classroomApi.generateQuiz(classroomId, {
        subject_id: classroom.subject.id,
        topic,
        difficulty,
        total_questions: totalQuestions,
        deadline: deadline || undefined,
        include_essay: includeEssay,
        essay_count: includeEssay ? essayCount : 0,
      });
      toast.success("Đã dùng AI sinh đề và giao bài kiểm tra thành công!");
      setShowGenModal(false);
      setTopic("");
      setDeadline("");
      setIncludeEssay(false);
      setEssayCount(2);
      await fetchAll();
      if (res.data) {
        setPreviewQuiz(res.data);
      }
    } catch (err) {
      toast.error(parseApiError(err, "Không thể sinh đề thi bằng AI."));
    } finally {
      setGenerating(false);
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

        {activeTab === "classroom_quizzes" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center pb-2 border-b border-zinc-100 dark:border-zinc-800">
              <h3 className="font-extrabold text-sm text-zinc-800 dark:text-zinc-200">
                Danh sách đề kiểm tra đã giao
              </h3>
              <button
                type="button"
                onClick={() => setShowGenModal(true)}
                className="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white font-bold text-xs rounded-xl shadow-md transition-all active:scale-[0.98] cursor-pointer flex items-center gap-1.5"
              >
                <BrainCircuit className="w-3.5 h-3.5" />
                Tạo đề thi bằng AI
              </button>
            </div>

            {quizzes.length === 0 ? (
              <div className="text-center py-12 text-zinc-400 dark:text-zinc-500">
                <ClipboardList className="w-10 h-10 mx-auto mb-3 opacity-40" />
                <p className="text-sm font-medium">Chưa có đề thi hay bài tập nào được giao cho lớp này.</p>
                <button
                  type="button"
                  onClick={() => setShowGenModal(true)}
                  className="mt-4 text-sm font-bold text-violet-600 dark:text-violet-400 hover:underline cursor-pointer"
                >
                  Tạo đề thi đầu tiên bằng AI
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {quizzes.map((q) => (
                  <div
                    key={q.id}
                    className="p-5 border border-zinc-100 dark:border-zinc-800 rounded-xl bg-zinc-50/50 dark:bg-zinc-950/20 flex flex-col justify-between hover:border-zinc-200 dark:hover:border-zinc-700 transition-all"
                  >
                    <div className="space-y-2 text-left">
                      <div className="flex justify-between items-center">
                        <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-violet-50 text-violet-600 dark:bg-violet-950/40 dark:text-violet-400">
                          {q.difficulty === "easy" ? "Dễ" : q.difficulty === "hard" ? "Khó" : "Trung bình"}
                        </span>
                        <span className="text-[11px] text-zinc-400 dark:text-zinc-500">
                          ID: #{q.id}
                        </span>
                      </div>
                      <h4 className="font-extrabold text-sm text-zinc-900 dark:text-white line-clamp-1">
                        {q.title}
                      </h4>
                      <p className="text-xs text-zinc-505 dark:text-zinc-400 mt-1">
                        Số câu hỏi: <strong className="text-zinc-700 dark:text-zinc-200">{q.total_questions}</strong> câu
                      </p>
                      {q.deadline && (
                        <p className="text-[11px] text-zinc-450 dark:text-zinc-500 mt-1">
                          Hạn chót: {new Date(q.deadline).toLocaleDateString("vi-VN", {
                            hour: "2-digit",
                            minute: "2-digit",
                            day: "2-digit",
                            month: "2-digit",
                          })}
                        </p>
                      )}
                    </div>
                    <div className="mt-4 pt-3 border-t border-zinc-100 dark:border-zinc-800 flex justify-end">
                      <button
                        type="button"
                        onClick={() => handlePreviewQuiz(q.id)}
                        disabled={loadingPreviewId === q.id}
                        className="px-3 py-1.5 bg-zinc-100 hover:bg-zinc-200 dark:bg-zinc-850 dark:hover:bg-zinc-850/80 text-zinc-700 dark:text-zinc-300 font-bold text-[11px] rounded-lg transition-all active:scale-[0.98] cursor-pointer flex items-center gap-1 disabled:opacity-50"
                      >
                        {loadingPreviewId === q.id ? (
                          <>
                            <Loader2 className="w-3 h-3 animate-spin" />
                            Đang tải...
                          </>
                        ) : (
                          <>
                            <Eye className="w-3 h-3" />
                            Xem chi tiết đề
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </motion.div>

      <AddStudentModal
        open={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSubmit={handleAddStudent}
      />

      {/* AI Quiz Generation Modal */}
      {showGenModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-6 w-full max-w-md shadow-2xl space-y-4"
          >
            <div className="flex justify-between items-center border-b border-zinc-100 dark:border-zinc-800 pb-3">
              <h3 className="font-black text-base text-zinc-900 dark:text-white flex items-center gap-2">
                <BrainCircuit className="w-5 h-5 text-violet-600" />
                Tạo đề thi bằng AI
              </h3>
              <button
                type="button"
                onClick={() => setShowGenModal(false)}
                className="text-zinc-400 hover:text-zinc-500 dark:text-zinc-500 dark:hover:text-zinc-400 text-sm font-bold cursor-pointer"
              >
                Đóng
              </button>
            </div>

            <form onSubmit={handleGenerateQuiz} className="space-y-4 text-left">
              <div className="space-y-1.5">
                <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase">
                  Chủ đề kiểm tra:
                </label>
                <input
                  type="text"
                  placeholder="Ví dụ: Lượng giác, Đạo hàm, Mảng trong Java..."
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-medium text-sm focus:outline-none focus:border-violet-500 text-zinc-900 dark:text-white"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase">
                    Độ khó:
                  </label>
                  <select
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value)}
                    className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-bold text-sm focus:outline-none focus:border-violet-500 text-zinc-900 dark:text-white"
                  >
                    <option value="easy">Dễ</option>
                    <option value="medium">Trung bình</option>
                    <option value="hard">Khó</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase">
                    Số câu hỏi:
                  </label>
                  <select
                    value={totalQuestions}
                    onChange={(e) => setTotalQuestions(Number(e.target.value))}
                    className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-bold text-sm focus:outline-none focus:border-violet-500 text-zinc-900 dark:text-white"
                  >
                    <option value={5}>5 câu</option>
                    <option value={10}>10 câu</option>
                    <option value={15}>15 câu</option>
                    <option value={20}>20 câu</option>
                  </select>
                </div>
              </div>

              <div className="border-t border-zinc-100 dark:border-zinc-800 pt-3 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-zinc-650 dark:text-zinc-400 uppercase">
                    Bao gồm câu hỏi tự luận:
                  </span>
                  <input
                    type="checkbox"
                    checked={includeEssay}
                    onChange={(e) => setIncludeEssay(e.target.checked)}
                    className="w-4 h-4 text-violet-600 focus:ring-violet-500 border-zinc-300 rounded cursor-pointer"
                  />
                </div>

                {includeEssay && (
                  <div className="space-y-1.5">
                    <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase">
                      Số câu hỏi tự luận:
                    </label>
                    <select
                      value={essayCount}
                      onChange={(e) => setEssayCount(Number(e.target.value))}
                      className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-bold text-sm focus:outline-none focus:border-violet-500 text-zinc-900 dark:text-white"
                    >
                      <option value={1}>1 câu</option>
                      <option value={2}>2 câu (Mặc định)</option>
                      <option value={3}>3 câu</option>
                      <option value={4}>4 câu</option>
                      <option value={5}>5 câu</option>
                    </select>
                  </div>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase">
                  Hạn chót nộp bài (Không bắt buộc):
                </label>
                <input
                  type="datetime-local"
                  value={deadline}
                  onChange={(e) => setDeadline(e.target.value)}
                  className="w-full px-4 py-2.5 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-medium text-sm focus:outline-none focus:border-violet-500 text-zinc-900 dark:text-white"
                />
              </div>

              <button
                type="submit"
                disabled={generating}
                className="w-full py-3 bg-violet-600 hover:bg-violet-500 text-white font-bold text-sm rounded-xl transition-all disabled:opacity-50 flex items-center justify-center gap-2 cursor-pointer shadow-md shadow-violet-500/20"
              >
                {generating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Đang thiết kế đề thi AI...
                  </>
                ) : (
                  <>
                    <BrainCircuit className="w-4 h-4" />
                    Sinh đề & Giao bài ngay
                  </>
                )}
              </button>
            </form>
          </motion.div>
        </div>
      )}

      {/* AI Quiz Preview Modal for Teacher */}
      <QuizPreviewModal
        open={!!previewQuiz}
        onClose={() => setPreviewQuiz(null)}
        quiz={previewQuiz}
      />
    </div>
  );
}

interface QuizPreviewModalProps {
  open: boolean;
  onClose: () => void;
  quiz: StudentQuiz | null;
}

export function QuizPreviewModal({ open, onClose, quiz }: QuizPreviewModalProps) {
  if (!open || !quiz) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl w-full max-w-2xl max-h-[85vh] shadow-2xl flex flex-col"
      >
        <div className="flex justify-between items-center border-b border-zinc-100 dark:border-zinc-800 p-5">
          <div className="text-left">
            <h3 className="font-black text-base text-zinc-900 dark:text-white line-clamp-1">
              {quiz.title}
            </h3>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-[10px] font-bold uppercase tracking-wider bg-violet-50 text-violet-600 dark:bg-violet-950/40 dark:text-violet-400 px-2 py-0.5 rounded">
                Độ khó: {quiz.difficulty === "easy" ? "Dễ" : quiz.difficulty === "hard" ? "Khó" : "Trung bình"}
              </span>
              <span className="text-[10px] text-zinc-400 dark:text-zinc-500">
                Tổng số: {quiz.total_questions} câu hỏi
              </span>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-zinc-400 hover:text-zinc-500 dark:text-zinc-500 dark:hover:text-zinc-400 text-sm font-bold cursor-pointer"
          >
            Đóng
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6 text-left">
          {quiz.questions.map((q, qIdx) => {
            const isEssay = q.question_type === "essay";
            return (
              <div
                key={qIdx}
                className="p-5 border border-zinc-100 dark:border-zinc-850 rounded-xl bg-zinc-50/30 dark:bg-zinc-950/10 space-y-4"
              >
                <div className="flex items-start gap-2.5">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-violet-100 dark:bg-violet-950/60 text-violet-600 dark:text-violet-400 flex items-center justify-center text-xs font-bold mt-0.5">
                    {qIdx + 1}
                  </span>
                  <div className="space-y-1">
                    <p className="text-sm font-extrabold text-zinc-900 dark:text-white leading-relaxed">
                      {q.question_text}
                    </p>
                    {isEssay && (
                      <span className="inline-block text-[10px] font-bold uppercase tracking-wider bg-zinc-100 text-zinc-650 dark:bg-zinc-800 dark:text-zinc-400 px-1.5 py-0.5 rounded">
                        Tự luận
                      </span>
                    )}
                  </div>
                </div>

                {!isEssay && q.options && q.options.length > 0 && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pl-8">
                    {q.options.map((opt) => {
                      const isCorrect = opt.key.trim().toUpperCase() === q.correct_answer?.trim().toUpperCase();
                      return (
                        <div
                          key={opt.key}
                          className={`p-3 rounded-lg border text-xs font-semibold transition-all flex items-start gap-2 ${
                            isCorrect
                              ? "bg-emerald-50/50 border-emerald-250 text-emerald-800 dark:bg-emerald-950/20 dark:border-emerald-900/50 dark:text-emerald-400"
                              : "bg-white border-zinc-100 text-zinc-700 dark:bg-zinc-950 dark:border-zinc-850 dark:text-zinc-300"
                          }`}
                        >
                          <span
                            className={`w-5 h-5 rounded-full flex-shrink-0 flex items-center justify-center text-[10px] font-bold ${
                              isCorrect
                                ? "bg-emerald-500 text-white"
                                : "bg-zinc-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400"
                            }`}
                          >
                            {opt.key}
                          </span>
                          <span className="flex-1 pt-0.5 leading-snug">{opt.value}</span>
                        </div>
                      );
                    })}
                  </div>
                )}

                {isEssay && q.correct_answer && (
                  <div className="pl-8 space-y-1.5">
                    <h5 className="text-[10px] font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">
                      Đáp án mẫu gợi ý:
                    </h5>
                    <div className="p-3.5 rounded-lg bg-zinc-100 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 text-xs text-zinc-750 dark:text-zinc-350 font-medium leading-relaxed whitespace-pre-line">
                      {q.correct_answer}
                    </div>
                  </div>
                )}

                {q.explanation && (
                  <div className="pl-8 space-y-1.5">
                    <h5 className="text-[10px] font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">
                      Giải thích đáp án:
                    </h5>
                    <div className="p-3.5 rounded-lg bg-violet-50/40 dark:bg-violet-950/10 border border-violet-100 dark:border-violet-900/30 text-xs text-zinc-650 dark:text-zinc-400 font-medium leading-relaxed">
                      {q.explanation}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <div className="border-t border-zinc-100 dark:border-zinc-800 p-4 flex justify-end bg-zinc-50/50 dark:bg-zinc-900/50 rounded-b-2xl">
          <button
            type="button"
            onClick={onClose}
            className="px-5 py-2 bg-zinc-100 hover:bg-zinc-200 dark:bg-zinc-800 dark:hover:bg-zinc-750 text-zinc-700 dark:text-zinc-300 font-bold text-xs rounded-xl transition-all cursor-pointer"
          >
            Đóng
          </button>
        </div>
      </motion.div>
    </div>
  );
}
