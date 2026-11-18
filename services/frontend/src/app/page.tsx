import { Suspense } from "react";
import { FailureNotice } from "@/components/failure-notice";
import { FieldList } from "@/components/field-list";
import { number } from "@/lib/format";
import { getFarms, getPlots } from "@/lib/registry";
import { SEEDED_PLOT_IDS } from "@/lib/seed";

export default function Home() {
  return (
    <main>
      <h1 className="text-4xl font-bold tracking-tight">Your fields</h1>
      <Suspense fallback={<p className="mt-6 text-lg">Loading farms and plots.</p>}>
        <Farms />
      </Suspense>
    </main>
  );
}

const count = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;

async function Farms() {
  const [allFarms, allPlots] = await Promise.all([getFarms(), getPlots()]);
  if (!allFarms.ok) return <div className="mt-6"><FailureNotice title="The farms are not available" failure={allFarms} /></div>;
  if (!allPlots.ok) return <div className="mt-6"><FailureNotice title="The plots are not available" failure={allPlots} /></div>;

  // The farmer sees what came with the database. What the admin adds by hand is on the admin page only (see lib/seed.ts).
  const plots = allPlots.data.filter((plot) => SEEDED_PLOT_IDS.has(plot.id));
  const farmIds = new Set(plots.map((plot) => plot.farm_id));
  const farms = allFarms.data.filter((farm) => farmIds.has(farm.id));
  if (farms.length === 0) return <p className="mt-3 text-lg">There are no farms yet. Ask Netafim to set up your farm.</p>;

  const totalArea = plots.reduce((sum, plot) => sum + plot.area_m2, 0);
  return (
    <>
      <p className="mt-2 text-lg text-muted-foreground">
        {count(farms.length, "farm")}, {count(plots.length, "plot")}, {number(totalArea, 0)} m² in all. Each plot shows today&apos;s answer.
      </p>
      <FieldList farms={farms} plots={plots} admin={false} />
    </>
  );
}
