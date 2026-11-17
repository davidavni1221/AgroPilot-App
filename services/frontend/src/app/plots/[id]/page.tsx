import { notFound } from "next/navigation";
import { Suspense } from "react";
import { DayList } from "@/components/day-list";
import { removePlot } from "@/app/actions";
import { DeleteButton } from "@/components/forms/delete-button";
import { FailureNotice } from "@/components/failure-notice";
import { Recommendation } from "@/components/recommendation";
import { getPlan } from "@/lib/planner";
import { getPlot } from "@/lib/registry";

export default function PlotPage({ params }: { params: Promise<{ id: string }> }) {
  return (
    <main>
      <Suspense fallback={<p className="text-lg">Working out today&apos;s plan. This can take a few seconds.</p>}>
        <PlotContent params={params} />
      </Suspense>
    </main>
  );
}

async function PlotContent({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [plot, plan] = await Promise.all([getPlot(id), getPlan(id)]);

  if (!plot.ok && plot.kind === "not-found") notFound();
  if (!plan.ok && plan.kind === "not-found") notFound();
  if (!plot.ok) return <FailureNotice title="This plot is not available" failure={plot} />;
  if (!plan.ok) return <FailureNotice title="There is no plan for this plot right now" failure={plan} />;

  return (
    <div className="space-y-10">
      <Recommendation plan={plan.data} plot={plot.data} />
      <DayList plan={plan.data} />
      <section aria-labelledby="remove" className="border-t border-border pt-8">
        <h2 id="remove" className="text-2xl font-bold">
          Remove this plot
        </h2>
        <p className="mt-1 mb-4 text-base text-muted-foreground">It disappears from your fields. Other plots are not touched.</p>
        <DeleteButton
          action={removePlot}
          id={plot.data.id}
          label="Delete this plot"
          question={`Delete ${plot.data.name}? This cannot be undone.`}
        />
      </section>
    </div>
  );
}
