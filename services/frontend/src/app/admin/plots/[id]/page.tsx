import { Pencil } from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";
import { removePlot } from "@/app/actions";
import { BackLink } from "@/components/back-link";
import { DeleteButton } from "@/components/forms/delete-button";
import { PlotView } from "@/components/plot-view";
import { getPlot } from "@/lib/registry";

export const metadata: Metadata = { title: "Plot | Admin | AgroPilot" };

/** What the farmer sees for the plot, and under it the admin's buttons to change or delete it. */
export default function AdminPlotPage({ params }: { params: Promise<{ id: string }> }) {
  return (
    <main className="space-y-8">
      <BackLink />
      <Suspense fallback={<p className="text-lg">Working out today&apos;s plan. This can take a few seconds.</p>}>
        <AdminPlot params={params} />
      </Suspense>
    </main>
  );
}

async function AdminPlot({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const plot = await getPlot(id);
  return (
    <>
      <PlotView id={id} />
      {plot.ok && (
        <section aria-labelledby="manage" className="space-y-3 border-t border-border pt-8">
          <h2 id="manage" className="text-2xl font-bold">
            Manage this plot
          </h2>
          <Link
            href={`/admin/plots/${encodeURIComponent(id)}/edit`}
            className="inline-flex h-11 items-center gap-2 rounded-xl px-5 text-base font-bold ring-1 ring-foreground/15 transition-colors hover:bg-secondary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
          >
            <Pencil aria-hidden className="size-4" />
            Change this plot
          </Link>
          <DeleteButton
            action={removePlot}
            id={id}
            label="Delete this plot"
            question={`Delete ${plot.data.name}? This cannot be undone.`}
          />
        </section>
      )}
    </>
  );
}
