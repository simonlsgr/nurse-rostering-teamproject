import { Nurse } from "@/types/nurseVars";
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(
  input: string | null,
  type: "weekday" | "date" | "time" | "datetime" = "datetime"
) {
  if (!input) return "--";
  
  const date = new Date(input);

  if (type === "weekday") {
    return date.toLocaleDateString("de-DE", { weekday: "short" });
  }

  if (type === "date") {
    return date.toLocaleDateString("de-DE");
  }

  if (type === "time") {
    return date.toLocaleTimeString("de-DE");
  }

  return date.toLocaleString("de-DE");
}

export function generateUID(): number {
  return Date.now() * 1000 + Math.floor(Math.random() * 1000);
}

export function createDefaultNurse(): Nurse {
  return {
    id: crypto.randomUUID(),
    uid: generateUID(),
    name: "",
    preferred_shifts: [],
    preferred_off_shifts: [],
    blocked_shifts: [],
    days_off: [],
    staff: true,
    min_time_between_shifts: "PT0S",
    preferred_shift_weight: {},
    preferred_off_shift_weight: {},
    minimum_work_time: 0,
    maximum_work_time: 0,
    minimum_consecutive_shifts: 0,
    maximum_consecutive_shifts: 0,
    minimum_consecutive_days_off: 0,
    maximum_weekends: 0,
    maximum_number_of_shifts_per_type: {},
  };
}

