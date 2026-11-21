import { ChevronRight, Sprout } from "lucide-react";
import Link from "next/link";
import { Suspense } from "react";
import { PlotActions } from "@/components/forms/edit-buttons";
import { PlotToday, PlotTodayFallback } from "@/components/plot-today";
import { cropName, number } from "@/lib/format";
import { getPlan } from "@/lib/planner";
import type { Plot } from "@/lib/types";

/**
 * One plot: its name, crop, area and today's answer. The card opens the plot's own page, /plots/{id}. The change and delete buttons
 * sit on the card, outside the link, so tapping them never opens the page. Name and crop take one line each, so every card is the same size.
 */
export function PlotCard({ plot, farmName, last }: { plot: Plot; farmName: string; last: boolean }) {
  const plan = getPlan(plot.id);
  return (
    <div className="relative rounded-2xl bg-card ring-1 ring-foreground/10">
      <Link
        href={`/plots/${encodeURIComponent(plot.id)}`}
        className="group flex flex-col gap-3 rounded-2xl p-4 transition-colors hover:bg-secondary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
      >
        <span className="flex items-start gap-3 pe-24">
          <span aria-hidden className="flex size-11 shrink-0 items-center justify-center rounded-full bg-secondary group-hover:bg-card xl:hidden">
            <Sprout className="size-6 text-dry" />
          </span>
          <span className="min-w-0 flex-1">
            <span className="block truncate text-xl font-bold" title={plot.name}>
              {plot.name}
            </span>
            <span className="block truncate text-base text-muted-foreground">
              {cropName(plot.crop_id)}, {number(plot.area_m2, 0)} m²
            </span>
          </span>
        </span>
        <span className="flex items-center justify-between gap-3">
          <Suspense fallback={<PlotTodayFallback />}>
            <PlotToday plan={plan} />
          </Suspense>
          <ChevronRight aria-hidden className="size-5 shrink-0 text-muted-foreground transition-transform group-hover:translate-x-0.5" />
        </span>
      </Link>
      <div className="absolute end-3 top-3">
        <PlotActions plot={plot} farmName={farmName} last={last} />
      </div>
    </div>
  );
}
