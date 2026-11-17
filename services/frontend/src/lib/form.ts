/** What a form action hands back to its form: an error to show, and what the farmer typed so it is not lost. */
export type FormState = { error?: string; values: Record<string, string> };

export const emptyForm: FormState = { values: {} };

export function readValues(formData: FormData): Record<string, string> {
  const values: Record<string, string> = {};
  for (const [key, value] of formData.entries()) {
    if (typeof value === "string") values[key] = value;
  }
  return values;
}

/** A number from a text field. Empty or not a number gives NaN. */
export const toNumber = (text: string | undefined): number => (text?.trim() ? Number(text) : Number.NaN);
