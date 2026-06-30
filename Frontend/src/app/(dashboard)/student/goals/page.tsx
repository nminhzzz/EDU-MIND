"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ROUTES } from "@/constants/routes";
import { goalApi, Subject, DraftResponse, StudyGoalResponse } from "@/services/goal";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { Trash2, Plus, Calendar, AlertCircle } from "lucide-react";

type Step = "checking" | "list_goals" | "setup_schedule" | "create_goal" | "roadmap_draft" | "success";

interface SlotDetail {
  enabled: boolean;
  start: string;
  end: string;
}

interface DaySchedule {
  morning: SlotDetail;
  afternoon: SlotDetail;
  evening: SlotDetail;
}

export default function GoalsPage() {
  const router = useRouter();

  const [step, setStep] = useState<Step>("checking");
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(false);
  const [goals, setGoals] = useState<StudyGoalResponse[]>([]);
  const [goalsLoading, setGoalsLoading] = useState(false);

  // 1. Dữ liệu Lịch rảnh (Preferences) - Mỗi buổi rảnh rỗi có trạng thái bật/tắt và chọn khoảng giờ cụ thể
  const [studyHours, setStudyHours] = useState<number>(2);
  const [preferredTime, setPreferredTime] = useState<string>("evening");
  const [schedule, setSchedule] = useState<Record<string, DaySchedule>>({
    mon: {
      morning: { enabled: true, start: "08:00", end: "12:00" },
      afternoon: { enabled: false, start: "13:00", end: "17:00" },
      evening: { enabled: true, start: "18:00", end: "22:00" }
    },
    tue: {
      morning: { enabled: true, start: "08:00", end: "12:00" },
      afternoon: { enabled: true, start: "13:00", end: "17:00" },
      evening: { enabled: true, start: "18:00", end: "22:00" }
    },
    wed: {
      morning: { enabled: false, start: "08:00", end: "12:00" },
      afternoon: { enabled: true, start: "13:00", end: "17:00" },
      evening: { enabled: true, start: "18:00", end: "22:00" }
    },
    thu: {
      morning: { enabled: true, start: "08:00", end: "12:00" },
      afternoon: { enabled: false, start: "13:00", end: "17:00" },
      evening: { enabled: true, start: "18:00", end: "22:00" }
    },
    fri: {
      morning: { enabled: true, start: "08:00", end: "12:00" },
      afternoon: { enabled: true, start: "13:00", end: "17:00" },
      evening: { enabled: false, start: "18:00", end: "22:00" }
    },
    sat: {
      morning: { enabled: false, start: "08:00", end: "12:00" },
      afternoon: { enabled: false, start: "13:00", end: "17:00" },
      evening: { enabled: false, start: "18:00", end: "22:00" }
    },
    sun: {
      morning: { enabled: false, start: "08:00", end: "12:00" },
      afternoon: { enabled: false, start: "13:00", end: "17:00" },
      evening: { enabled: false, start: "18:00", end: "22:00" }
    }
  });

  // 2. Dữ liệu Goal Form
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>("");
  const [targetScore, setTargetScore] = useState<number>(8);
  const [deadline, setDeadline] = useState<string>("");
  const [userMessage, setUserMessage] = useState<string>("");

  // 3. Dữ liệu Lộ trình nháp (Draft Roadmap)
  const [draft, setDraft] = useState<DraftResponse | null>(null);
  const [chatMessage, setChatMessage] = useState<string>("");
  const [chatLoading, setChatLoading] = useState(false);

  // Kiểm tra cấu hình lịch học khi mount
  useEffect(() => {
    const checkScheduleAndLoadData = async () => {
      try {
        // Tải danh sách môn học
        const subjectsRes = await goalApi.getSubjects();
        setSubjects(subjectsRes.data);
        if (subjectsRes.data.length > 0) {
          setSelectedSubjectId(String(subjectsRes.data[0].id));
        }

        // Tải danh sách lộ trình hiện có
        const goalsRes = await goalApi.getGoals();
        setGoals(goalsRes.data);

        // Kiểm tra lịch học trong DB
        const prefRes = await goalApi.getPreferences();
        if (prefRes.data) {
          setStudyHours(prefRes.data.study_hours_per_day);
          setPreferredTime(prefRes.data.preferred_study_time);
          
          // Chuẩn hóa và đọc dữ liệu lịch học chi tiết từ DB
          const savedSchedule = prefRes.data.available_schedule;
          if (savedSchedule) {
            const normalized: Record<string, DaySchedule> = {};
            const days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
            days.forEach(d => {
              const val = savedSchedule[d] as any;
              if (val && typeof val === "object") {
                normalized[d] = {
                  morning: {
                    enabled: !!val.morning,
                    start: val.morning_start || "08:00",
                    end: val.morning_end || "12:00"
                  },
                  afternoon: {
                    enabled: !!val.afternoon,
                    start: val.afternoon_start || "13:00",
                    end: val.afternoon_end || "17:00"
                  },
                  evening: {
                    enabled: !!val.evening,
                    start: val.evening_start || "18:00",
                    end: val.evening_end || "22:00"
                  }
                };
              } else {
                normalized[d] = {
                  morning: { enabled: !!val, start: "08:00", end: "12:00" },
                  afternoon: { enabled: !!val, start: "13:00", end: "17:00" },
                  evening: { enabled: !!val, start: "18:00", end: "22:00" }
                };
              }
            });
            setSchedule(normalized);
          }
          
          // Nếu học sinh đã có lộ trình từ trước, hiển thị danh sách lộ trình quản lý
          if (goalsRes.data.length > 0) {
            setStep("list_goals");
          } else {
            setStep("create_goal");
          }
        }
      } catch (err: any) {
        if (err.response?.status === 404) {
          // Chưa có lịch học -> Bắt buộc điền lịch trước
          setStep("setup_schedule");
        } else {
          console.error("Lỗi khi tải thông tin khởi tạo:", err);
          toast.error("Không thể kết nối với máy chủ.");
        }
      }
    };

    checkScheduleAndLoadData();
  }, []);

  const showError = (err: any, fallback: string) => {
    const detail = err.response?.data?.detail;
    if (!detail) {
      toast.error(err.message || fallback);
      return;
    }
    if (typeof detail === "string") {
      toast.error(detail);
    } else if (Array.isArray(detail)) {
      const msgs = detail.map((d: any) => `${d.loc?.join(".") || "Lỗi"}: ${d.msg || "dữ liệu không hợp lệ"}`).join("; ");
      toast.error(msgs);
    } else {
      toast.error(JSON.stringify(detail));
    }
  };

  // Xử lý lưu cấu hình lịch học vào DB
  const handleSaveSchedule = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    // Đóng gói lịch học l lồng nhau cho API
    const formattedSchedule: Record<string, any> = {};
    Object.keys(schedule).forEach(day => {
      const dayData = schedule[day];
      formattedSchedule[day] = {
        morning: dayData.morning.enabled,
        morning_start: dayData.morning.start,
        morning_end: dayData.morning.end,
        afternoon: dayData.afternoon.enabled,
        afternoon_start: dayData.afternoon.start,
        afternoon_end: dayData.afternoon.end,
        evening: dayData.evening.enabled,
        evening_start: dayData.evening.start,
        evening_end: dayData.evening.end
      };
    });

    try {
      await goalApi.updatePreferences({
        study_hours_per_day: studyHours,
        preferred_study_time: preferredTime,
        available_schedule: formattedSchedule
      });
      toast.success("Đã cấu hình lịch học cá nhân thành công!");
      setStep("create_goal");
    } catch (err: any) {
      showError(err, "Không thể lưu cấu hình lịch học.");
    } finally {
      setLoading(false);
    }
  };

  // Xử lý tạo lộ trình nháp (Draft) từ form điền mục tiêu + deadline
  const handleCreateDraft = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSubjectId) {
      toast.error("Vui lòng chọn môn học.");
      return;
    }
    if (!deadline) {
      toast.error("Vui lòng chọn hạn chót hoàn thành.");
      return;
    }

    setLoading(true);
    try {
      const res = await goalApi.createDraft({
        subject_id: Number(selectedSubjectId),
        target_score: targetScore,
        deadline: deadline,
        user_message: userMessage || undefined
      });
      setDraft(res.data);
      toast.success("AI đã phác thảo lộ trình học tập cá nhân!");
      setStep("roadmap_draft");
    } catch (err: any) {
      showError(err, "Lỗi khi AI xây dựng lộ trình học tập.");
    } finally {
      setLoading(false);
    }
  };

  // Gửi tin nhắn thảo luận và tinh chỉnh lộ trình với AI
  const handleSendMessageToAI = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatMessage.trim() || !draft) return;

    setChatLoading(true);
    const tempMsg = chatMessage;
    setChatMessage("");
    try {
      const res = await goalApi.createDraft({
        subject_id: Number(selectedSubjectId),
        target_score: targetScore,
        deadline: deadline,
        user_message: tempMsg,
        session_id: draft.session_id
      });
      setDraft(res.data);
      toast.success("Đã cập nhật lộ trình theo phản hồi của bạn.");
    } catch (err: any) {
      showError(err, "Không thể gửi tin nhắn phản hồi.");
      setChatMessage(tempMsg); // hoàn trả lại nội dung nếu lỗi
    } finally {
      setChatLoading(false);
    }
  };

  // Xác nhận lưu chính thức lộ trình vào database MySQL
  const handleConfirmRoadmap = async () => {
    if (!draft) return;
    setLoading(true);
    try {
      await goalApi.confirmDraft({
        subject_id: Number(selectedSubjectId),
        target_score: targetScore,
        deadline: deadline,
        session_id: draft.session_id
      });
      toast.success("Kích hoạt lộ trình học tập thành công!");
      setStep("success");
    } catch (err: any) {
      showError(err, "Lỗi khi lưu lộ trình chính thức.");
    } finally {
      setLoading(false);
    }
  };

  // Xóa lộ trình học hiện có
  const handleDeleteGoal = async (id: number) => {
    if (!confirm("Bạn có chắc chắn muốn xóa lộ trình học tập này? Toàn bộ lịch học và đề thi liên quan sẽ bị xóa vĩnh viễn.")) return;
    setGoalsLoading(true);
    try {
      await goalApi.deleteGoal(id);
      toast.success("Đã xóa lộ trình học tập thành công.");
      // Tải lại danh sách
      const res = await goalApi.getGoals();
      setGoals(res.data);
      if (res.data.length === 0) {
        setStep("create_goal");
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Không thể xóa lộ trình.");
    } finally {
      setGoalsLoading(false);
    }
  };


  // Thay đổi trạng thái bật/tắt của một buổi
  const toggleTimeSlot = (day: string, slot: "morning" | "afternoon" | "evening") => {
    setSchedule(prev => {
      const dayData = prev[day];
      return {
        ...prev,
        [day]: {
          ...dayData,
          [slot]: {
            ...dayData[slot],
            enabled: !dayData[slot].enabled
          }
        }
      };
    });
  };

  // Thay đổi giờ bắt đầu / giờ kết thúc của một buổi
  const handleHourChange = (day: string, slot: "morning" | "afternoon" | "evening", type: "start" | "end", value: string) => {
    setSchedule(prev => {
      const dayData = prev[day];
      return {
        ...prev,
        [day]: {
          ...dayData,
          [slot]: {
            ...dayData[slot],
            [type]: value
          }
        }
      };
    });
  };

  const dayLabels: Record<string, string> = {
    mon: "Thứ 2", tue: "Thứ 3", wed: "Thứ 4", thu: "Thứ 5", fri: "Thứ 6", sat: "Thứ 7", sun: "Chủ Nhật"
  };

  return (
    <div className="max-w-4xl mx-auto py-6 px-4 text-left">
      <AnimatePresence mode="wait">
        
        {/* Bước 1: Checking status */}
        {step === "checking" && (
          <motion.div 
            key="checking"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="py-24 text-center space-y-4"
          >
            <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400 font-mono">
              Đang phân tích cấu hình tài khoản học sinh...
            </p>
          </motion.div>
        )}

        {/* Bước: List active goals */}
        {step === "list_goals" && (
          <motion.div
            key="list_goals"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="space-y-6"
          >
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-8 rounded-2xl shadow-sm">
              <div>
                <h1 className="text-2xl font-black text-zinc-900 dark:text-white">
                  Lộ trình học tập của bạn
                </h1>
                <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
                  Quản lý các lộ trình học tập do AI lập riêng cho bạn.
                </p>
              </div>
              <button
                onClick={() => setStep("create_goal")}
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm rounded-xl shadow-md shadow-indigo-500/20 active:scale-[0.98] transition-all flex items-center justify-center gap-2 cursor-pointer"
              >
                <Plus className="w-4 h-4" />
                Tạo lộ trình mới
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {goals.map((g) => {
                const subj = subjects.find((s) => s.id === g.subject_id);
                return (
                  <div
                    key={g.id}
                    className="p-6 border border-zinc-200 dark:border-zinc-800 rounded-2xl bg-white dark:bg-zinc-900 shadow-sm hover:shadow-md transition-all flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <span className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded-md uppercase">
                            {subj?.code || "MÔN HỌC"}
                          </span>
                          <h3 className="text-base font-extrabold text-zinc-850 dark:text-zinc-100 mt-2 truncate">
                            {g.title || `Lộ trình môn ${subj?.name}`}
                          </h3>
                        </div>
                        <span className="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                          {g.status === "active" ? "Đang chạy" : g.status === "completed" ? "Đã xong" : g.status}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-4 mt-6 border-t border-zinc-100 dark:border-zinc-800 pt-4 text-xs">
                        <div>
                          <p className="text-zinc-400 dark:text-zinc-500 font-medium">Mục tiêu điểm</p>
                          <p className="text-sm font-black text-zinc-800 dark:text-zinc-200 mt-0.5">
                            {g.target_score.toFixed(1)} / 10
                          </p>
                        </div>
                        <div>
                          <p className="text-zinc-400 dark:text-zinc-500 font-medium">Ngày hoàn thành</p>
                          <p className="text-sm font-bold text-zinc-800 dark:text-zinc-200 mt-0.5 flex items-center gap-1.5">
                            <Calendar className="w-3.5 h-3.5 text-zinc-400" />
                            {new Date(g.deadline).toLocaleDateString("vi-VN")}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="mt-6 pt-4 border-t border-zinc-100 dark:border-zinc-800 flex justify-between items-center">
                      <Link
                        href="/"
                        className="text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:underline"
                      >
                        Bắt đầu học ngay →
                      </Link>
                      <button
                        onClick={() => handleDeleteGoal(g.id)}
                        disabled={goalsLoading}
                        className="p-2 text-zinc-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/40 rounded-xl transition-colors cursor-pointer disabled:opacity-50"
                        title="Xóa lộ trình học"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}

        {/* Bước 2: Setup Schedule (Chưa có cấu hình lịch học / Muốn cập nhật) */}
        {step === "setup_schedule" && (
          <motion.div
            key="setup_schedule"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="space-y-6"
          >
            <div className="bg-amber-500/10 border border-amber-500/20 text-amber-700 dark:text-amber-400 p-5 rounded-2xl text-xs font-semibold leading-relaxed">
              * THÔNG BÁO: Tài khoản của bạn chưa thiết lập lịch rảnh cá nhân. Để AI Agent của EduMind phân phối giờ học chuẩn xác và không chồng lấp thời gian biểu, vui lòng hoàn tất cấu hình lịch học dưới đây trước khi lập lộ trình.
            </div>

            <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-8 rounded-2xl shadow-sm">
              <h2 className="text-xl font-black text-zinc-950 dark:text-white uppercase mb-6">
                CẤU HÌNH LỊCH HỌC CỦA BẠN
              </h2>

              <form onSubmit={handleSaveSchedule} className="space-y-6">
                {/* 1. Số giờ học */}
                <div className="space-y-2">
                  <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase">
                    Số giờ tự học mong muốn mỗi ngày:
                  </label>
                  <input 
                    type="number" 
                    min={1} 
                    max={12}
                    value={studyHours} 
                    onChange={e => setStudyHours(Number(e.target.value))}
                    className="w-full px-4 py-3 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-bold focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white text-sm"
                  />
                  <span className="text-[10px] text-zinc-400 font-medium block">
                    AI sẽ phân bổ lượng kiến thức học dựa trên số giờ tự học bạn cam kết hàng ngày.
                  </span>
                </div>

                {/* 2. Khung giờ học */}
                <div className="space-y-2">
                  <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase">
                    Khung giờ học ưa thích nhất:
                  </label>
                  <select
                    value={preferredTime}
                    onChange={e => setPreferredTime(e.target.value)}
                    className="w-full px-4 py-3 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-bold focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white text-sm"
                  >
                    <option value="morning">Buổi sáng (08:00 - 12:00)</option>
                    <option value="afternoon">Buổi chiều (13:00 - 17:00)</option>
                    <option value="evening">Buổi tối (18:00 - 22:00)</option>
                  </select>
                </div>

                {/* 3. Lịch rảnh chi tiết các thứ và buổi trong tuần */}
                <div className="space-y-4 border-t border-zinc-200 dark:border-zinc-800 pt-6">
                  <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                    Chi tiết lịch rảnh các ngày trong tuần:
                  </label>
                  <span className="text-[10px] text-zinc-400 font-medium block mb-4">
                    Nhấn để kích hoạt buổi bạn rảnh rỗi và cấu hình khung giờ học chi tiết cho buổi đó:
                  </span>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.keys(schedule).map((day) => {
                      const slots = schedule[day] || {
                        morning: { enabled: false, start: "08:00", end: "12:00" },
                        afternoon: { enabled: false, start: "13:00", end: "17:00" },
                        evening: { enabled: false, start: "18:00", end: "22:00" }
                      };
                      return (
                        <div 
                          key={day} 
                          className="p-5 border border-zinc-200 dark:border-zinc-800 rounded-2xl bg-zinc-50/50 dark:bg-zinc-950/20 space-y-4 shadow-sm"
                        >
                          <div className="pb-2 border-b border-zinc-200/60 dark:border-zinc-800/80">
                            <span className="text-xs font-black text-zinc-800 dark:text-zinc-200 uppercase tracking-wide">
                              {dayLabels[day]}
                            </span>
                          </div>
                          
                          <div className="space-y-3">
                            {/* Morning Slot Row */}
                            <div className="flex flex-col space-y-2">
                              <div className="flex items-center justify-between">
                                <button
                                  type="button"
                                  onClick={() => toggleTimeSlot(day, "morning")}
                                  className={`px-3.5 py-1.5 rounded-xl border text-[10px] font-bold uppercase transition-all cursor-pointer ${
                                    slots.morning.enabled
                                      ? "bg-indigo-600 border-indigo-600 text-white shadow-sm shadow-indigo-500/10"
                                      : "bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800 text-zinc-400 dark:text-zinc-500 hover:border-zinc-350"
                                  }`}
                                >
                                  Buổi Sáng
                                </button>
                                <span className="text-[10px] text-zinc-450 dark:text-zinc-400 font-mono font-bold">
                                  {slots.morning.enabled ? `${slots.morning.start} - ${slots.morning.end}` : "Chưa chọn"}
                                </span>
                              </div>
                              {slots.morning.enabled && (
                                <div className="flex items-center gap-2 pl-2">
                                  <span className="text-[10px] text-zinc-400 font-medium">Từ:</span>
                                  <select
                                    value={slots.morning.start}
                                    onChange={e => handleHourChange(day, "morning", "start", e.target.value)}
                                    className="px-2.5 py-1.5 border border-zinc-200 dark:border-zinc-800 rounded-lg bg-white dark:bg-zinc-950 text-[10px] font-bold text-zinc-700 dark:text-zinc-300 focus:outline-none focus:border-indigo-500 cursor-pointer"
                                  >
                                    {["05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00"].map(h => (
                                      <option key={h} value={h}>{h}</option>
                                    ))}
                                  </select>
                                  <span className="text-[10px] text-zinc-400 font-medium">Đến:</span>
                                  <select
                                    value={slots.morning.end}
                                    onChange={e => handleHourChange(day, "morning", "end", e.target.value)}
                                    className="px-2.5 py-1.5 border border-zinc-200 dark:border-zinc-800 rounded-lg bg-white dark:bg-zinc-950 text-[10px] font-bold text-zinc-700 dark:text-zinc-300 focus:outline-none focus:border-indigo-500 cursor-pointer"
                                  >
                                    {["06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00"].map(h => (
                                      <option key={h} value={h}>{h}</option>
                                    ))}
                                  </select>
                                </div>
                              )}
                            </div>

                            {/* Afternoon Slot Row */}
                            <div className="flex flex-col space-y-2">
                              <div className="flex items-center justify-between">
                                <button
                                  type="button"
                                  onClick={() => toggleTimeSlot(day, "afternoon")}
                                  className={`px-3.5 py-1.5 rounded-xl border text-[10px] font-bold uppercase transition-all cursor-pointer ${
                                    slots.afternoon.enabled
                                      ? "bg-indigo-600 border-indigo-600 text-white shadow-sm shadow-indigo-500/10"
                                      : "bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800 text-zinc-400 dark:text-zinc-500 hover:border-zinc-350"
                                  }`}
                                >
                                  Buổi Chiều
                                </button>
                                <span className="text-[10px] text-zinc-450 dark:text-zinc-400 font-mono font-bold">
                                  {slots.afternoon.enabled ? `${slots.afternoon.start} - ${slots.afternoon.end}` : "Chưa chọn"}
                                </span>
                              </div>
                              {slots.afternoon.enabled && (
                                <div className="flex items-center gap-2 pl-2">
                                  <span className="text-[10px] text-zinc-400 font-medium">Từ:</span>
                                  <select
                                    value={slots.afternoon.start}
                                    onChange={e => handleHourChange(day, "afternoon", "start", e.target.value)}
                                    className="px-2.5 py-1.5 border border-zinc-200 dark:border-zinc-800 rounded-lg bg-white dark:bg-zinc-950 text-[10px] font-bold text-zinc-700 dark:text-zinc-300 focus:outline-none focus:border-indigo-500 cursor-pointer"
                                  >
                                    {["12:00", "13:00", "14:00", "15:00", "16:00", "17:00"].map(h => (
                                      <option key={h} value={h}>{h}</option>
                                    ))}
                                  </select>
                                  <span className="text-[10px] text-zinc-400 font-medium">Đến:</span>
                                  <select
                                    value={slots.afternoon.end}
                                    onChange={e => handleHourChange(day, "afternoon", "end", e.target.value)}
                                    className="px-2.5 py-1.5 border border-zinc-200 dark:border-zinc-800 rounded-lg bg-white dark:bg-zinc-950 text-[10px] font-bold text-zinc-700 dark:text-zinc-300 focus:outline-none focus:border-indigo-500 cursor-pointer"
                                  >
                                    {["13:00", "14:00", "15:00", "16:00", "17:00", "18:00"].map(h => (
                                      <option key={h} value={h}>{h}</option>
                                    ))}
                                  </select>
                                </div>
                              )}
                            </div>

                            {/* Evening Slot Row */}
                            <div className="flex flex-col space-y-2">
                              <div className="flex items-center justify-between">
                                <button
                                  type="button"
                                  onClick={() => toggleTimeSlot(day, "evening")}
                                  className={`px-3.5 py-1.5 rounded-xl border text-[10px] font-bold uppercase transition-all cursor-pointer ${
                                    slots.evening.enabled
                                      ? "bg-indigo-600 border-indigo-600 text-white shadow-sm shadow-indigo-500/10"
                                      : "bg-white dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800 text-zinc-400 dark:text-zinc-500 hover:border-zinc-350"
                                  }`}
                                >
                                  Buổi Tối
                                </button>
                                <span className="text-[10px] text-zinc-450 dark:text-zinc-400 font-mono font-bold">
                                  {slots.evening.enabled ? `${slots.evening.start} - ${slots.evening.end}` : "Chưa chọn"}
                                </span>
                              </div>
                              {slots.evening.enabled && (
                                <div className="flex items-center gap-2 pl-2">
                                  <span className="text-[10px] text-zinc-400 font-medium">Từ:</span>
                                  <select
                                    value={slots.evening.start}
                                    onChange={e => handleHourChange(day, "evening", "start", e.target.value)}
                                    className="px-2.5 py-1.5 border border-zinc-200 dark:border-zinc-800 rounded-lg bg-white dark:bg-zinc-950 text-[10px] font-bold text-zinc-700 dark:text-zinc-300 focus:outline-none focus:border-indigo-500 cursor-pointer"
                                  >
                                    {["18:00", "19:00", "20:00", "21:00", "22:00", "23:00"].map(h => (
                                      <option key={h} value={h}>{h}</option>
                                    ))}
                                  </select>
                                  <span className="text-[10px] text-zinc-400 font-medium">Đến:</span>
                                  <select
                                    value={slots.evening.end}
                                    onChange={e => handleHourChange(day, "evening", "end", e.target.value)}
                                    className="px-2.5 py-1.5 border border-zinc-200 dark:border-zinc-800 rounded-lg bg-white dark:bg-zinc-950 text-[10px] font-bold text-zinc-700 dark:text-zinc-300 focus:outline-none focus:border-indigo-500 cursor-pointer"
                                  >
                                    {["19:00", "20:00", "21:00", "22:00", "23:00", "24:00"].map(h => (
                                      <option key={h} value={h}>{h}</option>
                                    ))}
                                  </select>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className="pt-6 border-t border-zinc-200 dark:border-zinc-800">
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-3.5 bg-zinc-950 hover:bg-zinc-900 dark:bg-zinc-50 dark:hover:bg-zinc-100 text-zinc-50 dark:text-zinc-950 font-bold rounded-xl text-xs tracking-wider transition-all cursor-pointer disabled:opacity-50"
                  >
                    {loading ? "ĐANG LƯU CẤU HÌNH..." : "LƯU CẤU HÌNH LỊCH HỌC & TIẾP TỤC ->"}
                  </button>
                </div>
              </form>
            </div>
          </motion.div>
        )}

        {/* Bước 3: Điền mục tiêu & Hạn chót (Tạo lộ trình) */}
        {step === "create_goal" && (
          <motion.div
            key="create_goal"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="space-y-6"
          >
            <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-8 rounded-2xl shadow-sm">
              <h2 className="text-xl font-black text-zinc-950 dark:text-white uppercase mb-6">
                THIẾT LẬP MỤC TIÊU HỌC TẬP MỚI
              </h2>

              <form onSubmit={handleCreateDraft} className="space-y-6">
                {/* 1. Chọn môn học */}
                <div className="space-y-2">
                  <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase">
                    Chọn môn học cần lên lộ trình:
                  </label>
                  <select
                    value={selectedSubjectId}
                    onChange={e => setSelectedSubjectId(e.target.value)}
                    className="w-full px-4 py-3 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-bold focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white text-sm"
                  >
                    {subjects.length === 0 ? (
                      <option value="">Không tìm thấy môn học nào</option>
                    ) : (
                      subjects.map(sub => (
                        <option key={sub.id} value={sub.id}>{sub.name} ({sub.code})</option>
                      ))
                    )}
                  </select>
                </div>

                {/* 2. Điểm mong muốn & Deadline */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div className="space-y-2">
                    <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase">
                      Điểm số mục tiêu mong muốn (1 - 10):
                    </label>
                    <input 
                      type="number" 
                      min={1} 
                      max={10} 
                      step={0.5}
                      value={targetScore} 
                      onChange={e => setTargetScore(Number(e.target.value))}
                      className="w-full px-4 py-3 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-bold focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white text-sm"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase">
                      Hạn chót phải hoàn thành (Deadline):
                    </label>
                    <input 
                      type="date" 
                      min={new Date().toISOString().split("T")[0]}
                      value={deadline} 
                      onChange={e => setDeadline(e.target.value)}
                      className="w-full px-4 py-3 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-bold focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white text-sm"
                    />
                  </div>
                </div>

                {/* 3. Lời nhắn bổ sung cho AI */}
                <div className="space-y-2">
                  <label className="block text-xs font-bold text-zinc-500 dark:text-zinc-400 uppercase">
                    Yêu cầu bổ sung gửi AI Agent (Tùy chọn):
                  </label>
                  <textarea
                    rows={3}
                    placeholder="Ví dụ: Tập trung nhiều bài kiểm tra, giảm giờ học tuần đầu, tôi yếu lập trình hướng đối tượng..."
                    value={userMessage}
                    onChange={e => setUserMessage(e.target.value)}
                    className="w-full px-4 py-3 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50 dark:bg-zinc-950 font-medium focus:outline-none focus:border-indigo-500 text-zinc-900 dark:text-white text-sm"
                  />
                </div>

                <div className="pt-4 flex flex-col md:flex-row items-center justify-between gap-4">
                  <button
                    type="button"
                    onClick={() => setStep("setup_schedule")}
                    className="text-xs font-bold text-zinc-500 hover:text-zinc-950 dark:hover:text-white hover:underline cursor-pointer"
                  >
                    Thay đổi lịch học / cấu hình thời gian rảnh
                  </button>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full md:w-fit px-8 py-3.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs tracking-wider transition-all cursor-pointer disabled:opacity-50 shadow-md shadow-indigo-500/10"
                  >
                    {loading ? "AI ĐANG LẬP LỘ TRÌNH..." : "AI LẬP LỘ TRÌNH THỬ NGAY ->"}
                  </button>
                </div>
              </form>
            </div>
          </motion.div>
        )}

        {/* Bước 4: Roadmap Draft & Thảo luận tinh chỉnh */}
        {step === "roadmap_draft" && draft && (
          <motion.div
            key="roadmap_draft"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="grid grid-cols-1 lg:grid-cols-3 gap-6"
          >
            {/* Cột trái: Timeline Lộ trình học nháp */}
            <div className="lg:col-span-2 space-y-5">
              <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm">
                <div className="pb-4 border-b border-zinc-200 dark:border-zinc-850 mb-6">
                  <h2 className="font-bold text-sm tracking-wide text-zinc-900 dark:text-white uppercase">
                    Bản thảo lộ trình học đề xuất từ AI Agent
                  </h2>
                  <p className="text-[10px] text-zinc-500 font-mono mt-1 uppercase">
                    Môn: {subjects.find(s => String(s.id) === selectedSubjectId)?.name} // Điểm mong muốn: {targetScore} // Hạn chót: {deadline}
                  </p>
                </div>

                <div className="space-y-6 max-h-[60vh] overflow-y-auto pr-2">
                  {/* 1. Lộ trình tuần */}
                  <div className="space-y-4 text-left">
                    <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-3">📅 Lộ trình theo tuần</h3>
                    {draft.plan.weeks.map((week) => (
                      <div key={week.week} className="relative pl-6 border-l border-zinc-200 dark:border-zinc-800 space-y-2">
                        <span className="absolute -left-1.5 top-1.5 w-3 h-3 rounded-full bg-indigo-600 border border-white dark:border-zinc-900" />
                        <h4 className="text-xs font-bold text-zinc-850 dark:text-zinc-200">
                          Tuần {week.week}
                        </h4>
                        <div className="space-y-1 pl-2">
                          {week.tasks.map((task, idx) => (
                            <p key={idx} className="text-xs font-semibold text-zinc-550 dark:text-zinc-450">
                              • {task}
                            </p>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* 2. Lịch học chi tiết hàng ngày */}
                  {draft.plan.daily_schedule && draft.plan.daily_schedule.length > 0 && (
                    <div className="pt-6 border-t border-zinc-100 dark:border-zinc-850 space-y-4 text-left">
                      <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-3">⏰ Thời khóa biểu hàng ngày chi tiết</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                        {draft.plan.daily_schedule.map((day, idx) => (
                          <div key={idx} className="bg-zinc-50/50 dark:bg-zinc-950/20 border border-zinc-200/50 dark:border-zinc-850 p-4 rounded-xl space-y-2 shadow-sm animate-fade-in">
                            <div className="flex items-center justify-between">
                              <span className="text-[9px] font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded-md font-mono">{day.date}</span>
                              <span className="text-[9px] text-zinc-400 dark:text-zinc-550 font-bold">{day.start_time} - {day.end_time}</span>
                            </div>
                            <h5 className="text-xs font-extrabold text-zinc-800 dark:text-zinc-200">{day.task}</h5>
                            <p className="text-[10px] text-zinc-550 dark:text-zinc-450 leading-relaxed font-semibold">{day.description}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 3. Giáo trình bài giảng tham khảo */}
                  {draft.plan.curriculum_materials && draft.plan.curriculum_materials.length > 0 && (
                    <div className="pt-6 border-t border-zinc-100 dark:border-zinc-850 space-y-3 text-left">
                      <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-2">📚 Tài liệu bài giảng RAG tham khảo</h3>
                      <div className="space-y-2.5">
                        {draft.plan.curriculum_materials.map((mat, idx) => (
                          <div key={idx} className="p-3 border border-zinc-150 dark:border-zinc-800 rounded-xl bg-zinc-50/30 dark:bg-zinc-900/10">
                            <h5 className="text-xs font-extrabold text-zinc-800 dark:text-zinc-200">{mat.topic}</h5>
                            <p className="text-[10px] text-zinc-550 dark:text-zinc-400 mt-1 leading-relaxed font-semibold">{mat.content}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 4. Bộ câu hỏi AI sinh kèm */}
                  {draft.plan.quizzes && draft.plan.quizzes.length > 0 && (
                    <div className="pt-6 border-t border-zinc-100 dark:border-zinc-850 space-y-3 text-left">
                      <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-2">📝 Đề thi luyện tập AI sinh kèm</h3>
                      <div className="space-y-2.5">
                        {draft.plan.quizzes.map((quiz, idx) => (
                          <div key={idx} className="p-3 border border-zinc-150 dark:border-zinc-800 rounded-xl bg-zinc-50/30 dark:bg-zinc-900/10 flex justify-between items-center">
                            <div>
                              <h5 className="text-xs font-extrabold text-zinc-850 dark:text-zinc-200">{quiz.title}</h5>
                              <span className="text-[10px] text-zinc-400 font-bold">{quiz.questions ? quiz.questions.length : 0} câu hỏi trắc nghiệm</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Cột phải: Chat Tinh chỉnh & Nút Xác nhận */}
            <div className="space-y-5">
              {/* Khung tương tác tinh chỉnh với AI */}
              <div className="bg-zinc-950 dark:bg-zinc-900 border border-zinc-850 p-6 rounded-2xl text-zinc-50 shadow-md">
                <span className="text-[10px] font-bold tracking-wider text-indigo-300 block uppercase">
                  Thảo luận với AI
                </span>
                <h3 className="text-sm font-black uppercase mt-1">
                  ĐIỀU CHỈNH LỘ TRÌNH
                </h3>
                <p className="text-[10px] text-zinc-400 mt-2 leading-relaxed">
                  Nếu bạn muốn thay đổi bất kỳ phần nào của lộ trình (ví dụ: chuyển bài học giữa các tuần, học thêm chủ đề cụ thể...), hãy yêu cầu AI ngay bên dưới.
                </p>

                <form onSubmit={handleSendMessageToAI} className="mt-5 space-y-3">
                  <textarea
                    rows={3}
                    placeholder="Nhập yêu cầu điều chỉnh lộ trình..."
                    value={chatMessage}
                    onChange={e => setChatMessage(e.target.value)}
                    className="w-full px-3 py-2 text-xs border border-zinc-800 rounded-xl bg-zinc-900 text-white font-medium focus:outline-none focus:border-indigo-500 placeholder-zinc-500"
                  />
                  <button
                    type="submit"
                    disabled={chatLoading || !chatMessage.trim()}
                    className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-zinc-850 text-white font-bold rounded-xl text-xs transition-all cursor-pointer"
                  >
                    {chatLoading ? "AI ĐANG ĐIỀU CHỈNH..." : "GỬI YÊU CẦU ĐỔI ->"}
                  </button>
                </form>
              </div>

              {/* Nút Confirm chính thức */}
              <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800 p-6 rounded-2xl shadow-sm space-y-4">
                <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed font-medium">
                  Nhấp vào xác nhận để lưu chính thức lộ trình học tập này vào dữ liệu lớp học và bắt đầu lộ trình hàng ngày.
                </p>
                <button
                  onClick={handleConfirmRoadmap}
                  disabled={loading}
                  className="w-full py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs tracking-wider transition-all shadow-md shadow-emerald-500/10 cursor-pointer disabled:opacity-50"
                >
                  {loading ? "ĐANG KÍCH HOẠT..." : "XÁC NHẬN & BẮT ĐẦU HỌC ✓"}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    if (window.confirm("Bạn có chắc muốn hủy bản nháp lộ trình này để làm lại từ đầu?")) {
                      setDraft(null);
                      setStep("setup_schedule");
                    }
                  }}
                  className="w-full py-2.5 border border-red-200 dark:border-red-950/40 hover:bg-red-50 dark:hover:bg-red-950/20 text-red-600 dark:text-red-400 font-bold rounded-xl text-xs transition-all cursor-pointer"
                >
                  HỦY BẢN NHÁP & LÀM LẠI ✕
                </button>
              </div>
            </div>
          </motion.div>
        )}

        {/* Bước 5: Tạo lộ trình thành công */}
        {step === "success" && (
          <motion.div
            key="success"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="max-w-md mx-auto text-center space-y-6 py-12"
          >
            <div className="w-16 h-16 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 rounded-full flex items-center justify-center text-3xl font-black mx-auto select-none">
              ✓
            </div>
            <div className="space-y-2">
              <h2 className="text-xl font-black text-zinc-950 dark:text-white uppercase">
                KÍCH HOẠT THÀNH CÔNG!
              </h2>
              <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed font-medium">
                Mục tiêu học tập của bạn đã được ghi nhận. AI Agent đã tạo đầy đủ các buổi học hàng ngày, tài liệu bài giảng và bộ câu hỏi ôn tập thông minh tương thích.
              </p>
            </div>
            <Link
              href={ROUTES.STUDENT_DASHBOARD}
              className="inline-block w-full py-3.5 bg-zinc-950 hover:bg-zinc-900 dark:bg-zinc-50 dark:hover:bg-zinc-100 text-zinc-50 dark:text-zinc-950 font-bold rounded-xl text-xs tracking-wider transition-all cursor-pointer"
            >
              ĐI ĐẾN BẢNG ĐIỀU KHIỂN {"->"}
            </Link>
          </motion.div>
        )}

      </AnimatePresence>
    </div>
  );
}
