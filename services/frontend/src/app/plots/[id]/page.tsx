import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Suspense } from "react";
import { DayList } from "@/components/day-list";
import { FailureNotice } from "@/components/failure-notice";
import { Recommendation } from "@/components/recommendation";
import { getPlan } from "@/lib/planner";
import { getPlot } from "@/lib/registry";

export const metadata: Metadata = { title: "Plot | AgroPilot" };

/** One plot: today's recommendation first, big, then the next 7 days. */
export default function PlotPage({ params }: { params: Promise<{ id: string }> }) {
  return (
    <main className="space-y-8">
      <Link href="/" className="text-base font-bold underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring">
        Back to your fields
      </Link>
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

  // A phone: one column. A wide screen: today on the left, the week (chart and table side by side) on the right.
  return (
    <div className="space-y-10 lg:grid lg:grid-cols-[minmax(0,1fr)_minmax(0,2fr)] lg:items-start lg:gap-12 lg:space-y-0">
      <Recommendation plan={plan.data} plot={plot.data} />
      <DayList plan={plan.data} />
    </div>
  );
}
