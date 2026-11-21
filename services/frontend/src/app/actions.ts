"use server";

import { revalidatePath } from "next/cache";
import { cropIdFromName, friendlyDetail } from "@/lib/crops";
import { type FormState, readValues, toNumber } from "@/lib/form";
import { type PlaceSearch, searchPlaces } from "@/lib/geocoding";
import { createCrop, createFarm, createPlot, deleteFarm, deletePlot, getCrops, getPlots, updateFarm, updatePlot } from "@/lib/registry";
import { describeFailure, type Failure } from "@/lib/services";
import type { PlotChanges } from "@/lib/types";

const sentence = (failure: Failure) => friendlyDetail(describeFailure(failure));

/** The saved change shows on the page, and the window that asked can close. */
function saved(extra: Partial<FormState> = {}): FormState {
  revalidatePath("/");
  return { values: {}, done: true, ...extra };
}

export async function addFarm(_previous: FormState, formData: FormData): Promise<FormState> {
  const values = readValues(formData);
  const name = (values.name ?? "").trim();
  if (!name) return { error: "Type the farm name.", values };

  const created = await createFarm(name);
  if (!created.ok) return { error: sentence(created), values };
  return saved({ done: false, created: { kind: "farm", id: created.data.id } });
}

const CROP_NUMBERS = ["kc_ini", "kc_mid", "kc_end", "l_ini", "l_dev", "l_mid", "l_late", "root_depth_m"] as const;

export async function addCrop(_previous: FormState, formData: FormData): Promise<FormState> {
  const values = readValues(formData);
  const name = (values.name ?? "").trim();
  const id = cropIdFromName(name);
  if (!id) return { error: "Type the crop name, with letters or digits (a-z, 0-9).", values };

  const known = await getCrops();
  if (!known.ok) return { error: sentence(known), values };
  // A crop we already hold (tomato, bell pepper) keeps its stored numbers. Whatever was typed is ignored.
  if (known.data.some((crop) => crop.id === id)) return saved({ done: false, created: { kind: "crop", id, known: true } });

  const numbers = Object.fromEntries(CROP_NUMBERS.map((key) => [key, toNumber(values[key])])) as Record<
    (typeof CROP_NUMBERS)[number],
    number
  >;
  if (CROP_NUMBERS.some((key) => Number.isNaN(numbers[key]))) {
    return { error: "This crop is new to us, so fill in all eight numbers.", values };
  }

  const created = await createCrop({ name, ...numbers });
  if (!created.ok) return { error: sentence(created), values };
  return saved({ done: false, created: { kind: "crop", id: created.data.id } });
}

/** The plot fields the form sends, checked. Add and edit use the same checks; the registry still has the last word. */
function readPlotFields(values: Record<string, string>): { error: string } | { fields: PlotChanges } {
  const name = (values.name ?? "").trim();
  if (!name) return { error: "Type the plot name." };
  for (const [key, label] of [["crop_id", "crop"], ["soil_id", "soil"], ["emitter_id", "emitter"]]) {
    if (!values[key]) return { error: `Choose the ${label}.` };
  }
  if (!values.planting_date) return { error: "Choose the planting date." };
  const lat = toNumber(values.lat);
  const lon = toNumber(values.lon);
  if (Number.isNaN(lat) || Number.isNaN(lon)) return { error: "Search for the place and pick it from the list." };
  const area = toNumber(values.area_m2);
  const row = toNumber(values.row_spacing_m);
  const emitter = toNumber(values.emitter_spacing_m);
  if ([area, row, emitter].some(Number.isNaN)) return { error: "Fill in the area and both spacings." };
  return {
    fields: {
      name,
      area_m2: area,
      crop_id: values.crop_id,
      planting_date: values.planting_date,
      soil_id: values.soil_id,
      row_spacing_m: row,
      emitter_spacing_m: emitter,
      emitter_id: values.emitter_id,
      lat,
      lon,
    },
  };
}

export async function addPlot(_previous: FormState, formData: FormData): Promise<FormState> {
  const values = readValues(formData);
  if (!values.farm_id) return { error: "Choose the farm.", values };
  const read = readPlotFields(values);
  if ("error" in read) return { error: read.error, values };

  const created = await createPlot({ farm_id: values.farm_id, ...read.fields });
  if (!created.ok) return { error: sentence(created), values };
  return saved();
}

export async function editPlot(_previous: FormState, formData: FormData): Promise<FormState> {
  const values = readValues(formData);
  const read = readPlotFields(values);
  if ("error" in read) return { error: read.error, values };

  const id = values.id ?? "";
  const changed = await updatePlot(id, read.fields);
  if (!changed.ok) return { error: sentence(changed), values };
  return saved();
}

export async function editFarm(_previous: FormState, formData: FormData): Promise<FormState> {
  const values = readValues(formData);
  const name = (values.name ?? "").trim();
  if (!name) return { error: "Type the farm name.", values };

  const changed = await updateFarm(values.id ?? "", name);
  if (!changed.ok) return { error: sentence(changed), values };
  return saved();
}

export async function findPlaces(query: string): Promise<PlaceSearch> {
  return searchPlaces(query);
}

// A 404 on delete means it is already gone, which is what the farmer wanted.
// A farm with no plots is deleted with its last plot. If that second step fails, the empty farm stays and has its own delete button.
export async function removePlot(_previous: FormState, formData: FormData): Promise<FormState> {
  const values = readValues(formData);
  const deleted = await deletePlot(values.id ?? "");
  if (!deleted.ok && deleted.kind !== "not-found") return { error: sentence(deleted), values };

  const farmId = values.farm_id;
  if (farmId) {
    const rest = await getPlots();
    if (rest.ok && !rest.data.some((plot) => plot.farm_id === farmId)) await deleteFarm(farmId);
  }
  return saved();
}

export async function removeFarm(_previous: FormState, formData: FormData): Promise<FormState> {
  const values = readValues(formData);
  const deleted = await deleteFarm(values.id ?? "");
  if (!deleted.ok && deleted.kind !== "not-found") return { error: sentence(deleted), values };
  return saved();
}
