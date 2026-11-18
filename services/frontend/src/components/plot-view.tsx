import { notFound } from "next/navigation";
import { DayList } from "@/components/day-list";
import { FailureNotice } from "@/components/failure-notice";
import { Recommendation } from "@/components/recommendation";
import { getPlan } from "@/lib/planner";
import { getPlot } from "@/lib/registry";

/** Today's answer and the next 7 days for one plot. The farmer's page and the admin's page show the same. */
export async function PlotView({ id }: { id: string }) {
  const [plot, plan] = await Promise.all([getPlot(id), getPlan(id)]);

  if (!plot.ok && plot.kind === "not-found") notFound();
  if (!plan.ok && plan.kind === "not-found") notFound();
  if (!plot.ok) return <FailureNotice title="This plot is not available" failure={plot} />;
  if (!plan.ok) return <FailureNotice title="There is no plan for this plot right now" failure={plan} />;

  return (
    <div className="space-y-10">
      <Recommendation plan={plan.data} plot={plot.data} />
      <DayList plan={plan.data} />
    </div>
  );
}
