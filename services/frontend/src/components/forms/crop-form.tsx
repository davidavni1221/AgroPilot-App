"use client";

import { useActionState } from "react";
import { addCrop } from "@/app/actions";
import { Field, FormError, inputClass, SubmitButton } from "@/components/forms/form-parts";
import { Input } from "@/components/ui/input";
import { emptyForm } from "@/lib/form";

const NUMBERS = [
  { id: "kc_ini", example: "0.6", label: "Kc at the start", hint: "FAO-56 Table 12, Kc ini. Usually 0.1 to 1.", step: "0.01" },
  { id: "kc_mid", example: "1.0", label: "Kc in the middle", hint: "Table 12, Kc mid.", step: "0.01" },
  { id: "kc_end", example: "0.75", label: "Kc at the end", hint: "Table 12, Kc end.", step: "0.01" },
  { id: "l_ini", example: "20", label: "Start stage, days", hint: "Table 11, L ini.", step: "1" },
  { id: "l_dev", example: "30", label: "Growth stage, days", hint: "Table 11, L dev.", step: "1" },
  { id: "l_mid", example: "40", label: "Middle stage, days", hint: "Table 11, L mid.", step: "1" },
  { id: "l_late", example: "15", label: "Late stage, days", hint: "Table 11, L late.", step: "1" },
  { id: "root_depth_m", example: "0.7", label: "Root depth, metres", hint: "Table 22. For scheduling, take the small end of the range.", step: "0.01" },
];

export function CropForm() {
  const [state, action] = useActionState(addCrop, emptyForm);
  return (
    <form action={action} className="space-y-5">
      <Field id="name" label="Crop name">
        <Input id="name" name="name" placeholder="e.g. Cucumber" required maxLength={100} defaultValue={state.values.name} className={inputClass} />
      </Field>
      <section aria-labelledby="crop-numbers" className="space-y-5 rounded-xl bg-card p-4">
        <h2 id="crop-numbers" className="text-lg font-bold">
          Numbers for a new crop
        </h2>
        <p className="text-base text-muted-foreground">
          Only for a crop we do not know yet. The grey examples are for Cucumber (FAO-56, fresh market). For Tomato and Bell pepper we already have the numbers, so anything typed here is
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
              placeholder={`e.g. ${n.example}`}
              min="0"
              defaultValue={state.values[n.id]}
              aria-describedby={`${n.id}-hint`}
              className={inputClass}
            />
          </Field>
        ))}
      </section>
      <FormError message={state.error} />
      <SubmitButton>Add crop</SubmitButton>
    </form>
  );
}
