import { FarmActions } from "@/components/forms/edit-buttons";
import { PlotCard } from "@/components/plot-card";
import { PlotSearch, type SearchGroup } from "@/components/plot-search";
import { cropName, number } from "@/lib/format";
import type { Farm, Plot } from "@/lib/types";

const count = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;
const byName = (a: { name: string }, b: { name: string }) => a.name.localeCompare(b.name, "en", { sensitivity: "base" });

/** Every farm with its plots, sorted A to Z. The farm's buttons are beside its name, the plot's buttons on its card. */
export function FieldList({ farms, plots }: { farms: Farm[]; plots: Plot[] }) {
  const groups: SearchGroup[] = [...farms].sort(byName).map((farm) => {
    const farmPlots = plots.filter((plot) => plot.farm_id === farm.id).sort(byName);
    const area = farmPlots.reduce((sum, plot) => sum + plot.area_m2, 0);
    return {
      id: farm.id,
      name: farm.name,
      summary: `${count(farmPlots.length, "plot")}, ${number(area, 0)} m²`,
      emptyNote: "No plots on this farm yet.",
      actions: <FarmActions farm={farm} empty={farmPlots.length === 0} />,
      plots: farmPlots.map((plot) => ({
        id: plot.id,
        text: `${plot.name} ${farm.name} ${cropName(plot.crop_id)}`.toLowerCase(),
        card: <PlotCard plot={plot} farmName={farm.name} last={farmPlots.length === 1} />,
      })),
    };
  });
  return <PlotSearch groups={groups} />;
}
