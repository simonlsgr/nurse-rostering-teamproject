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
