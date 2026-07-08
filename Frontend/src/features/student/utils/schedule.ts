import {
  DaySchedule,
  SavedDaySchedule,
  TimeSlot,
  WeekSchedule,
} from "@/features/student/types/schedule";

export const SCHEDULE_DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"] as const;

export const DAY_LABELS: Record<string, string> = {
  mon: "Thứ 2",
  tue: "Thứ 3",
  wed: "Thứ 4",
  thu: "Thứ 5",
  fri: "Thứ 6",
  sat: "Thứ 7",
  sun: "Chủ Nhật",
};

export const SLOT_LABELS: Record<TimeSlot, string> = {
  morning: "Buổi Sáng",
  afternoon: "Buổi Chiều",
  evening: "Buổi Tối",
};

export const SLOT_HOUR_OPTIONS: Record<
  TimeSlot,
  { start: string[]; end: string[] }
> = {
  morning: {
    start: ["05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00"],
    end: ["06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00"],
  },
  afternoon: {
    start: ["12:00", "13:00", "14:00", "15:00", "16:00", "17:00"],
    end: ["13:00", "14:00", "15:00", "16:00", "17:00", "18:00"],
  },
  evening: {
    start: ["18:00", "19:00", "20:00", "21:00", "22:00", "23:00"],
    end: ["19:00", "20:00", "21:00", "22:00", "23:00", "24:00"],
  },
};

const DEFAULT_SLOT: Record<TimeSlot, SlotDetailDefaults> = {
  morning: { enabled: false, start: "08:00", end: "12:00" },
  afternoon: { enabled: false, start: "13:00", end: "17:00" },
  evening: { enabled: false, start: "18:00", end: "22:00" },
};

interface SlotDetailDefaults {
  enabled: boolean;
  start: string;
  end: string;
}

export function createDefaultWeekSchedule(): WeekSchedule {
  return {
    mon: {
      morning: { enabled: true, start: "08:00", end: "12:00" },
      afternoon: { enabled: false, start: "13:00", end: "17:00" },
      evening: { enabled: true, start: "18:00", end: "22:00" },
    },
    tue: {
      morning: { enabled: true, start: "08:00", end: "12:00" },
      afternoon: { enabled: true, start: "13:00", end: "17:00" },
      evening: { enabled: true, start: "18:00", end: "22:00" },
    },
    wed: {
      morning: { enabled: false, start: "08:00", end: "12:00" },
      afternoon: { enabled: true, start: "13:00", end: "17:00" },
      evening: { enabled: true, start: "18:00", end: "22:00" },
    },
    thu: {
      morning: { enabled: true, start: "08:00", end: "12:00" },
      afternoon: { enabled: false, start: "13:00", end: "17:00" },
      evening: { enabled: true, start: "18:00", end: "22:00" },
    },
    fri: {
      morning: { enabled: true, start: "08:00", end: "12:00" },
      afternoon: { enabled: true, start: "13:00", end: "17:00" },
      evening: { enabled: false, start: "18:00", end: "22:00" },
    },
    sat: {
      morning: { enabled: false, start: "08:00", end: "12:00" },
      afternoon: { enabled: false, start: "13:00", end: "17:00" },
      evening: { enabled: false, start: "18:00", end: "22:00" },
    },
    sun: {
      morning: { enabled: false, start: "08:00", end: "12:00" },
      afternoon: { enabled: false, start: "13:00", end: "17:00" },
      evening: { enabled: false, start: "18:00", end: "22:00" },
    },
  };
}

export function normalizeScheduleFromApi(
  savedSchedule: Record<string, unknown>,
): WeekSchedule {
  const normalized: WeekSchedule = {};

  SCHEDULE_DAYS.forEach((day) => {
    const val = savedSchedule[day];
    if (val && typeof val === "object" && !Array.isArray(val)) {
      const dayVal = val as SavedDaySchedule;
      normalized[day] = {
        morning: {
          enabled: !!dayVal.morning,
          start: dayVal.morning_start || DEFAULT_SLOT.morning.start,
          end: dayVal.morning_end || DEFAULT_SLOT.morning.end,
        },
        afternoon: {
          enabled: !!dayVal.afternoon,
          start: dayVal.afternoon_start || DEFAULT_SLOT.afternoon.start,
          end: dayVal.afternoon_end || DEFAULT_SLOT.afternoon.end,
        },
        evening: {
          enabled: !!dayVal.evening,
          start: dayVal.evening_start || DEFAULT_SLOT.evening.start,
          end: dayVal.evening_end || DEFAULT_SLOT.evening.end,
        },
      };
    } else {
      normalized[day] = {
        morning: { enabled: !!val, start: DEFAULT_SLOT.morning.start, end: DEFAULT_SLOT.morning.end },
        afternoon: {
          enabled: !!val,
          start: DEFAULT_SLOT.afternoon.start,
          end: DEFAULT_SLOT.afternoon.end,
        },
        evening: { enabled: !!val, start: DEFAULT_SLOT.evening.start, end: DEFAULT_SLOT.evening.end },
      };
    }
  });

  return normalized;
}

export function formatScheduleForApi(schedule: WeekSchedule): Record<string, SavedDaySchedule & Record<string, boolean | string>> {
  const formatted: Record<string, SavedDaySchedule & Record<string, boolean | string>> = {};

  Object.keys(schedule).forEach((day) => {
    const dayData = schedule[day];
    formatted[day] = {
      morning: dayData.morning.enabled,
      morning_start: dayData.morning.start,
      morning_end: dayData.morning.end,
      afternoon: dayData.afternoon.enabled,
      afternoon_start: dayData.afternoon.start,
      afternoon_end: dayData.afternoon.end,
      evening: dayData.evening.enabled,
      evening_start: dayData.evening.start,
      evening_end: dayData.evening.end,
    };
  });

  return formatted;
}

export function getFallbackDaySchedule(): DaySchedule {
  return {
    morning: { ...DEFAULT_SLOT.morning },
    afternoon: { ...DEFAULT_SLOT.afternoon },
    evening: { ...DEFAULT_SLOT.evening },
  };
}
