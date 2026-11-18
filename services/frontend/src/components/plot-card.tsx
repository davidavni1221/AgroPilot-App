import { ChevronRight, Sprout } from "lucide-react";
import Link from "next/link";
import { Suspense } from "react";
import { PlotToday, PlotTodayFallback } from "@/components/plot-today";
import { cropName, number } from "@/lib/format";
import type { Plot } from "@/lib/types";

/** One plot: its name, crop and area, and today's answer. */
export function PlotCard({ plot, href }: { plot: Plot; href: string }) {
  return (
    <Link
      href={href}
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
  );
}
