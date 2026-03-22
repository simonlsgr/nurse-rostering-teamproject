import { Nurse, Shift } from "@/types/nurseVars";
import { NewProject, ShiftType } from "@/types/projectVars";
import { clsx, type ClassValue } from "clsx"
import { labelDayButton } from "react-day-picker";
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(
  input: string | undefined,
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

export function toGermanTime(time: string){
  new Date(time).toLocaleString("de-DE", {
    timeZone: "Europe/Berlin"
  });
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

export function createDefaultNewProject(): NewProject {
  return {

    id: crypto.randomUUID(),
    name: "",
  }
} 


export function generateDatesFromPlanningHorizon(planningHorizon: [string, string]) {
  const [startStr, endStr] = planningHorizon;
  const startDate = new Date(startStr);
  const endDate = new Date(endStr);

  const dates: string[] = [];
  let current = new Date(startDate);

  while (current <= endDate) {
    dates.push(current.toISOString().split("T")[0]); // nur "YYYY-MM-DD"
    current.setDate(current.getDate() + 1); // nächsten Tag
  }

  return dates;
}

export function convertShiftTypes(shiftTypes: ShiftType[]) {

  let result = [{value: "", label: ""}];

  shiftTypes.forEach((type) => {
    
    result.push({value: type.name, label: type.name});
  });

  return result;
}

export function calculateStringDifference(
  left: string[],
  right: string[]
): [string[], string[]] {
  const leftSet = new Set(left);
  const rightSet = new Set(right);

  const leftOnly = [...leftSet].filter((item) => !rightSet.has(item));
  const rightOnly = [...rightSet].filter((item) => !leftSet.has(item));

  return [leftOnly, rightOnly];
}


type ValidationResult = {
  valid: boolean;
  error?: string;
};

export function validateNursesImport(
  nurses: Nurse[],
  shiftTypes: ShiftType[],
  planningHorizon?: [string, string]
): ValidationResult {

  const seen = new Set<number>();

  for (let i = 0; i < nurses.length; i++) {
    const uid = nurses[i].uid;

    if (seen.has(uid)) {
      return {
        valid: false,
        error: `Duplicate uid found: ${uid} (index ${i})`
      };
    }

    seen.add(uid);
  }

  const validShiftTypes = new Set(shiftTypes.map(st => st.name));

  for (let i = 0; i < nurses.length; i++) {
    const nurse = nurses[i];

    const keys = Object.keys(nurse.maximum_number_of_shifts_per_type || {});

    for (const key of keys) {
      if (!validShiftTypes.has(key)) {
        return {
          valid: false,
          error: `Invalid shift type "${key}" in nurse "${nurse.name}" (index ${i})`
        };
      }
    }
  }

  if (planningHorizon) {
    const [start, end] = planningHorizon;

    const startDate = new Date(start);
    const endDate = new Date(end);

    for (let i = 0; i < nurses.length; i++) {
      const nurse = nurses[i];

      for (const day of nurse.days_off || []) {
        const d = new Date(day);

        if (d < startDate || d > endDate) {
          return {
            valid: false,
            error: `Day off ${day} of nurse "${nurse.name}" is outside planning horizon`
          };
        }
      }
    }
  }

  return { valid: true };
}


export function sortShiftsByStartTime(shifts: Shift[]): Shift[] {
  return [...shifts].sort((a, b) =>
    a.start_time.localeCompare(b.start_time)
  );
}