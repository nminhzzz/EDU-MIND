"use client";

import { useCallback, useEffect, useState } from "react";
import { goalService } from "@/features/student/services/goal";
import { subjectService } from "@/features/student/services/subject";
import { useConfirmDialog } from "@/features/student/hooks/use-confirm-dialog";
import type { DraftResponse, StudyGoalResponse, Subject } from "@/features/student/types";
import { TimeSlot, WeekSchedule } from "@/features/student/types/schedule";
import {
  createDefaultWeekSchedule,
  formatScheduleForApi,
  normalizeScheduleFromApi,
} from "@/features/student/utils/schedule";
import { parseApiError, getApiErrorStatus } from "@/utils/api-error";
import { toast } from "sonner";

export type GoalsWizardStep =
  | "checking"
  | "list_goals"
  | "setup_schedule"
  | "create_goal"
  | "roadmap_draft"
  | "success";

export function useGoalsWizard() {
  const confirm = useConfirmDialog();
  const [step, setStep] = useState<GoalsWizardStep>("checking");
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(false);
  const [goals, setGoals] = useState<StudyGoalResponse[]>([]);
  const [goalsLoading, setGoalsLoading] = useState(false);

  const [studyHours, setStudyHours] = useState<number>(2);
  const [preferredTime, setPreferredTime] = useState<string>("evening");
  const [schedule, setSchedule] = useState<WeekSchedule>(createDefaultWeekSchedule);

  const [selectedSubjectId, setSelectedSubjectId] = useState<string>("");
  const [targetScore, setTargetScore] = useState<number>(8);
  const [deadline, setDeadline] = useState<string>("");
  const [userMessage, setUserMessage] = useState<string>("");

  const [draft, setDraft] = useState<DraftResponse | null>(null);
  const [chatMessage, setChatMessage] = useState<string>("");
  const [chatLoading, setChatLoading] = useState(false);

  useEffect(() => {
    const checkScheduleAndLoadData = async () => {
      try {
        const subjectsRes = await subjectService.list();
        setSubjects(subjectsRes.data);
        if (subjectsRes.data.length > 0) {
          setSelectedSubjectId(String(subjectsRes.data[0].id));
        }

        const goalsRes = await goalService.getGoals();
        setGoals(goalsRes.data);

        const prefRes = await goalService.getPreferences();
        if (prefRes.data) {
          setStudyHours(prefRes.data.study_hours_per_day);
          setPreferredTime(prefRes.data.preferred_study_time);

          const savedSchedule = prefRes.data.available_schedule;
          if (savedSchedule) {
            setSchedule(
              normalizeScheduleFromApi(savedSchedule as Record<string, unknown>),
            );
          }

          if (goalsRes.data.length > 0) {
            setStep("list_goals");
          } else {
            setStep("create_goal");
          }
        }
      } catch (err: unknown) {
        if (getApiErrorStatus(err) === 404) {
          setStep("setup_schedule");
        } else {
          console.error("Lỗi khi tải thông tin khởi tạo:", err);
          toast.error("Không thể kết nối với máy chủ.");
        }
      }
    };

    checkScheduleAndLoadData();
  }, []);

  const handleSaveSchedule = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setLoading(true);

      try {
        await goalService.updatePreferences({
          study_hours_per_day: studyHours,
          preferred_study_time: preferredTime,
          available_schedule: formatScheduleForApi(schedule),
        });
        toast.success("Đã cấu hình lịch học cá nhân thành công!");
        setStep("create_goal");
      } catch (err: unknown) {
        toast.error(parseApiError(err, "Không thể lưu cấu hình lịch học."));
      } finally {
        setLoading(false);
      }
    },
    [schedule, studyHours, preferredTime],
  );

  const handleCreateDraft = useCallback(
    async (e: React.FormEvent) => {
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
        const res = await goalService.createDraft({
          subject_id: Number(selectedSubjectId),
          target_score: targetScore,
          deadline,
          user_message: userMessage || undefined,
        });
        setDraft(res.data);
        toast.success("AI đã phác thảo lộ trình học tập cá nhân!");
        setStep("roadmap_draft");
      } catch (err: unknown) {
        toast.error(parseApiError(err, "Lỗi khi AI xây dựng lộ trình học tập."));
      } finally {
        setLoading(false);
      }
    },
    [selectedSubjectId, targetScore, deadline, userMessage],
  );

  const handleSendMessageToAI = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!chatMessage.trim() || !draft) return;

      setChatLoading(true);
      const tempMsg = chatMessage;
      setChatMessage("");
      try {
        const res = await goalService.createDraft({
          subject_id: Number(selectedSubjectId),
          target_score: targetScore,
          deadline,
          user_message: tempMsg,
          session_id: draft.session_id,
        });
        setDraft(res.data);
        toast.success("Đã cập nhật lộ trình theo phản hồi của bạn.");
      } catch (err: unknown) {
        toast.error(parseApiError(err, "Không thể gửi tin nhắn phản hồi."));
        setChatMessage(tempMsg);
      } finally {
        setChatLoading(false);
      }
    },
    [chatMessage, draft, selectedSubjectId, targetScore, deadline],
  );

  const handleConfirmRoadmap = useCallback(async () => {
    if (!draft) return;
    setLoading(true);
    try {
      await goalService.confirmDraft({
        subject_id: Number(selectedSubjectId),
        target_score: targetScore,
        deadline,
        session_id: draft.session_id,
      });
      toast.success("Kích hoạt lộ trình học tập thành công!");
      setStep("success");
    } catch (err: unknown) {
      toast.error(parseApiError(err, "Lỗi khi lưu lộ trình chính thức."));
    } finally {
      setLoading(false);
    }
  }, [draft, selectedSubjectId, targetScore, deadline]);

  const handleDeleteGoal = useCallback(async (id: number) => {
    if (
      !confirm(
        "Bạn có chắc chắn muốn xóa lộ trình học tập này? Toàn bộ lịch học và đề thi liên quan sẽ bị xóa vĩnh viễn.",
      )
    ) {
      return;
    }
    setGoalsLoading(true);
    try {
      await goalService.deleteGoal(id);
      toast.success("Đã xóa lộ trình học tập thành công.");
      const res = await goalService.getGoals();
      setGoals(res.data);
      if (res.data.length === 0) {
        setStep("create_goal");
      }
    } catch (err: unknown) {
      toast.error(parseApiError(err, "Không thể xóa lộ trình."));
    } finally {
      setGoalsLoading(false);
    }
  }, [confirm]);

  const toggleTimeSlot = useCallback((day: string, slot: TimeSlot) => {
    setSchedule((prev) => {
      const dayData = prev[day];
      return {
        ...prev,
        [day]: {
          ...dayData,
          [slot]: {
            ...dayData[slot],
            enabled: !dayData[slot].enabled,
          },
        },
      };
    });
  }, []);

  const handleHourChange = useCallback(
    (day: string, slot: TimeSlot, type: "start" | "end", value: string) => {
      setSchedule((prev) => {
        const dayData = prev[day];
        return {
          ...prev,
          [day]: {
            ...dayData,
            [slot]: {
              ...dayData[slot],
              [type]: value,
            },
          },
        };
      });
    },
    [],
  );

  const handleCancelDraft = useCallback(() => {
    if (confirm("Bạn có chắc muốn hủy bản nháp lộ trình này để làm lại từ đầu?")) {
      setDraft(null);
      setStep("setup_schedule");
    }
  }, [confirm]);

  return {
    step,
    setStep,
    subjects,
    loading,
    goals,
    goalsLoading,
    studyHours,
    setStudyHours,
    preferredTime,
    setPreferredTime,
    schedule,
    selectedSubjectId,
    setSelectedSubjectId,
    targetScore,
    setTargetScore,
    deadline,
    setDeadline,
    userMessage,
    setUserMessage,
    draft,
    chatMessage,
    setChatMessage,
    chatLoading,
    handleSaveSchedule,
    handleCreateDraft,
    handleSendMessageToAI,
    handleConfirmRoadmap,
    handleDeleteGoal,
    toggleTimeSlot,
    handleHourChange,
    handleCancelDraft,
  };
}

export type GoalsWizardState = ReturnType<typeof useGoalsWizard>;
