"use client";

import { useActionState } from "react";
import { addCrop } from "@/app/actions";
import { Field, FormError, inputClass, SubmitButton } from "@/components/forms/form-parts";
import { Input } from "@/components/ui/input";
import { emptyForm } from "@/lib/form";

const NUMBERS = [
  { id: "kc_ini", label: "Kc at the start", hint: "FAO-56 Table 12, Kc ini. Usually 0.1 to 1.", step: "0.01" },
  { id: "kc_mid", label: "Kc in the middle", hint: "Table 12, Kc mid.", step: "0.01" },
  { id: "kc_end", label: "Kc at the end", hint: "Table 12, Kc end.", step: "0.01" },
  { id: "l_ini", label: "Start stage, days", hint: "Table 11, L ini.", step: "1" },
  { id: "l_dev", label: "Growth stage, days", hint: "Table 11, L dev.", step: "1" },
  { id: "l_mid", label: "Middle stage, days", hint: "Table 11, L mid.", step: "1" },
  { id: "l_late", label: "Late stage, days", hint: "Table 11, L late.", step: "1" },
  { id: "root_depth_m", label: "Root depth, metres", hint: "Table 22. For scheduling, take the small end of the range.", step: "0.01" },
];

export function CropForm() {
  const [state, action] = useActionState(addCrop, emptyForm);
  return (
    <form action={action} className="space-y-5">
      <Field id="name" label="Crop name">
        <Input id="name" name="name" required maxLength={100} defaultValue={state.values.name} className={inputClass} />
      </Field>
      <fieldset className="space-y-5 rounded-xl bg-card p-4">
        <legend className="px-1 text-lg font-bold">Numbers for a new crop</legend>
        <p className="text-base text-muted-foreground">
          Only for a crop we do not know yet. For Tomato and Bell pepper we already have the numbers, so anything typed here is
          ignored.
        </p>
        {NUMBERS.map((n) => (
          <Field key={n.id} id={n.id} label={n.label} hint={n.hint}>
            <Input
              id={n.id}
              name={n.id}
              type="number"
              inputMode="decimal"
              step={n.step}
              min="0"
              defaultValue={state.values[n.id]}
              aria-describedby={`${n.id}-hint`}
              className={inputClass}
            />
          </Field>
        ))}
      </fieldset>
      <FormError message={state.error} />
      <SubmitButton>Add crop</SubmitButton>
    </form>
  );
}
