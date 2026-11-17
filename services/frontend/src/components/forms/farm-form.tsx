"use client";

import { useActionState } from "react";
import { addFarm } from "@/app/actions";
import { Field, FormError, inputClass, SubmitButton } from "@/components/forms/form-parts";
import { Input } from "@/components/ui/input";
import { emptyForm } from "@/lib/form";

export function FarmForm() {
  const [state, action] = useActionState(addFarm, emptyForm);
  return (
    <form action={action} className="space-y-5">
      <Field id="name" label="Farm name">
        <Input id="name" name="name" required maxLength={100} defaultValue={state.values.name} className={inputClass} />
      </Field>
      <FormError message={state.error} />
      <SubmitButton>Add farm</SubmitButton>
    </form>
  );
}
