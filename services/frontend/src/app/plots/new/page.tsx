import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";
import { BackLink } from "@/components/back-link";
import { FailureNotice } from "@/components/failure-notice";
import { PlotForm } from "@/components/forms/plot-form";
import { getCrops, getEmitters, getFarms, getSoils } from "@/lib/registry";

export const metadata: Metadata = { title: "Add plot | AgroPilot" };

export default function NewPlotPage({ searchParams }: { searchParams: Promise<{ farm?: string; crop?: string; known?: string }> }) {
  return (
    <main className="space-y-6">
      <BackLink />
      <h1 className="text-4xl font-bold tracking-tight">Add a plot</h1>
      <Suspense fallback={<p className="text-lg">Loading the lists.</p>}>
        <PlotFormLoader searchParams={searchParams} />
      </Suspense>
    </main>
  );
}

async function PlotFormLoader({ searchParams }: { searchParams: Promise<{ farm?: string; crop?: string; known?: string }> }) {
  const [{ farm, crop, known }, farms, crops, soils, emitters] = await Promise.all([
    searchParams,
    getFarms(),
    getCrops(),
    getSoils(),
    getEmitters(),
  ]);
  if (!farms.ok) return <FailureNotice title="The farms are not available" failure={farms} />;
  if (!crops.ok) return <FailureNotice title="The crops are not available" failure={crops} />;
  if (!soils.ok) return <FailureNotice title="The soils are not available" failure={soils} />;
  if (!emitters.ok) return <FailureNotice title="The emitters are not available" failure={emitters} />;

  if (farms.data.length === 0) {
    return (
      <p className="text-lg">
        A plot belongs to a farm.{" "}
        <Link href="/farms/new" className="font-bold underline underline-offset-4">
          Add a farm first.
        </Link>
      </p>
    );
  }

  const knownCrop = known ? crops.data.find((c) => c.id === crop) : undefined;
  return (
    <>
      {knownCrop && (
        <p className="rounded-lg bg-card px-4 py-3 text-base font-bold">
          We already know {knownCrop.name}, so we use the numbers we have for it.
        </p>
      )}
      <PlotForm farms={farms.data} crops={crops.data} soils={soils.data} emitters={emitters.data} defaults={{ farm, crop }} />
    </>
  );
}
