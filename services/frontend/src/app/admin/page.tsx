import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";
import { AddActions } from "@/components/add-actions";
import { FailureNotice } from "@/components/failure-notice";
import { FieldList } from "@/components/field-list";
import { getFarms, getPlots } from "@/lib/registry";

export const metadata: Metadata = { title: "Admin | AgroPilot" };

export default function AdminPage() {
  return (
    <main>
      <Link href="/" className="text-base font-bold underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring">
        Back to your fields
      </Link>
      <h1 className="mt-6 text-4xl font-bold tracking-tight">Admin</h1>
      <p className="mt-2 text-lg text-muted-foreground">For the Netafim team: every farm and plot, and where to set them up.</p>
      <AddActions />
      <section aria-labelledby="all" className="mt-14 border-t border-border pt-8">
        <h2 id="all" className="text-2xl font-bold">
          All farms and plots
        </h2>
        <p className="mt-1 text-base text-muted-foreground">
          Open a plot to change or delete it. A farm can be deleted when it has no plots.
        </p>
        <Suspense fallback={<p className="mt-6 text-lg">Loading farms and plots.</p>}>
          <Everything />
        </Suspense>
      </section>
    </main>
  );
}

async function Everything() {
  const [farms, plots] = await Promise.all([getFarms(), getPlots()]);
  if (!farms.ok) return <div className="mt-6"><FailureNotice title="The farms are not available" failure={farms} /></div>;
  if (!plots.ok) return <div className="mt-6"><FailureNotice title="The plots are not available" failure={plots} /></div>;
  if (farms.data.length === 0) return <p className="mt-6 text-lg">There are no farms yet.</p>;
  return <FieldList farms={farms.data} plots={plots.data} admin />;
}
