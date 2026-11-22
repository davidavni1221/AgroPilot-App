/** The id the registry gives a crop: its name in lower case with dashes ("Bell pepper" becomes "bell-pepper").
 * Same rule as registry-service, so we can tell that a typed name is a crop it already knows. */
export function cropIdFromName(name: string): string {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
}

/** The registry names the field that failed ("kc_mid: Input should be..."). Say it the way the form does. */
const FIELD_LABELS: Record<string, string> = {
  name: "Name",
  kc_ini: "Kc at the start",
  kc_mid: "Kc in the middle",
  kc_end: "Kc at the end",
  l_ini: "Start stage days",
  l_dev: "Growth stage days",
  l_mid: "Middle stage days",
  l_late: "Late stage days",
  root_depth_m: "Root depth",
  area_m2: "Plot area",
  row_spacing_m: "Row spacing",
  emitter_spacing_m: "Emitter spacing",
  planting_date: "Planting date",
  lat: "Location",
  lon: "Location",
};

export function friendlyDetail(detail: string): string {
  return detail.replace(/\b([a-z_0-9]+):/g, (match, key: string) => (FIELD_LABELS[key] ? `${FIELD_LABELS[key]}:` : match));
}
