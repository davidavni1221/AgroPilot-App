import { CircularProgress, CircularProgressValue } from "@/components/ui/circular-progress";
import { number } from "@/lib/format";

/** The soil bucket as a ring: how full it is at the end of the day. */
export function SoilRing({ level, capacity }: { level: number; capacity: number }) {
  const percent = Math.round(Math.min(100, Math.max(0, (level / capacity) * 100)));
  return (
    <CircularProgress
      value={percent}
      size={96}
      thickness={10}
      aria-label={`Estimated soil water ${number(level)} of ${number(capacity)} millimetres, ${percent} percent`}
      className="shrink-0"
    >
      <CircularProgressValue className="text-lg font-bold">{percent}%</CircularProgressValue>
    </CircularProgress>
  );
}
