import { ChevronRight, Sprout } from "lucide-react";
import Link from "next/link";
import { Suspense } from "react";
import { AddActions } from "@/components/add-actions";
import { FailureNotice } from "@/components/failure-notice";
import { PlotToday, PlotTodayFallback } from "@/components/plot-today";
import { cropName, number } from "@/lib/format";
import { getFarms, getPlots } from "@/lib/registry";

export default function Home() {
  return (
    <main>
      <h1 className="text-4xl font-bold tracking-tight">Your fields</h1>
      <Suspense fallback={<p className="mt-6 text-lg">Loading farms and plots.</p>}>
        <Farms />
      </Suspense>
      <AddActions />
    </main>
  );
}

const count = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;

async function Farms() {
  const [farms, plots] = await Promise.all([getFarms(), getPlots()]);
  if (!farms.ok) return <div className="mt-6"><FailureNotice title="The farms are not available" failure={farms} /></div>;
  if (!plots.ok) return <div className="mt-6"><FailureNotice title="The plots are not available" failure={plots} /></div>;
  if (farms.data.length === 0) return <p className="mt-3 text-lg">There are no farms yet. Add one below to start.</p>;

  const totalArea = plots.data.reduce((sum, plot) => sum + plot.area_m2, 0);
  return (
    <>
      <p className="mt-2 text-lg text-muted-foreground">
        {count(farms.data.length, "farm")}, {count(plots.data.length, "plot")}, {number(totalArea, 0)} m² in all.
        Each plot shows today&apos;s answer.
      </p>
      <div className="mt-8 space-y-10">
        {farms.data.map((farm) => {
          const farmPlots = plots.data.filter((plot) => plot.farm_id === farm.id);
          const area = farmPlots.reduce((sum, plot) => sum + plot.area_m2, 0);
          return (
            <section key={farm.id} aria-labelledby={`farm-${farm.id}`}>
              <div className="flex flex-wrap items-baseline justify-between gap-x-4">
                <h2 id={`farm-${farm.id}`} className="text-2xl font-bold">
                  {farm.name}
                </h2>
                <p className="text-base text-muted-foreground">
                  {count(farmPlots.length, "plot")}, {number(area, 0)} m²
                </p>
              </div>
              {farmPlots.length === 0 ? (
                <p className="mt-2 text-lg text-muted-foreground">No plots on this farm yet.</p>
              ) : (
                <ul className="mt-3 grid gap-3 sm:grid-cols-2">
                  {farmPlots.map((plot) => (
                    <li key={plot.id}>
                      <Link
                        href={`/plots/${plot.id}`}
                        className="group flex h-full flex-col gap-3 rounded-2xl bg-card p-4 ring-1 ring-foreground/10 transition-colors hover:bg-secondary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
                      >
                        <span className="flex items-start gap-3">
                          <span aria-hidden className="flex size-11 shrink-0 items-center justify-center rounded-full bg-secondary group-hover:bg-card">
                            <Sprout className="size-6 text-dry" />
                          </span>
                          <span className="flex-1">
                            <span className="block text-xl font-bold">{plot.name}</span>
                            <span className="block text-base text-muted-foreground">
                              {cropName(plot.crop_id)}, {number(plot.area_m2, 0)} m²
                            </span>
                          </span>
                          <ChevronRight aria-hidden className="mt-1 size-5 shrink-0 text-muted-foreground transition-transform group-hover:translate-x-0.5" />
                        </span>
                        <span>
                          <Suspense fallback={<PlotTodayFallback />}>
                            <PlotToday plotId={plot.id} />
                          </Suspense>
                        </span>
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          );
        })}
      </div>
    </>
  );
}
