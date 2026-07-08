export type TimeSlot = "morning" | "afternoon" | "evening";

export interface SlotDetail {
  enabled: boolean;
  start: string;
  end: string;
}

export interface DaySchedule {
  morning: SlotDetail;
  afternoon: SlotDetail;
  evening: SlotDetail;
}

export type WeekSchedule = Record<string, DaySchedule>;

export interface SavedDaySchedule {
  morning?: boolean;
  morning_start?: string;
  morning_end?: string;
  afternoon?: boolean;
  afternoon_start?: string;
  afternoon_end?: string;
  evening?: boolean;
  evening_start?: string;
  evening_end?: string;
}
