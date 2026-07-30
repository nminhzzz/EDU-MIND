"use client";

import React, { useEffect, useState, useRef } from "react";
import { userApi } from "@/services/user";
import { StudentProfileDetail, StudentGrade } from "@/types/user";
import { useAuth } from "@/hooks/use-auth";
import {
  User, Mail, GraduationCap, Clock, Calendar, Brain, Award, AlertTriangle,
  Sparkles, CheckCircle2, BookOpen, Compass, BarChart3, Loader2, Edit3, X, Save, Check, UploadCloud
} from "lucide-react";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";

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

const AVATAR_PRESETS = [
  "https://api.dicebear.com/7.x/bottts/svg?seed=EduMind1",
  "https://api.dicebear.com/7.x/avataaars/svg?seed=Minh",
  "https://api.dicebear.com/7.x/avataaars/svg?seed=Linh",
  "https://api.dicebear.com/7.x/open-peeps/svg?seed=Student",
  "https://api.dicebear.com/7.x/bottts/svg?seed=AI2026",
];

export const dynamic = "force-dynamic";

export default function StudentProfilePage() {
  const { checkAuth, updateCurrentUser } = useAuth();
  const [profile, setProfile] = useState<StudentProfileDetail | null>(null);
  const [loading, setLoading] = useState(true);

  // Edit Modal State
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [fullName, setFullName] = useState("");
  const [grade, setGrade] = useState<StudentGrade>("grade_10");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [saving, setSaving] = useState(false);
  const [uploadingAvatar, setUploadingAvatar] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadProfile = async () => {
    try {
      const res = await userApi.getProfile();
      setProfile(res.data);
      if (res.data?.user) {
        setFullName(res.data.user.full_name || "");
        setGrade(res.data.user.grade || "grade_10");
        setAvatarUrl(res.data.user.avatar_url || "");
      }
    } catch (err) {
      console.error(err);
      toast.error("Không thể tải thông tin hồ sơ học tập.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      toast.error("Tập tin tải lên phải là hình ảnh (PNG, JPG, WEBP, SVG).");
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      toast.error("Kích thước hình ảnh vượt quá 5MB.");
      return;
    }

    setUploadingAvatar(true);
    try {
      const res = await userApi.uploadAvatar(file);
      setAvatarUrl(res.data.avatar_url);
      toast.success("Tải ảnh đại diện từ máy tính thành công!");
    } catch (err) {
      console.error(err);
      toast.error("Không thể tải tệp ảnh lên server. Vui lòng thử lại.");
    } finally {
      setUploadingAvatar(false);
    }
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim()) {
      toast.warning("Vui lòng nhập họ và tên.");
      return;
    }

    setSaving(true);
    try {
      const res = await userApi.updateProfile({
        full_name: fullName.trim(),
        grade: grade,
        avatar_url: avatarUrl || undefined,
      });

      // Synchronously update global AuthContext user state INSTANTLY (0ms delay!)
      if (res.data && updateCurrentUser) {
        updateCurrentUser(res.data);
      }

      toast.success("Cập nhật thông tin cá nhân thành công!");
      setIsEditOpen(false);

      // Refresh both profile page and background auth state
      await Promise.all([loadProfile(), checkAuth()]);
    } catch (err) {
      console.error(err);
      toast.error("Cập nhật thất bại. Vui lòng kiểm tra lại.");
    } finally {
      setSaving(false);
    }
  };


  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Loader2 className="w-10 h-10 text-indigo-600 dark:text-indigo-400 animate-spin" />
        <span className="text-sm font-semibold text-zinc-500 dark:text-zinc-400">Đang tải hồ sơ học tập...</span>
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

        <div className="relative flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex flex-col md:flex-row items-center gap-6 text-center md:text-left">
            <div
              onClick={() => setIsEditOpen(true)}
              className="relative group cursor-pointer"
              title="Nhấn để đổi ảnh đại diện"
            >
              {user.avatar_url ? (
                <img
                  src={user.avatar_url}
                  alt={user.full_name || "Avatar"}
                  className="w-24 h-24 rounded-2xl object-cover bg-white/10 backdrop-blur-md border-2 border-white/40 shadow-lg shrink-0 group-hover:opacity-90 transition-opacity"
                />
              ) : (
                <div className="w-24 h-24 rounded-2xl bg-white/10 backdrop-blur-md border-2 border-white/40 flex items-center justify-center font-bold text-3xl shadow-lg shrink-0 text-white group-hover:bg-white/20 transition-colors">
                  {user.full_name ? user.full_name.charAt(0).toUpperCase() : "U"}
                </div>
              )}
              <div className="absolute inset-0 bg-black/40 rounded-2xl opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity text-xs font-bold text-white">
                <Edit3 className="w-5 h-5" />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-center md:justify-start gap-3">
                <h1 className="text-2xl md:text-3xl font-black tracking-tight">{user.full_name || "Chưa cập nhật họ tên"}</h1>
                <button
                  onClick={() => setIsEditOpen(true)}
                  className="p-1.5 rounded-lg bg-white/20 hover:bg-white/30 text-white transition-colors cursor-pointer"
                  title="Chỉnh sửa họ tên"
                >
                  <Edit3 className="w-4 h-4" />
                </button>
              </div>
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

          {/* Prominent Edit Profile Button */}
          <button
            onClick={() => setIsEditOpen(true)}
            className="px-6 py-3 bg-white text-indigo-700 hover:bg-indigo-50 font-black text-xs rounded-2xl transition-all flex items-center gap-2 cursor-pointer shadow-lg active:scale-95 shrink-0 z-10"
          >
            <Edit3 className="w-4.5 h-4.5 text-indigo-600" />
            Chỉnh sửa thông tin
          </button>
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
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                        <div className="space-y-1">
                          <h4 className="text-sm font-black text-zinc-850 dark:text-zinc-100">
                            {analytic.subject?.name || `Môn học (ID: ${analytic.subject_id})`}
                          </h4>
                          <span className="inline-block text-[10px] font-bold text-zinc-400">
                            Đã làm: {analytic.quizzes_completed} bài kiểm tra
                          </span>
                        </div>

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

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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

      {/* 4. Edit Profile Modal */}
      <AnimatePresence>
        {isEditOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.5 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsEditOpen(false)}
              className="fixed inset-0 bg-black"
            />

            {/* Hidden File Input for Avatar Upload */}
            <input
              type="file"
              ref={fileInputRef}
              accept="image/*"
              className="hidden"
              onChange={handleFileSelect}
            />

            {/* Modal Dialog Content */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="relative w-full max-w-lg bg-white dark:bg-zinc-900 rounded-3xl border border-zinc-200 dark:border-zinc-800 shadow-2xl p-6 md:p-8 space-y-6 z-10 text-left overflow-hidden"
            >
              <div className="flex items-center justify-between border-b border-zinc-100 dark:border-zinc-800 pb-4">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-xl bg-indigo-50 dark:bg-indigo-950/50 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                    <User className="w-4 h-4" />
                  </div>
                  <h2 className="text-lg font-black text-zinc-900 dark:text-white uppercase tracking-tight">
                    Chỉnh sửa thông tin cá nhân
                  </h2>
                </div>
                <button
                  onClick={() => setIsEditOpen(false)}
                  className="p-1.5 text-zinc-400 hover:text-zinc-900 dark:hover:text-white rounded-xl transition-colors cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleUpdateProfile} className="space-y-5">
                {/* Full Name */}
                <div className="space-y-2">
                  <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                    Họ và tên
                  </label>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Nhập họ và tên đầy đủ..."
                    className="w-full px-4 py-3 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 font-bold text-sm text-zinc-900 dark:text-white focus:outline-none focus:border-indigo-500 transition-colors"
                  />
                </div>

                {/* Grade Selection */}
                <div className="space-y-2">
                  <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                    Khối lớp / Trình độ học tập
                  </label>
                  <select
                    value={grade}
                    onChange={(e) => setGrade(e.target.value as StudentGrade)}
                    className="w-full px-4 py-3 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 font-bold text-sm text-zinc-900 dark:text-white focus:outline-none focus:border-indigo-500 transition-colors cursor-pointer"
                  >
                    {Object.entries(GRADE_MAP).map(([key, label]) => (
                      <option key={key} value={key}>
                        {label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Avatar Selection & Upload */}
                <div className="space-y-3">
                  <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                    Ảnh đại diện (Avatar)
                  </label>

                  {/* Upload from Computer Button */}
                  <button
                    type="button"
                    disabled={uploadingAvatar}
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full py-2.5 px-4 bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-950/40 dark:hover:bg-indigo-950/70 text-indigo-600 dark:text-indigo-300 font-bold text-xs rounded-xl border border-indigo-200/60 dark:border-indigo-800/40 flex items-center justify-center gap-2 cursor-pointer transition-all active:scale-[0.98] disabled:opacity-50"
                  >
                    {uploadingAvatar ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Đang tải ảnh từ máy tính lên...
                      </>
                    ) : (
                      <>
                        <UploadCloud className="w-4 h-4" />
                        Tải ảnh từ máy tính của bạn
                      </>
                    )}
                  </button>

                  {/* Preset Avatars Selection */}
                  <div className="space-y-1">
                    <span className="text-[10px] font-bold text-zinc-400 uppercase">Hoặc chọn ảnh đại diện mẫu:</span>
                    <div className="flex items-center gap-3 overflow-x-auto pb-1">
                      {AVATAR_PRESETS.map((url, idx) => (
                        <button
                          key={idx}
                          type="button"
                          onClick={() => setAvatarUrl(url)}
                          className={`w-12 h-12 rounded-xl p-1 border-2 transition-all cursor-pointer shrink-0 relative ${
                            avatarUrl === url
                              ? "border-indigo-600 bg-indigo-50 dark:bg-indigo-950/50 scale-105"
                              : "border-transparent hover:border-zinc-300 dark:hover:border-zinc-700"
                          }`}
                        >
                          <img src={url} alt={`Preset ${idx}`} className="w-full h-full object-cover rounded-lg" />
                          {avatarUrl === url && (
                            <div className="absolute -top-1 -right-1 w-4 h-4 bg-indigo-600 text-white rounded-full flex items-center justify-center">
                              <Check className="w-2.5 h-2.5" />
                            </div>
                          )}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* URL Input */}
                  <input
                    type="text"
                    value={avatarUrl}
                    onChange={(e) => setAvatarUrl(e.target.value)}
                    placeholder="Hoặc dán URL ảnh đại diện tùy chỉnh (https://...)"
                    className="w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 font-medium text-xs text-zinc-900 dark:text-white focus:outline-none focus:border-indigo-500 transition-colors"
                  />
                </div>

                {/* Submit Actions */}
                <div className="pt-4 flex items-center justify-end gap-3 border-t border-zinc-100 dark:border-zinc-800">
                  <button
                    type="button"
                    onClick={() => setIsEditOpen(false)}
                    className="px-5 py-2.5 text-xs font-bold text-zinc-500 hover:text-zinc-900 dark:hover:text-white cursor-pointer"
                  >
                    Hủy bỏ
                  </button>
                  <button
                    type="submit"
                    disabled={saving || uploadingAvatar}
                    className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl shadow-md shadow-indigo-500/20 active:scale-95 transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50"
                  >
                    {saving ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Đang lưu...
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4" />
                        Lưu thay đổi
                      </>
                    )}
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
