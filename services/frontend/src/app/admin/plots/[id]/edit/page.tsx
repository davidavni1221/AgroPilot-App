import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Suspense } from "react";
import { BackLink } from "@/components/back-link";
import { FailureNotice } from "@/components/failure-notice";
import { PlotForm } from "@/components/forms/plot-form";
import { getCrops, getEmitters, getFarms, getPlot, getSoils } from "@/lib/registry";

export const metadata: Metadata = { title: "Change plot | AgroPilot" };

export default function EditPlotPage({ params }: { params: Promise<{ id: string }> }) {
  return (
    <main className="space-y-6">
      <Suspense fallback={null}>
        <Back params={params} />
      </Suspense>
      <h1 className="text-4xl font-bold tracking-tight">Change this plot</h1>
      <Suspense fallback={<p className="text-lg">Loading the plot.</p>}>
        <Loader params={params} />
      </Suspense>
    </main>
  );
}

async function Back({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <BackLink href={`/admin/plots/${encodeURIComponent(id)}`}>Back to the plot</BackLink>;
}

async function Loader({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [plot, farms, crops, soils, emitters] = await Promise.all([getPlot(id), getFarms(), getCrops(), getSoils(), getEmitters()]);
  if (!plot.ok && plot.kind === "not-found") notFound();
  if (!plot.ok) return <FailureNotice title="This plot is not available" failure={plot} />;
  if (!farms.ok) return <FailureNotice title="The farms are not available" failure={farms} />;
  if (!crops.ok) return <FailureNotice title="The crops are not available" failure={crops} />;
  if (!soils.ok) return <FailureNotice title="The soils are not available" failure={soils} />;
  if (!emitters.ok) return <FailureNotice title="The emitters are not available" failure={emitters} />;
  return <PlotForm farms={farms.data} crops={crops.data} soils={soils.data} emitters={emitters.data} defaults={{}} plot={plot.data} />;
}
