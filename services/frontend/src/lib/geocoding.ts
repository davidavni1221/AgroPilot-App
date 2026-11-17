// Finds a place by name, so the farmer never types coordinates. Open-Meteo's free search, no key needed.
// Runs on the server only. The text the farmer types is sent to open-meteo.com.

export type Place = { label: string; lat: number; lon: number };

type SearchAnswer = {
  results?: { name: string; admin1?: string; country?: string; latitude: number; longitude: number }[];
};

export type PlaceSearch = { ok: true; places: Place[] } | { ok: false; message: string };

export async function searchPlaces(query: string): Promise<PlaceSearch> {
  const text = query.trim();
  if (text.length < 2) return { ok: false, message: "Type at least 2 letters of the place name." };

  const url = new URL("https://geocoding-api.open-meteo.com/v1/search");
  url.search = new URLSearchParams({ name: text, count: "5", language: "en", format: "json" }).toString();

  try {
    const response = await fetch(url, { cache: "no-store", signal: AbortSignal.timeout(5000) });
    if (!response.ok) throw new Error(`status ${response.status}`);
    const body = (await response.json()) as SearchAnswer;
    const places = (body.results ?? [])
      .filter((r) => Number.isFinite(r.latitude) && Number.isFinite(r.longitude))
      .map((r) => ({
        label: [r.name, r.admin1, r.country].filter(Boolean).join(", "),
        lat: r.latitude,
        lon: r.longitude,
      }));
    return { ok: true, places };
  } catch {
    return { ok: false, message: "The place search is not available. Try again in a minute." };
  }
}
