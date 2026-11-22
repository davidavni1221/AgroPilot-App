"use client";

import { Trash2 } from "lucide-react";
import { useActionState, useEffect, useState } from "react";
import { FormError } from "@/components/forms/form-parts";
import { iconButton } from "@/components/forms/icon-button";
import { Modal } from "@/components/modal";
import { Button } from "@/components/ui/button";
import { emptyForm, type FormState } from "@/lib/form";

type Props = {
  action: (previous: FormState, formData: FormData) => Promise<FormState>;
  fields: Record<string, string>; // sent with the form, for example { id, farm_id }
  label: string; // the button's name for screen readers: "Delete North block"
  title: string; // the window's title: "Delete this plot?"
  question: string; // "Delete North block? This cannot be undone."
};

/** A trash button. It opens a window that asks first, so a slip of the finger does not delete anything. */
export function DeleteButton({ action, fields, label, title, question }: Props) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button type="button" onClick={() => setOpen(true)} aria-label={label} title={label} className={`${iconButton} text-destructive`}>
        <Trash2 aria-hidden className="size-5" />
      </button>
      {open && (
        <Modal title={title} onClose={() => setOpen(false)}>
          <Confirm action={action} fields={fields} question={question} onClose={() => setOpen(false)} />
        </Modal>
      )}
    </>
  );
}

function Confirm({ action, fields, question, onClose }: Pick<Props, "action" | "fields" | "question"> & { onClose: () => void }) {
  const [state, formAction, pending] = useActionState(action, emptyForm);
  useEffect(() => {
    if (state.done) onClose();
  }, [state, onClose]);
  return (
    <form action={formAction} className="space-y-4">
      {Object.entries(fields).map(([name, value]) => (
        <input key={name} type="hidden" name={name} value={value} />
      ))}
      <p className="text-base font-bold">{question}</p>
      <div className="flex flex-wrap gap-2">
        <Button type="submit" variant="destructive" disabled={pending} className="h-11 rounded-xl px-5 text-base font-bold">
          <Trash2 aria-hidden className="size-4" />
          {pending ? "Deleting..." : "Yes, delete"}
        </Button>
        <Button type="button" variant="outline" onClick={onClose} className="h-11 rounded-xl px-5 text-base font-bold">
          Cancel
        </Button>
      </div>
      <FormError message={state.error} />
    </form>
  );
}
