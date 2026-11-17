"use client";

import { Trash2 } from "lucide-react";
import { useActionState, useState } from "react";
import { FormError } from "@/components/forms/form-parts";
import { Button } from "@/components/ui/button";
import { emptyForm, type FormState } from "@/lib/form";

type Props = {
  action: (previous: FormState, formData: FormData) => Promise<FormState>;
  id: string;
  label: string; // "Delete this plot"
  question: string; // "Delete North block? This cannot be undone."
};

/** Two steps, so a slip of the finger does not delete anything: the first button only asks. */
export function DeleteButton({ action, id, label, question }: Props) {
  const [state, formAction, pending] = useActionState(action, emptyForm);
  const [asking, setAsking] = useState(false);
  return (
    <form action={formAction} className="space-y-3">
      <input type="hidden" name="id" value={id} />
      {asking ? (
        <div className="space-y-3 rounded-xl bg-card p-4 ring-1 ring-destructive/40">
          <p role="alert" className="text-base font-bold">
            {question}
          </p>
          <div className="flex flex-wrap gap-2">
            <Button type="submit" variant="destructive" disabled={pending} className="h-11 rounded-xl px-5 text-base font-bold">
              <Trash2 aria-hidden className="size-4" />
              {pending ? "Deleting..." : "Yes, delete"}
            </Button>
            <Button type="button" variant="outline" onClick={() => setAsking(false)} className="h-11 rounded-xl px-5 text-base font-bold">
              Cancel
            </Button>
          </div>
        </div>
      ) : (
        <Button type="button" variant="outline" onClick={() => setAsking(true)} className="h-11 rounded-xl px-5 text-base font-bold text-destructive">
          <Trash2 aria-hidden className="size-4" />
          {label}
        </Button>
      )}
      <FormError message={state.error} />
    </form>
  );
}
