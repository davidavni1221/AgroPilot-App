"use client";

import { useActionState } from "react";
import Link from "next/link";
import { addPlot } from "@/app/actions";
import { Field, FormError, inputClass, selectClass, SubmitButton } from "@/components/forms/form-parts";
import { PlacePicker } from "@/components/forms/place-picker";
import { Input } from "@/components/ui/input";
import { emptyForm } from "@/lib/form";
import { number } from "@/lib/format";
import type { Crop, Emitter, Farm, Soil } from "@/lib/types";

type Props = {
  farms: Farm[];
  crops: Crop[];
  soils: Soil[];
  emitters: Emitter[];
  defaults: { farm?: string; crop?: string };
};

export function PlotForm({ farms, crops, soils, emitters, defaults }: Props) {
  const [state, action] = useActionState(addPlot, emptyForm);
  const v = state.values;
  return (
    <form action={action} className="space-y-5">
      <Field id="farm_id" label="Farm">
        <select id="farm_id" name="farm_id" required defaultValue={v.farm_id ?? defaults.farm ?? ""} className={selectClass}>
          <option value="" disabled>
            Choose a farm
          </option>
          {farms.map((farm) => (
            <option key={farm.id} value={farm.id}>
              {farm.name}
            </option>
          ))}
        </select>
      </Field>
      <Field id="name" label="Plot name" hint="Unique on its farm, for example North block.">
        <Input id="name" name="name" required maxLength={100} defaultValue={v.name} aria-describedby="name-hint" className={inputClass} />
      </Field>
      <Field id="crop_id" label="Crop">
        <select id="crop_id" name="crop_id" required defaultValue={v.crop_id ?? defaults.crop ?? ""} className={selectClass}>
          <option value="" disabled>
            Choose a crop
          </option>
          {crops.map((crop) => (
            <option key={crop.id} value={crop.id}>
              {crop.name}
            </option>
          ))}
        </select>
        <p className="text-sm text-muted-foreground">
          Not in the list?{" "}
          <Link href="/crops/new" className="font-bold underline underline-offset-4">
            Add a crop
          </Link>
        </p>
      </Field>
      <Field id="planting_date" label="Planting date">
        <Input id="planting_date" name="planting_date" type="date" required defaultValue={v.planting_date} className={inputClass} />
      </Field>
      <PlacePicker
        initial={v.lat ? { label: v.place ?? "", lat: v.lat, lon: v.lon ?? "" } : undefined}
      />
      <Field id="area_m2" label="Area, square metres">
        <Input id="area_m2" name="area_m2" type="number" inputMode="decimal" step="any" min="0" required defaultValue={v.area_m2} className={inputClass} />
      </Field>
      <Field id="soil_id" label="Soil">
        <select id="soil_id" name="soil_id" required defaultValue={v.soil_id ?? ""} className={selectClass}>
          <option value="" disabled>
            Choose a soil
          </option>
          {soils.map((soil) => (
            <option key={soil.id} value={soil.id}>
              {soil.name} ({number(soil.available_water_mm_per_m, 0)} mm of water per metre)
            </option>
          ))}
        </select>
      </Field>
      <Field id="emitter_id" label="Emitter">
        <select id="emitter_id" name="emitter_id" required defaultValue={v.emitter_id ?? ""} className={selectClass}>
          <option value="" disabled>
            Choose an emitter
          </option>
          {emitters.map((emitter) => (
            <option key={emitter.id} value={emitter.id}>
              {emitter.name} ({number(emitter.flow_lph)} litres per hour)
            </option>
          ))}
        </select>
      </Field>
      <Field id="row_spacing_m" label="Row spacing, metres" hint="Distance between the drip lines.">
        <Input id="row_spacing_m" name="row_spacing_m" type="number" inputMode="decimal" step="any" min="0" required defaultValue={v.row_spacing_m} aria-describedby="row_spacing_m-hint" className={inputClass} />
      </Field>
      <Field id="emitter_spacing_m" label="Emitter spacing, metres" hint="Distance between emitters along a line.">
        <Input id="emitter_spacing_m" name="emitter_spacing_m" type="number" inputMode="decimal" step="any" min="0" required defaultValue={v.emitter_spacing_m} aria-describedby="emitter_spacing_m-hint" className={inputClass} />
      </Field>
      <FormError message={state.error} />
      <SubmitButton>Add plot</SubmitButton>
    </form>
  );
}
