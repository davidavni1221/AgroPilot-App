import type { Metadata } from "next";
import { Suspense } from "react";
import { BackLink } from "@/components/back-link";
import { FailureNotice } from "@/components/failure-notice";
import { CropForm } from "@/components/forms/crop-form";
import { getCrops } from "@/lib/registry";

export const metadata: Metadata = { title: "Add crop | AgroPilot" };

export default function NewCropPage() {
  return (
    <main className="space-y-6">
      <BackLink />
      <h1 className="text-4xl font-bold tracking-tight">Add a crop</h1>
      <Suspense fallback={<p className="text-lg">Loading the known crops.</p>}>
        <KnownCrops />
      </Suspense>
      <CropForm />
    </main>
  );
}

async function KnownCrops() {
  const crops = await getCrops();
  if (!crops.ok) return <FailureNotice title="The crops are not available" failure={crops} />;
  return (
    <p className="text-lg">
      We already know: <span className="font-bold">{crops.data.map((crop) => crop.name).join(", ")}</span>. You only add a crop that is
      not in this list.
    </p>
  );
}
