import { removeFarm } from "@/app/actions";
import { DeleteButton } from "@/components/forms/delete-button";
import { getFarms, getPlots } from "@/lib/registry";

/** Removing a farm, at the very bottom of the home page. Like the registry, only a farm with no plots can go. */
export async function RemoveFarms() {
  const [farms, plots] = await Promise.all([getFarms(), getPlots()]);
  if (!farms.ok || !plots.ok || farms.data.length === 0) return null;

  return (
    <section aria-labelledby="remove" className="mt-10 border-t border-border pt-8">
      <h2 id="remove" className="text-2xl font-bold">
        Remove a farm
      </h2>
      <p className="mt-1 text-base text-muted-foreground">A farm can be removed when it has no plots. Delete its plots first.</p>
      <ul className="mt-4 space-y-4">
        {farms.data.map((farm) => {
          const count = plots.data.filter((plot) => plot.farm_id === farm.id).length;
          return (
            <li key={farm.id} className="space-y-2">
              <p className="text-lg font-bold">{farm.name}</p>
              {count > 0 ? (
                <p className="text-base text-muted-foreground">
                  Has {count} {count === 1 ? "plot" : "plots"}. Delete {count === 1 ? "it" : "them"} first.
                </p>
              ) : (
                <DeleteButton
                  action={removeFarm}
                  id={farm.id}
                  label="Delete this farm"
                  question={`Delete ${farm.name}? This cannot be undone.`}
                />
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
