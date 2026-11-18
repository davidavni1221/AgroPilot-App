import Link from "next/link";
import { removeFarm } from "@/app/actions";
import { DeleteButton } from "@/components/forms/delete-button";
import { PlotCard } from "@/components/plot-card";
import { PlotSearch, type SearchGroup } from "@/components/plot-search";
import { cropName, number } from "@/lib/format";
import type { Farm, Plot } from "@/lib/types";

const count = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;
const byName = (a: { name: string }, b: { name: string }) => a.name.localeCompare(b.name, "en", { sensitivity: "base" });

/** The farmer's list and the admin's list are the same, sorted A to Z. The admin's also has the farm buttons, and its cards open the admin page of the plot. */
export function FieldList({ farms, plots, admin }: { farms: Farm[]; plots: Plot[]; admin: boolean }) {
  const groups: SearchGroup[] = [...farms].sort(byName).map((farm) => {
    const farmPlots = plots.filter((plot) => plot.farm_id === farm.id).sort(byName);
    const area = farmPlots.reduce((sum, plot) => sum + plot.area_m2, 0);
    return {
      id: farm.id,
      name: farm.name,
      summary: `${count(farmPlots.length, "plot")}, ${number(area, 0)} m²`,
      emptyNote: "No plots on this farm yet.",
      actions: admin ? (
        <>
          <Link
            href={`/admin/farms/${encodeURIComponent(farm.id)}/edit`}
            className="inline-block text-base font-bold underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
          >
            Change the farm name
          </Link>
          {farmPlots.length === 0 && (
            <DeleteButton
              action={removeFarm}
              id={farm.id}
              label="Delete this farm"
              question={`Delete ${farm.name}? This cannot be undone.`}
            />
          )}
        </>
      ) : undefined,
      plots: farmPlots.map((plot) => ({
        id: plot.id,
        text: `${plot.name} ${farm.name} ${cropName(plot.crop_id)}`.toLowerCase(),
        card: <PlotCard plot={plot} href={`${admin ? "/admin" : ""}/plots/${encodeURIComponent(plot.id)}`} />,
      })),
    };
  });
  return <PlotSearch groups={groups} />;
}
