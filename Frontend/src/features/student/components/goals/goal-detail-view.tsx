"use client";

import React, { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  BookOpen,
  Calendar,
  CheckCircle2,
  Clock,
  Filter,
  Lock,
  Play,
  RotateCcw,
  Sparkles,
  Target,
  Trash2,
  AlertCircle,
} from "lucide-react";
import { toast } from "sonner";
import { ROUTES } from "@/features/student/constants";
import { goalApi } from "@/services/goal";
import { studyPlanApi, StudyPlan } from "@/services/study-plan";
import type { StudyGoal, Subject } from "@/features/student/types";
import { StudentLoadingState } from "@/features/student/components/common/student-loading-state";

interface GoalDetailViewProps {
  goalId: number;
}

function isFutureDate(dateStr: string): boolean {
  const planDate = new Date(dateStr);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  planDate.setHours(0, 0, 0, 0);
  return planDate.getTime() > today.getTime();
}

function isTodayDate(dateStr: string): boolean {
  const planDate = new Date(dateStr);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  planDate.setHours(0, 0, 0, 0);
  return planDate.getTime() === today.getTime();
}

function getStatusStyle(status: string) {
  switch (status) {
    case "active":
      return {
        label: "Đang thực hiện",
        className:
          "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-400 dark:border-emerald-800",
      };
    case "completed":
      return {
        label: "Đã hoàn thành",
        className:
          "bg-indigo-50 text-indigo-700 border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-400 dark:border-indigo-800",
      };
    case "cancelled":
      return {
        label: "Đã hủy",
        className:
          "bg-zinc-100 text-zinc-600 border-zinc-200 dark:bg-zinc-800 dark:text-zinc-400 dark:border-zinc-700",
      };
    default:
      return {
        label: status,
        className:
          "bg-zinc-100 text-zinc-600 border-zinc-200 dark:bg-zinc-800 dark:text-zinc-400 dark:border-zinc-700",
      };
  }
}

export function GoalDetailView({ goalId }: GoalDetailViewProps) {
  const router = useRouter();
  const [goal, setGoal] = useState<StudyGoal | null>(null);
  const [plans, setPlans] = useState<StudyPlan[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [deleting, setDeleting] = useState<boolean>(false);
  const [statusFilter, setStatusFilter] = useState<"all" | "todo" | "doing" | "done">("all");

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const [goalRes, plansRes, subjectsRes] = await Promise.all([
        goalApi.getGoal(goalId),
        goalApi.getGoalPlans(goalId),
        goalApi.getSubjects().catch(() => ({ data: [] as Subject[] })),
      ]);

      setGoal(goalRes.data);
      setPlans(plansRes.data || []);
      setSubjects(subjectsRes.data || []);
    } catch (err: unknown) {
      const errorMsg =
        err && typeof err === "object" && "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      toast.error(errorMsg || "Không thể tải thông tin chi tiết lộ trình.");
    } finally {
      setLoading(false);
    }
  }, [goalId]);

  useEffect(() => {
    if (goalId) {
      fetchData();
    }
  }, [goalId, fetchData]);

  const handleToggleTaskStatus = async (planId: number, currentStatus: "todo" | "doing" | "done") => {
    const nextStatusMap: Record<"todo" | "doing" | "done", "todo" | "doing" | "done"> = {
      todo: "doing",
      doing: "done",
      done: "todo",
    };
    const newStatus = nextStatusMap[currentStatus];

    try {
      setPlans((prev) =>
        prev.map((p) => (p.id === planId ? { ...p, status: newStatus } : p))
      );
      await studyPlanApi.updatePlanStatus(planId, newStatus);
      toast.success("Đã cập nhật trạng thái nhiệm vụ!");
    } catch (err) {
      toast.error("Không thể cập nhật trạng thái nhiệm vụ.");
      fetchData(); // Rollback on error
    }
  };

  const handleDeleteGoal = async () => {
    if (!confirm("Bạn có chắc chắn muốn xóa lộ trình học này cùng tất cả nhiệm vụ liên quan?")) {
      return;
    }

    try {
      setDeleting(true);
      await goalApi.deleteGoal(goalId);
      toast.success("Đã xóa lộ trình học thành công!");
      router.push(ROUTES.STUDENT_GOALS);
    } catch (err) {
      toast.error("Lỗi khi xóa lộ trình học tập.");
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto py-12 px-4 text-left">
        <StudentLoadingState message="Đang tải chi tiết lộ trình học tập..." />
      </div>
    );
  }

  if (!goal) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4 text-left space-y-6">
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-10 rounded-3xl text-center space-y-4 shadow-sm">
          <AlertCircle className="w-12 h-12 text-amber-500 mx-auto" />
          <h2 className="text-xl font-bold text-zinc-900 dark:text-white">Không tìm thấy lộ trình học</h2>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">
            Lộ trình này không tồn tại hoặc đã bị xóa.
          </p>
          <Link
            href={ROUTES.STUDENT_GOALS}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-xl font-bold text-xs shadow-md hover:bg-indigo-500 transition-all"
          >
            <ArrowLeft className="w-4 h-4" /> Quay lại danh sách lộ trình
          </Link>
        </div>
      </div>
    );
  }

  const subject = subjects.find((s) => s.id === goal.subject_id);
  const statusStyle = getStatusStyle(goal.status);

  // Statistics
  const totalTasks = plans.length;
  const completedTasks = plans.filter((p) => p.status === "done").length;
  const doingTasks = plans.filter((p) => p.status === "doing").length;
  const todoTasks = plans.filter((p) => p.status === "todo").length;
  const progressPercent = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  // Filtered plans
  const filteredPlans = plans.filter((p) => {
    if (statusFilter === "all") return true;
    return p.status === statusFilter;
  });

  return (
    <div className="max-w-5xl mx-auto py-6 px-4 sm:px-6 space-y-6 text-left">
      {/* Back button & Action Header */}
      <div className="flex items-center justify-between gap-4">
        <Link
          href={ROUTES.STUDENT_GOALS}
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold text-zinc-600 dark:text-zinc-300 bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 hover:border-indigo-300 dark:hover:border-indigo-700 transition-all shadow-sm"
        >
          <ArrowLeft className="w-4 h-4" />
          Quay lại Lộ trình
        </Link>
        <button
          type="button"
          onClick={handleDeleteGoal}
          disabled={deleting}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/60 hover:bg-red-100 transition-all cursor-pointer disabled:opacity-50"
        >
          <Trash2 className="w-3.5 h-3.5" />
          Xóa lộ trình
        </button>
      </div>

      {/* Main Goal Banner Card */}
      <div className="bg-gradient-to-br from-white via-indigo-50/20 to-indigo-100/30 dark:from-zinc-900 dark:via-zinc-900 dark:to-indigo-950/30 border border-zinc-200/80 dark:border-zinc-800 p-6 sm:p-8 rounded-3xl shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center text-[10px] font-extrabold tracking-wide text-indigo-700 dark:text-indigo-300 bg-indigo-100/80 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-900 px-2.5 py-1 rounded-lg uppercase">
                {subject?.code || "MÔN HỌC"}
              </span>
              <span
                className={`inline-flex items-center text-[10px] font-bold px-2.5 py-1 rounded-lg border ${statusStyle.className}`}
              >
                {statusStyle.label}
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-zinc-900 dark:text-white tracking-tight">
              {goal.title || `Lộ trình môn ${subject?.name || ""}`}
            </h1>
            {subject?.name && (
              <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400 flex items-center gap-1.5">
                <BookOpen className="w-4 h-4 text-indigo-500" />
                Môn học: <span className="font-semibold text-zinc-700 dark:text-zinc-200">{subject.name}</span>
              </p>
            )}
          </div>
        </div>

        {/* Progress & Target Stats Row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 border-t border-zinc-200/60 dark:border-zinc-800">
          <div className="p-4 rounded-2xl bg-white/80 dark:bg-zinc-950/50 border border-zinc-200/60 dark:border-zinc-800/80 space-y-1">
            <p className="text-[10px] font-extrabold uppercase tracking-wider text-zinc-400 flex items-center gap-1">
              <Target className="w-3.5 h-3.5 text-indigo-500" /> Mục tiêu điểm
            </p>
            <p className="text-xl font-black text-zinc-900 dark:text-white">
              {goal.target_score.toFixed(1)} <span className="text-xs text-zinc-400 font-bold">/ 10</span>
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-white/80 dark:bg-zinc-950/50 border border-zinc-200/60 dark:border-zinc-800/80 space-y-1">
            <p className="text-[10px] font-extrabold uppercase tracking-wider text-zinc-400 flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5 text-indigo-500" /> Hạn hoàn thành
            </p>
            <p className="text-base font-bold text-zinc-900 dark:text-white">
              {new Date(goal.deadline).toLocaleDateString("vi-VN", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
              })}
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-white/80 dark:bg-zinc-950/50 border border-zinc-200/60 dark:border-zinc-800/80 space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-[10px] font-extrabold uppercase tracking-wider text-zinc-400 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-indigo-500" /> Tiến độ hoàn thành
              </p>
              <span className="text-xs font-black text-indigo-600 dark:text-indigo-400">{progressPercent}%</span>
            </div>
            <div className="w-full h-2.5 bg-zinc-100 dark:bg-zinc-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-emerald-500 rounded-full transition-all duration-500"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
            <p className="text-[11px] text-zinc-500 dark:text-zinc-400 font-medium">
              Đã hoàn thành {completedTasks}/{totalTasks} bài học
            </p>
          </div>
        </div>
      </div>

      {/* Task Filters & Section Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <h2 className="text-lg font-black text-zinc-900 dark:text-white flex items-center gap-2">
            Lịch học & Nhiệm vụ chi tiết
            <Sparkles className="w-4 h-4 text-indigo-500" />
          </h2>
          <p className="text-xs text-zinc-500 dark:text-zinc-400">
            Danh sách các nhiệm vụ do AI tạo riêng theo ngày. Nhấn bài học để bắt đầu học với Gia sư AI.
          </p>
        </div>

        {/* Filter Buttons */}
        <div className="flex items-center gap-1 bg-white dark:bg-zinc-900 p-1 rounded-2xl border border-zinc-200/80 dark:border-zinc-800 shadow-sm shrink-0">
          <button
            type="button"
            onClick={() => setStatusFilter("all")}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              statusFilter === "all"
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200"
            }`}
          >
            Tất cả ({totalTasks})
          </button>
          <button
            type="button"
            onClick={() => setStatusFilter("todo")}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              statusFilter === "todo"
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200"
            }`}
          >
            Chưa làm ({todoTasks})
          </button>
          <button
            type="button"
            onClick={() => setStatusFilter("doing")}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              statusFilter === "doing"
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200"
            }`}
          >
            Đang làm ({doingTasks})
          </button>
          <button
            type="button"
            onClick={() => setStatusFilter("done")}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              statusFilter === "done"
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200"
            }`}
          >
            Đã xong ({completedTasks})
          </button>
        </div>
      </div>

      {/* Task List */}
      {filteredPlans.length === 0 ? (
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-10 rounded-3xl text-center shadow-sm space-y-3">
          <Filter className="w-10 h-10 text-zinc-300 dark:text-zinc-700 mx-auto" />
          <p className="text-sm font-bold text-zinc-600 dark:text-zinc-400">
            {statusFilter === "all"
              ? "Chưa có nhiệm vụ nào được phân bổ cho lộ trình này."
              : "Không tìm thấy nhiệm vụ phù hợp với bộ lọc."}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredPlans.map((plan, index) => {
            const isDone = plan.status === "done";
            const isDoing = plan.status === "doing";
            const isFuture = isFutureDate(plan.study_date);
            const isToday = isTodayDate(plan.study_date);

            return (
              <div
                key={plan.id}
                className={`group flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl border transition-all duration-200 bg-white dark:bg-zinc-900 ${
                  isDone
                    ? "border-emerald-200/80 dark:border-emerald-950/80 bg-emerald-50/20 dark:bg-emerald-950/10"
                    : isDoing
                    ? "border-indigo-300 dark:border-indigo-700/80 bg-indigo-50/30 dark:bg-indigo-950/20 shadow-sm"
                    : isFuture
                    ? "border-zinc-200/60 dark:border-zinc-800/60 opacity-80"
                    : "border-zinc-200/80 dark:border-zinc-800 hover:border-indigo-200 dark:hover:border-indigo-800"
                }`}
              >
                {/* Left Task Content */}
                <div className="flex items-start gap-3.5 flex-1 min-w-0">
                  {/* Status Toggle Icon Button */}
                  <button
                    type="button"
                    onClick={() => handleToggleTaskStatus(plan.id, plan.status)}
                    title="Đổi trạng thái bài học"
                    className={`mt-0.5 shrink-0 w-6 h-6 rounded-full flex items-center justify-center border transition-all cursor-pointer ${
                      isDone
                        ? "bg-emerald-500 border-emerald-500 text-white"
                        : isDoing
                        ? "bg-indigo-100 dark:bg-indigo-950 border-indigo-500 text-indigo-600 dark:text-indigo-400"
                        : "border-zinc-300 dark:border-zinc-700 text-transparent hover:border-indigo-400"
                    }`}
                  >
                    {isDone ? (
                      <CheckCircle2 className="w-4 h-4" />
                    ) : isDoing ? (
                      <RotateCcw className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <CheckCircle2 className="w-4 h-4 opacity-0 hover:opacity-50" />
                    )}
                  </button>

                  <div className="space-y-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-[11px] font-mono font-bold text-zinc-400 dark:text-zinc-500">
                        #{index + 1}
                      </span>
                      <span className="inline-flex items-center gap-1 text-[11px] font-bold text-zinc-500 dark:text-zinc-400 bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5 rounded-md">
                        <Calendar className="w-3 h-3 text-indigo-500" />
                        {new Date(plan.study_date).toLocaleDateString("vi-VN")}
                      </span>
                      {isToday && (
                        <span className="inline-flex items-center text-[10px] font-extrabold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-200 dark:border-indigo-900 px-2 py-0.5 rounded-md uppercase">
                          Hôm nay
                        </span>
                      )}
                      {isFuture && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold text-zinc-400 dark:text-zinc-500 bg-zinc-100 dark:bg-zinc-800/80 px-2 py-0.5 rounded-md">
                          <Lock className="w-2.5 h-2.5" /> Chưa đến ngày
                        </span>
                      )}
                      {plan.start_time && (
                        <span className="inline-flex items-center gap-1 text-[11px] font-medium text-zinc-400 font-mono">
                          <Clock className="w-3 h-3" />
                          {plan.start_time.slice(0, 5)} - {plan.end_time?.slice(0, 5)}
                        </span>
                      )}
                    </div>

                    <h3 className={`text-base font-extrabold leading-snug ${
                      isDone ? "text-zinc-500 line-through dark:text-zinc-500" : "text-zinc-900 dark:text-zinc-100"
                    }`}>
                      {plan.title}
                    </h3>

                    {plan.task_description && (
                      <p className="text-xs text-zinc-500 dark:text-zinc-400 line-clamp-2 leading-relaxed">
                        {plan.task_description}
                      </p>
                    )}
                  </div>
                </div>

                {/* Right Action Button */}
                <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
                  {isFuture ? (
                    <button
                      type="button"
                      disabled
                      title={`Nhiệm vụ này mở vào ngày ${new Date(plan.study_date).toLocaleDateString("vi-VN")}`}
                      className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-bold text-zinc-400 dark:text-zinc-500 bg-zinc-100 dark:bg-zinc-800/80 border border-zinc-200/80 dark:border-zinc-700/60 cursor-not-allowed select-none opacity-80"
                    >
                      <Lock className="w-3.5 h-3.5" />
                      Chưa đến ngày
                    </button>
                  ) : (
                    <Link
                      href={ROUTES.STUDENT_TASK(plan.id)}
                      className="inline-flex items-center gap-1.5 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold shadow-md shadow-indigo-500/20 active:scale-[0.98] transition-all"
                    >
                      <Play className="w-3.5 h-3.5 fill-current" />
                      Học bài này
                    </Link>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
