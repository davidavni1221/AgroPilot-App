"use client";

import { Search } from "lucide-react";
import { useState, type ReactNode } from "react";

export type SearchPlot = { id: string; text: string; card: ReactNode };
export type SearchGroup = {
  id: string;
  name: string;
  summary: string;
  actions: ReactNode; // beside the farm's name: change the name, delete an empty farm
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
      {groups.length > 0 && (
        <div className="mt-2 flex justify-end">
          <div className="relative w-32">
            <label htmlFor="plot-search" className="sr-only">
              Search farms and plots
            </label>
            <Search aria-hidden className="pointer-events-none absolute start-2.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <input
              id="plot-search"
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search"
              autoComplete="off"
              className="h-8 w-full rounded-lg border border-input bg-card ps-8 pe-2 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            />
          </div>
        </div>
      )}
      {groups.length === 0 && <p className="mt-6 text-lg">There are no farms yet. Use Add to create your first farm.</p>}
      <p aria-live="polite" className={q && shown.length === 0 ? "mt-3 text-base text-muted-foreground" : ""}>
        {q && shown.length === 0 ? `Nothing matches "${query.trim()}".` : ""}
      </p>
      <div className="mt-4 space-y-6">
        {shown.map((group) => (
          <section key={group.id} aria-labelledby={`farm-${group.id}`} className="rounded-3xl bg-secondary/60 p-4 ring-1 ring-foreground/10">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <h2 id={`farm-${group.id}`} className="text-2xl font-bold break-words">
                  {group.name}
                </h2>
                <p className="text-base text-muted-foreground">{group.summary}</p>
              </div>
              {group.actions}
            </div>
            {group.plots.length === 0 ? (
              <p className="mt-2 text-lg text-muted-foreground">{group.emptyNote}</p>
            ) : (
              <ul className="mt-4 grid items-start gap-3 sm:grid-cols-2 xl:grid-cols-4">
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
