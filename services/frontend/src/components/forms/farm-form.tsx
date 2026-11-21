"use client";

import { useActionState, useEffect } from "react";
import { addFarm, editFarm } from "@/app/actions";
import { Field, FormError, inputClass, SubmitButton } from "@/components/forms/form-parts";
import { Input } from "@/components/ui/input";
import { emptyForm } from "@/lib/form";

/** Without `farm` it adds a farm. With `farm` it changes that farm's name. */
export function FarmForm({
  farm,
  onDone,
  onCreated,
}: {
  farm?: { id: string; name: string };
  onDone?: () => void;
  onCreated?: (id: string) => void;
}) {
  const [state, action] = useActionState(farm ? editFarm : addFarm, emptyForm);
  useEffect(() => {
    if (state.done) onDone?.();
    if (state.created?.kind === "farm") onCreated?.(state.created.id);
  }, [state, onDone, onCreated]);
  return (
    <form action={action} className="space-y-5">
      {farm && <input type="hidden" name="id" value={farm.id} />}
      <Field id="name" label="Farm name">
        <Input id="name" name="name" required maxLength={100} defaultValue={state.values.name ?? farm?.name} className={inputClass} />
      </Field>
      <FormError message={state.error} />
      <SubmitButton>{farm ? "Save the name" : "Add farm"}</SubmitButton>
    </form>
  );
}
