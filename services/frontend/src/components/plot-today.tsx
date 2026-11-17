import { CircleCheck, Clock, Droplets } from "lucide-react";
import { wholeMinutes } from "@/lib/format";
import { getPlan } from "@/lib/planner";

const pill = "inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-base font-bold";

/** Today's answer for one plot, as a small pill on its card. It asks the planner, so it can take a few seconds. */
export async function PlotToday({ plotId }: { plotId: string }) {
  const plan = await getPlan(plotId);
  if (!plan.ok) {
    return (
      <span className={`${pill} bg-stale-bg text-stale`}>
        <Clock aria-hidden className="size-4" />
        Plan not available
      </span>
    );
  }
  const today = plan.data.days[0];
  if (today.run_minutes > 0) {
    return (
      <span className={`${pill} bg-water text-primary-foreground`}>
        <Droplets aria-hidden className="size-4" />
        Water for {wholeMinutes(today.run_minutes)} min
      </span>
    );
  }
  return (
    <span className={`${pill} bg-secondary text-foreground`}>
      <CircleCheck aria-hidden className="size-4" />
      No water today
    </span>
  );
}

export function PlotTodayFallback() {
  return <span className={`${pill} bg-secondary text-muted-foreground`}>Checking today</span>;
}
