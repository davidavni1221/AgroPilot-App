import { number } from "@/lib/format";

/** The soil as a bucket. The mark is the half line: below it the plan waters. */
export function BucketGauge({ level, capacity, large = false }: { level: number; capacity: number; large?: boolean }) {
  const share = Math.min(1, Math.max(0, level / capacity));
  return (
    <div
      role="img"
      aria-label={`Soil water ${number(level)} of ${number(capacity)} millimetres. Watering starts below half.`}
      className={`relative w-full overflow-hidden rounded-full bg-secondary ${large ? "h-5" : "h-2"}`}
    >
      <div className="h-full rounded-full bg-water" style={{ width: `${share * 100}%` }} />
      <div className="absolute inset-y-0 left-1/2 w-0.5 bg-foreground/70" />
    </div>
  );
}
