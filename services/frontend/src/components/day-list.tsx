import { BucketGauge } from "@/components/bucket-gauge";
import { dayLabel, duration, number } from "@/lib/format";
import type { Plan } from "@/lib/types";

/** The plan for the week, one row per day. A list and not a wide table, so it fits a phone. */
export function DayList({ plan }: { plan: Plan }) {
  return (
    <section aria-labelledby="week">
      <h2 id="week" className="text-2xl font-bold">
        The next 7 days
      </h2>
      <ol className="mt-3 divide-y divide-border rounded-xl bg-card">
        {plan.days.map((day, index) => {
          const waters = day.run_minutes > 0;
          return (
            <li key={day.date} className="px-4 py-3">
              <div className="flex items-baseline justify-between gap-3">
                <span className="text-lg font-bold">{dayLabel(day.date, index)}</span>
                <span className={`text-lg font-bold ${waters ? "text-water" : "text-dry"}`}>
                  {waters ? `${duration(day.run_minutes)}` : "No water"}
                </span>
              </div>
              <div className="mt-2">
                <BucketGauge level={day.bucket_end_mm} capacity={plan.bucket_capacity_mm} />
              </div>
              <p className="mt-2 text-sm text-muted-foreground">
                {waters && `${number(day.litres, 0)} litres. `}
                {day.rain_mm > 0 ? `Rain ${number(day.rain_mm)} mm. ` : "No rain. "}
                Crop uses {number(day.etc_mm)} mm (ET0 {number(day.et0_mm)} mm, Kc {number(day.kc, 2)}).
              </p>
              {day.stale && <p className="mt-1 text-sm font-bold text-stale">Based on an old forecast.</p>}
            </li>
          );
        })}
      </ol>
    </section>
  );
}
