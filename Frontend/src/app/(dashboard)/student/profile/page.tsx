"use client";

import React, { useEffect, useState } from "react";
import { userApi } from "@/services/user";
import { StudentProfileDetail, StudentGrade } from "@/types/user";
import { 
  User, Mail, GraduationCap, Clock, Calendar, Brain, Award, AlertTriangle, 
  Sparkles, CheckCircle2, BookOpen, Compass, ChevronRight, BarChart3, Loader2 
} from "lucide-react";
import { toast } from "sonner";

const GRADE_MAP: Record<StudentGrade, string> = {
  grade_6: "Lớp 6 (THCS)",
  grade_7: "Lớp 7 (THCS)",
  grade_8: "Lớp 8 (THCS)",
  grade_9: "Lớp 9 (THCS)",
  grade_10: "Lớp 10 (THPT)",
  grade_11: "Lớp 11 (THPT)",
  grade_12: "Lớp 12 (THPT)",
  uni_year_1: "Sinh viên Năm 1 (Đại học)",
  uni_year_2: "Sinh viên Năm 2 (Đại học)",
  uni_year_3: "Sinh viên Năm 3 (Đại học)",
  uni_year_4: "Sinh viên Năm 4 (Đại học)",
};

const WEEKDAY_VN: Record<string, string> = {
  mon: "Thứ Hai",
  tue: "Thứ Ba",
  wed: "Thứ Tư",
  thu: "Thứ Năm",
  fri: "Thứ Sáu",
  sat: "Thứ Bảy",
  sun: "Chủ Nhật",
};

export default function StudentProfilePage() {
  const [profile, setProfile] = useState<StudentProfileDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const res = await userApi.getProfile();
        setProfile(res.data);
      } catch (err) {
        console.error(err);
        toast.error("Không thể tải thông tin hồ sơ học tập.");
      } finally {
        setLoading(false);
      }
    };
    loadProfile();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Loader2 className="w-10 h-10 text-indigo-600 animate-spin" />
        <span className="text-sm font-semibold text-zinc-500">Đang tải hồ sơ học tập...</span>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="text-center py-12">
        <p className="text-zinc-500 font-semibold">Không tìm thấy thông tin hồ sơ.</p>
      </div>
    );
  }

  const { user, preference, learning_analytics } = profile;

  // Format schedule
  const activeDays = preference?.available_schedule
    ? Object.entries(preference.available_schedule)
        .filter(([_, active]) => active)
        .map(([day]) => WEEKDAY_VN[day] || day)
    : [];

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-12 animate-fadeIn text-left">
      {/* 1. Header Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-violet-600 via-indigo-600 to-blue-600 p-8 text-white shadow-xl shadow-indigo-500/20">
        <div className="absolute right-0 top-0 -mt-12 -mr-12 w-64 h-64 bg-white/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute left-0 bottom-0 -mb-16 -ml-16 w-80 h-80 bg-blue-400/20 rounded-full blur-3xl pointer-events-none" />

        <div className="relative flex flex-col md:flex-row items-center gap-6">
          <div className="w-24 h-24 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 flex items-center justify-center font-bold text-3xl shadow-lg shrink-0 text-white">
            {user.full_name ? user.full_name.charAt(0).toUpperCase() : "U"}
          </div>
          <div className="space-y-2 text-center md:text-left flex-1">
            <h1 className="text-2xl md:text-3xl font-black tracking-tight">{user.full_name || "Chưa cập nhật họ tên"}</h1>
            <div className="flex flex-wrap justify-center md:justify-start gap-3 text-sm font-medium text-indigo-100">
              <span className="flex items-center gap-1.5 px-3 py-1 bg-white/10 rounded-xl backdrop-blur-sm">
                <Mail className="w-4 h-4" />
                {user.email}
              </span>
              <span className="flex items-center gap-1.5 px-3 py-1 bg-white/10 rounded-xl backdrop-blur-sm">
                <GraduationCap className="w-4 h-4" />
                {user.grade ? GRADE_MAP[user.grade] : "Chưa cập nhật lớp"}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* 2. Cấu hình học tập (Left Side) */}
        <div className="lg:col-span-1 space-y-6">
          <div className="p-6 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-sm space-y-6">
            <h3 className="text-sm font-black text-zinc-850 dark:text-zinc-150 uppercase tracking-wider flex items-center gap-2 border-b border-zinc-100 dark:border-zinc-800 pb-3">
              <Compass className="w-4.5 h-4.5 text-indigo-500" />
              Cấu hình học tập
            </h3>

            <div className="space-y-4">
              <div className="flex items-start gap-3.5">
                <div className="w-9 h-9 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 flex items-center justify-center text-indigo-600 dark:text-indigo-400 shrink-0">
                  <Clock className="w-4.5 h-4.5" />
                </div>
                <div>
                  <h4 className="text-[10px] font-black text-zinc-400 uppercase tracking-wider">Mục tiêu học mỗi ngày</h4>
                  <p className="text-xs font-bold text-zinc-850 dark:text-zinc-100 mt-0.5">
                    {preference?.study_hours_per_day || 2} giờ / ngày
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3.5">
                <div className="w-9 h-9 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 flex items-center justify-center text-indigo-600 dark:text-indigo-400 shrink-0">
                  <BookOpen className="w-4.5 h-4.5" />
                </div>
                <div>
                  <h4 className="text-[10px] font-black text-zinc-400 uppercase tracking-wider">Khung giờ ưa thích</h4>
                  <p className="text-xs font-bold text-zinc-850 dark:text-zinc-100 mt-0.5 capitalize">
                    {preference?.preferred_study_time === "morning"
                      ? "Buổi Sáng"
                      : preference?.preferred_study_time === "afternoon"
                      ? "Buổi Chiều"
                      : "Buổi Tối"}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3.5">
                <div className="w-9 h-9 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 flex items-center justify-center text-indigo-600 dark:text-indigo-400 shrink-0">
                  <Calendar className="w-4.5 h-4.5" />
                </div>
                <div className="flex-1">
                  <h4 className="text-[10px] font-black text-zinc-400 uppercase tracking-wider">Lịch học trong tuần</h4>
                  {activeDays.length > 0 ? (
                    <div className="flex flex-wrap gap-1.5 mt-1.5">
                      {activeDays.map((day, idx) => (
                        <span key={idx} className="px-2 py-0.5 text-[9px] font-black bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 rounded-md">
                          {day}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-zinc-400 italic mt-0.5">Chưa cài đặt lịch</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 3. Báo cáo học lực & Điểm mạnh/yếu (Right Side) */}
        <div className="lg:col-span-2 space-y-6">
          <div className="p-6 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-sm space-y-6">
            <h3 className="text-sm font-black text-zinc-850 dark:text-zinc-150 uppercase tracking-wider flex items-center gap-2 border-b border-zinc-100 dark:border-zinc-800 pb-3">
              <BarChart3 className="w-4.5 h-4.5 text-violet-500" />
              Báo cáo học lực theo môn
            </h3>

            {learning_analytics.length > 0 ? (
              <div className="space-y-8">
                {learning_analytics.map((analytic) => {
                  const score = analytic.average_score;
                  const isHigh = score >= 8.0;
                  const isMedium = score >= 5.0;
                  const ringColor = isHigh 
                    ? "text-emerald-500 dark:text-emerald-400" 
                    : isMedium 
                    ? "text-indigo-500 dark:text-indigo-400" 
                    : "text-amber-500 dark:text-amber-400";

                  return (
                    <div key={analytic.id} className="p-5 rounded-2xl border border-zinc-150 dark:border-zinc-800/80 bg-zinc-50/50 dark:bg-zinc-900/50 space-y-5">
                      {/* Subject GPA Info Header */}
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                        <div className="space-y-1">
                          <h4 className="text-sm font-black text-zinc-850 dark:text-zinc-100">
                            {analytic.subject?.name || `Môn học (ID: ${analytic.subject_id})`}
                          </h4>
                          <span className="inline-block text-[10px] font-bold text-zinc-400">
                            Đã làm: {analytic.quizzes_completed} bài kiểm tra
                          </span>
                        </div>

                        {/* GPA Circle Progress Badge */}
                        <div className="flex items-center gap-3 bg-white dark:bg-zinc-950 p-2.5 rounded-xl border border-zinc-100 dark:border-zinc-800 shrink-0">
                          <div className="relative w-10 h-10 flex items-center justify-center">
                            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                              <path
                                className="text-zinc-100 dark:text-zinc-800"
                                strokeWidth="3"
                                stroke="currentColor"
                                fill="none"
                                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                              />
                              <path
                                className={ringColor}
                                strokeDasharray={`${score * 10}, 100`}
                                strokeWidth="3"
                                strokeLinecap="round"
                                stroke="currentColor"
                                fill="none"
                                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                              />
                            </svg>
                            <span className="absolute text-[10px] font-black text-zinc-800 dark:text-zinc-200">
                              {score.toFixed(1)}
                            </span>
                          </div>
                          <div className="text-left leading-none">
                            <span className="text-[8px] font-black uppercase text-zinc-400 block tracking-wider">GPA môn</span>
                            <span className={`text-[10px] font-black uppercase ${ringColor}`}>
                              {isHigh ? "Giỏi" : isMedium ? "Khá" : "Cần cố gắng"}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Grid Strengths and Weaknesses topics */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Strengths */}
                        <div className="p-3.5 rounded-xl bg-emerald-50/20 dark:bg-emerald-950/10 border border-emerald-100/50 dark:border-emerald-900/30 space-y-2">
                          <h5 className="text-[10px] font-black uppercase text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            Điểm mạnh / Chủ đề nắm vững
                          </h5>
                          {analytic.strong_topics && analytic.strong_topics.length > 0 ? (
                            <div className="flex flex-wrap gap-1.5">
                              {analytic.strong_topics.map((t: any, idx) => (
                                <span key={idx} className="px-2 py-0.5 text-[10px] font-bold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 rounded-md">
                                  {typeof t === "string" ? t : t.topic || ""}
                                </span>
                              ))}
                            </div>
                          ) : (
                            <p className="text-[10px] text-zinc-400 italic">Chưa xác định</p>
                          )}
                        </div>

                        {/* Weaknesses */}
                        <div className="p-3.5 rounded-xl bg-amber-50/20 dark:bg-amber-950/10 border border-amber-100/50 dark:border-amber-900/30 space-y-2">
                          <h5 className="text-[10px] font-black uppercase text-amber-700 dark:text-amber-400 flex items-center gap-1.5">
                            <AlertTriangle className="w-3.5 h-3.5" />
                            Chủ đề cần cải thiện
                          </h5>
                          {analytic.weak_topics && analytic.weak_topics.length > 0 ? (
                            <div className="flex flex-wrap gap-1.5">
                              {analytic.weak_topics.map((t: any, idx) => (
                                <span key={idx} className="px-2 py-0.5 text-[10px] font-bold bg-amber-50/60 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 rounded-md">
                                  {typeof t === "string" ? t : t.topic || ""}
                                </span>
                              ))}
                            </div>
                          ) : (
                            <p className="text-[10px] text-emerald-600 font-semibold italic">Không có chủ đề yếu nào!</p>
                          )}
                        </div>
                      </div>

                      {/* AI Tutor Insights */}
                      {analytic.ai_feedback && (
                        <div className="p-4 rounded-xl bg-violet-50/20 dark:bg-violet-950/15 border border-violet-100/50 dark:border-violet-900/30 text-left relative overflow-hidden">
                          <div className="flex items-center gap-1.5 text-xs font-black text-violet-600 dark:text-violet-400 uppercase tracking-wider mb-2">
                            <Sparkles className="w-4 h-4 animate-pulse shrink-0" />
                            Nhận xét từ AI Tutor
                          </div>
                          <p className="text-xs text-zinc-700 dark:text-zinc-300 leading-relaxed italic font-medium">
                            "{analytic.ai_feedback}"
                          </p>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center p-8 text-center bg-zinc-50 dark:bg-zinc-950/20 rounded-2xl border border-dashed border-zinc-200 dark:border-zinc-800">
                <Brain className="w-10 h-10 text-zinc-300 mb-2" />
                <p className="text-xs text-zinc-500 font-bold">Chưa có đủ dữ liệu học tập để tổng hợp báo cáo học lực.</p>
                <p className="text-[10px] text-zinc-400 mt-1">Hãy tham gia làm các bài kiểm tra ôn luyện môn học để AI xây dựng lộ trình và báo cáo điểm mạnh/yếu.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
