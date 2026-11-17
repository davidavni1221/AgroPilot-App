import Link from "next/link";
import { Suspense } from "react";
import { FailureNotice } from "@/components/failure-notice";
import { buttonVariants } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cropName, number } from "@/lib/format";
import { getFarms, getPlots } from "@/lib/registry";

export default function Home() {
  return (
    <main>
      <h1 className="text-4xl font-bold tracking-tight">Your fields</h1>
      <nav aria-label="Add" className="mt-4 flex flex-wrap gap-2">
        {[
          { href: "/farms/new", label: "Add farm" },
          { href: "/crops/new", label: "Add crop" },
          { href: "/plots/new", label: "Add plot" },
        ].map((item) => (
          <Link key={item.href} href={item.href} className={`${buttonVariants({ variant: "outline" })} h-11 px-4 text-base font-bold`}>
            {item.label}
          </Link>
        ))}
      </nav>
      <Suspense fallback={<p className="mt-6 text-lg">Loading farms and plots.</p>}>
        <Farms />
      </Suspense>
    </main>
  );
}

async function Farms() {
  const [farms, plots] = await Promise.all([getFarms(), getPlots()]);
  if (!farms.ok) return <div className="mt-6"><FailureNotice title="The farms are not available" failure={farms} /></div>;
  if (!plots.ok) return <div className="mt-6"><FailureNotice title="The plots are not available" failure={plots} /></div>;
  if (farms.data.length === 0) return <p className="mt-6 text-lg">There are no farms yet. Add a farm to start.</p>;

  return (
    <div className="mt-6 space-y-8">
      {farms.data.map((farm) => {
        const farmPlots = plots.data.filter((plot) => plot.farm_id === farm.id);
        return (
          <section key={farm.id} aria-labelledby={`farm-${farm.id}`}>
            <h2 id={`farm-${farm.id}`} className="text-2xl font-bold">
              {farm.name}
            </h2>
            {farmPlots.length === 0 ? (
              <p className="mt-2 text-lg text-muted-foreground">No plots on this farm.</p>
            ) : (
              <ul className="mt-3 space-y-3">
                {farmPlots.map((plot) => (
                  <li key={plot.id}>
                    <Link
                      href={`/plots/${plot.id}`}
                      className="block rounded-xl focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
                    >
                      <Card className="px-4 py-4 transition-colors hover:bg-secondary">
                        <span className="text-xl font-bold">{plot.name}</span>
                        <span className="text-base text-muted-foreground">
                          {cropName(plot.crop_id)}, {number(plot.area_m2, 0)} m²
                        </span>
                      </Card>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </section>
        );
      })}
    </div>
  );
}
