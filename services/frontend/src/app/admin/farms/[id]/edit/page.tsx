import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Suspense } from "react";
import { BackLink } from "@/components/back-link";
import { FailureNotice } from "@/components/failure-notice";
import { FarmForm } from "@/components/forms/farm-form";
import { getFarm } from "@/lib/registry";

export const metadata: Metadata = { title: "Change farm | AgroPilot" };

export default function EditFarmPage({ params }: { params: Promise<{ id: string }> }) {
  return (
    <main className="space-y-6">
      <BackLink />
      <h1 className="text-4xl font-bold tracking-tight">Change the farm name</h1>
      <Suspense fallback={<p className="text-lg">Loading the farm.</p>}>
        <Loader params={params} />
      </Suspense>
    </main>
  );
}

async function Loader({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const farm = await getFarm(id);
  if (!farm.ok && farm.kind === "not-found") notFound();
  if (!farm.ok) return <FailureNotice title="This farm is not available" failure={farm} />;
  return <FarmForm farm={farm.data} />;
}
