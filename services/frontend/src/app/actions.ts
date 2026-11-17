"use server";

import { redirect } from "next/navigation";
import { cropIdFromName, friendlyDetail } from "@/lib/crops";
import { type FormState, readValues, toNumber } from "@/lib/form";
import { type PlaceSearch, searchPlaces } from "@/lib/geocoding";
import { createCrop, createFarm, createPlot, getCrops } from "@/lib/registry";
import { describeFailure, type Failure } from "@/lib/services";

const sentence = (failure: Failure) => friendlyDetail(describeFailure(failure));

export async function addFarm(_previous: FormState, formData: FormData): Promise<FormState> {
  const values = readValues(formData);
  const name = (values.name ?? "").trim();
  if (!name) return { error: "Type the farm name.", values };

  const created = await createFarm(name);
  if (!created.ok) return { error: sentence(created), values };
  redirect(`/plots/new?farm=${encodeURIComponent(created.data.id)}`);
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
  if (known.data.some((crop) => crop.id === id)) redirect(`/plots/new?crop=${encodeURIComponent(id)}&known=1`);

  const numbers = Object.fromEntries(CROP_NUMBERS.map((key) => [key, toNumber(values[key])])) as Record<
    (typeof CROP_NUMBERS)[number],
    number
  >;
  if (CROP_NUMBERS.some((key) => Number.isNaN(numbers[key]))) {
    return { error: "This crop is new to us, so fill in all eight numbers.", values };
  }

  const created = await createCrop({ name, ...numbers });
  if (!created.ok) return { error: sentence(created), values };
  redirect(`/plots/new?crop=${encodeURIComponent(created.data.id)}`);
}

export async function addPlot(_previous: FormState, formData: FormData): Promise<FormState> {
  const values = readValues(formData);
  const name = (values.name ?? "").trim();
  if (!name) return { error: "Type the plot name.", values };
  for (const [key, label] of [["farm_id", "farm"], ["crop_id", "crop"], ["soil_id", "soil"], ["emitter_id", "emitter"]]) {
    if (!values[key]) return { error: `Choose the ${label}.`, values };
  }
  if (!values.planting_date) return { error: "Choose the planting date.", values };
  const lat = toNumber(values.lat);
  const lon = toNumber(values.lon);
  if (Number.isNaN(lat) || Number.isNaN(lon)) return { error: "Search for the place and pick it from the list.", values };
  const area = toNumber(values.area_m2);
  const row = toNumber(values.row_spacing_m);
  const emitter = toNumber(values.emitter_spacing_m);
  if ([area, row, emitter].some(Number.isNaN)) return { error: "Fill in the area and both spacings.", values };

  const created = await createPlot({
    farm_id: values.farm_id,
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
  });
  if (!created.ok) return { error: sentence(created), values };
  redirect(`/plots/${encodeURIComponent(created.data.id)}`);
}

export async function findPlaces(query: string): Promise<PlaceSearch> {
  return searchPlaces(query);
}
