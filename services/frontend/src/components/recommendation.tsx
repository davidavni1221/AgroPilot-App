import { BucketGauge } from "@/components/bucket-gauge";
import { cropName, duration, number } from "@/lib/format";
import type { Plan, Plot } from "@/lib/types";

/** Today's answer, first and big. */
export function Recommendation({ plan, plot }: { plan: Plan; plot: Plot }) {
  const today = plan.days[0];
  const waters = today.run_minutes > 0;
  return (
    <section aria-labelledby="today">
      <h1 id="today" className={`text-5xl leading-[1.05] font-bold tracking-tight ${waters ? "text-water" : "text-dry"}`}>
        {waters ? `Water for ${duration(today.run_minutes)}` : "No irrigation today"}
      </h1>
      <p className="mt-3 text-lg">
        {waters
          ? `${number(today.need_mm)} mm, ${number(today.litres, 0)} litres on ${plot.name}.`
          : `${plot.name} has enough water for today.`}
      </p>
      {plan.stale && (
        <p className="mt-4 rounded-lg bg-stale-bg px-4 py-3 text-base font-bold text-stale">
          The weather forecast is out of date. This plan uses the last forecast we received.
        </p>
      )}
      <div className="mt-6">
        <BucketGauge level={today.bucket_end_mm} capacity={plan.bucket_capacity_mm} large />
        <p className="mt-2 text-base text-muted-foreground">
          Soil water at the end of today: {number(today.bucket_end_mm)} of {number(plan.bucket_capacity_mm)} mm.
          Watering starts when it would fall below half.
        </p>
      </div>
      <p className="mt-4 text-base text-muted-foreground">
        {cropName(plot.crop_id)}, {number(plot.area_m2, 0)} m².
      </p>
    </section>
  );
}
