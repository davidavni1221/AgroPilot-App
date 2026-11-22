export function cropName(id: string): string {
  const text = id.replace(/-/g, " ");
  return text.charAt(0).toUpperCase() + text.slice(1);
}

const dateFormat = new Intl.DateTimeFormat("en-GB", { weekday: "short", day: "numeric", month: "short", timeZone: "UTC" });

/** The first day of a plan is today, the second is tomorrow. The dates come from the plan, not from this computer's clock. */
export function dayLabel(date: string, index: number): string {
  if (index === 0) return "Today";
  if (index === 1) return "Tomorrow";
  return dateFormat.format(new Date(`${date}T00:00:00Z`));
}

/** Whole minutes for people. The plan itself keeps one decimal. */
export function wholeMinutes(minutes: number): number {
  return Math.max(1, Math.round(minutes));
}

export function duration(minutes: number): string {
  const whole = wholeMinutes(minutes);
  if (whole < 90) return `${whole} minutes`;
  return `${whole} minutes (${Math.floor(whole / 60)} h ${whole % 60} min)`;
}

/** "1 h 55 min" for long runs, so the headline can stay short. Nothing for a run under 90 minutes. */
export function hoursAndMinutes(minutes: number): string | null {
  const whole = wholeMinutes(minutes);
  return whole < 90 ? null : `${Math.floor(whole / 60)} h ${whole % 60} min`;
}

export const number = (value: number, digits = 1) =>
  new Intl.NumberFormat("en-GB", { maximumFractionDigits: digits }).format(value);
