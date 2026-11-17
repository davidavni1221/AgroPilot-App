"use client";

import { useState } from "react";
import { findPlaces } from "@/app/actions";
import { Field, inputClass } from "@/components/forms/form-parts";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { Place } from "@/lib/geocoding";

/** The farmer types a place name and picks a match. The coordinates travel in two hidden fields. */
export function PlacePicker({ initial }: { initial?: { label: string; lat: string; lon: string } }) {
  const [query, setQuery] = useState(initial?.label ?? "");
  const [results, setResults] = useState<Place[]>([]);
  const [message, setMessage] = useState("");
  const [chosen, setChosen] = useState<{ label: string; lat: string; lon: string } | undefined>(
    initial?.lat ? initial : undefined,
  );
  const [searching, setSearching] = useState(false);

  async function search() {
    setSearching(true);
    setMessage("");
    const answer = await findPlaces(query);
    setSearching(false);
    if (!answer.ok) {
      setResults([]);
      setMessage(answer.message);
    } else {
      setResults(answer.places);
      setMessage(answer.places.length === 0 ? "No place found. Try another spelling." : "");
    }
  }

  return (
    <div className="space-y-3">
      <Field id="place" label="Where is the plot?" hint="Type a town or village, search, then pick the right one.">
        <div className="flex gap-2">
          <Input
            id="place"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                void search();
              }
            }}
            aria-describedby="place-hint"
            className={inputClass}
          />
          <Button type="button" variant="outline" onClick={search} disabled={searching} className="h-11 px-4 text-base">
            {searching ? "Searching..." : "Search"}
          </Button>
        </div>
      </Field>
      <p aria-live="polite" className="text-base font-bold text-destructive">
        {message}
      </p>
      {results.length > 0 && (
        <ul className="divide-y divide-border rounded-xl bg-card">
          {results.map((place) => (
            <li key={`${place.lat},${place.lon}`}>
              <button
                type="button"
                onClick={() => {
                  setChosen({ label: place.label, lat: String(place.lat), lon: String(place.lon) });
                  setQuery(place.label);
                  setResults([]);
                }}
                className="w-full px-4 py-3 text-start text-base hover:bg-secondary focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-ring"
              >
                {place.label}
              </button>
            </li>
          ))}
        </ul>
      )}
      {chosen && (
        <p className="text-base">
          Chosen: <span className="font-bold">{chosen.label}</span>
        </p>
      )}
      <input type="hidden" name="lat" value={chosen?.lat ?? ""} />
      <input type="hidden" name="lon" value={chosen?.lon ?? ""} />
      <input type="hidden" name="place" value={chosen?.label ?? ""} />
    </div>
  );
}
