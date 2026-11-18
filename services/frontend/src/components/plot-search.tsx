"use client";

import { Search } from "lucide-react";
import { useState, type ReactNode } from "react";

export type SearchPlot = { id: string; text: string; card: ReactNode };
export type SearchGroup = {
  id: string;
  name: string;
  summary: string;
  actions?: ReactNode; // admin only: edit the farm's name, delete an empty farm
  emptyNote: string;
  plots: SearchPlot[];
};

/**
 * The farms with their plots, and a box that filters them as you type. It filters what the page already loaded, so there is no
 * request per keystroke. A farm whose name matches keeps all its plots; otherwise only the plots whose own text matches stay.
 * The text of a plot is its name, its farm and its crop, already in lower case.
 */
export function PlotSearch({ groups }: { groups: SearchGroup[] }) {
  const [query, setQuery] = useState("");
  const q = query.trim().toLowerCase();

  const shown = groups.flatMap((group) => {
    if (!q) return [group];
    const farmMatches = group.name.toLowerCase().includes(q);
    const plots = farmMatches ? group.plots : group.plots.filter((plot) => plot.text.includes(q));
    return farmMatches || plots.length > 0 ? [{ ...group, plots }] : [];
  });

  return (
    <>
      <div className="relative mt-6 max-w-sm">
        <label htmlFor="plot-search" className="sr-only">
          Search farms and plots
        </label>
        <Search aria-hidden className="pointer-events-none absolute start-3 top-1/2 size-5 -translate-y-1/2 text-muted-foreground" />
        <input
          id="plot-search"
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search farms and plots"
          autoComplete="off"
          className="h-11 w-full rounded-lg border border-input bg-card ps-10 pe-3 text-base outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
        />
      </div>
      <p aria-live="polite" className="mt-3 text-base text-muted-foreground">
        {q && shown.length === 0 ? `Nothing matches "${query.trim()}".` : ""}
      </p>
      <div className="mt-5 space-y-10">
        {shown.map((group) => (
          <section key={group.id} aria-labelledby={`farm-${group.id}`}>
            <div className="flex flex-wrap items-baseline justify-between gap-x-4">
              <h2 id={`farm-${group.id}`} className="text-2xl font-bold">
                {group.name}
              </h2>
              <p className="text-base text-muted-foreground">{group.summary}</p>
            </div>
            {group.actions && <div className="mt-2 space-y-3">{group.actions}</div>}
            {group.plots.length === 0 ? (
              <p className="mt-2 text-lg text-muted-foreground">{group.emptyNote}</p>
            ) : (
              <ul className="mt-3 grid gap-3 sm:grid-cols-2">
                {group.plots.map((plot) => (
                  <li key={plot.id}>{plot.card}</li>
                ))}
              </ul>
            )}
          </section>
        ))}
      </div>
    </>
  );
}
