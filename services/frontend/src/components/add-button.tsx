"use client";

import { ChevronRight, MapPin, Plus, Sprout, Tractor } from "lucide-react";
import { useState } from "react";
import { CropForm } from "@/components/forms/crop-form";
import { FarmForm } from "@/components/forms/farm-form";
import { useLists } from "@/components/forms/lists";
import { PlotForm } from "@/components/forms/plot-form";
import { Modal } from "@/components/modal";
import { Button } from "@/components/ui/button";

// farm, crop and knownCrop only matter on the "plot" step: what was just added, to start the plot form with it chosen.
type Step = { name: "choose" | "farm" | "crop" | "plot"; farm?: string; crop?: string; knownCrop?: string };

const TITLES = { choose: "Add", farm: "Add a farm", crop: "Add a crop", plot: "Add a plot" } as const;

const choices = [
  { step: "plot", title: "Add a plot", text: "Pick the crop and soil, find the place.", Icon: MapPin, main: true },
  { step: "farm", title: "Add a farm", text: "Just a name.", Icon: Tractor, main: false },
  { step: "crop", title: "Add a crop", text: "Only when ours is not in the list.", Icon: Sprout, main: false },
] as const;

/**
 * The Add button and its window. The window first asks what to add. A new farm or a new crop goes straight on to the plot form
 * with it already chosen, because a farm or a crop is only useful with a plot.
 */
export function AddButton() {
  const [step, setStep] = useState<Step | null>(null); // null: the window is closed
  const lists = useLists();
  const close = () => setStep(null);

  return (
    <>
      <Button type="button" onClick={() => setStep({ name: "choose" })} className="h-10 w-32 rounded-lg px-3 text-base font-bold">
        <Plus aria-hidden className="size-5" />
        Add
      </Button>
      {step && (
        <Modal title={TITLES[step.name]} onClose={close}>
          {step.name === "choose" && (
            <ul className="space-y-3">
              {choices.map(({ step: next, title, text, Icon, main }) => (
                <li key={next}>
                  <button
                    type="button"
                    onClick={() => setStep({ name: next })}
                    className={`group flex w-full items-center gap-3 rounded-2xl p-4 text-start ring-1 transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring ${
                      main ? "bg-primary text-primary-foreground ring-primary hover:bg-primary/90" : "bg-card ring-foreground/10 hover:bg-secondary"
                    }`}
                  >
                    <Icon aria-hidden className="size-6 shrink-0" />
                    <span className="flex-1">
                      <span className="block text-lg font-bold">{title}</span>
                      <span className={`block text-base ${main ? "text-primary-foreground/90" : "text-muted-foreground"}`}>{text}</span>
                    </span>
                    <ChevronRight aria-hidden className="size-5 shrink-0" />
                  </button>
                </li>
              ))}
            </ul>
          )}
          {step.name === "farm" && (
            <FarmForm onCreated={(farm) => setStep({ name: "plot", farm })} />
          )}
          {step.name === "crop" && (
            <div className="space-y-5">
              <p className="text-lg">
                We already know: <span className="font-bold">{lists.crops.map((crop) => crop.name).join(", ")}</span>. You only add a crop that is not in
                this list.
              </p>
              <CropForm
                onCreated={(crop, known) =>
                  setStep({ name: "plot", crop, knownCrop: known ? lists.crops.find((c) => c.id === crop)?.name : undefined })
                }
              />
            </div>
          )}
          {step.name === "plot" &&
            (lists.farms.length === 0 ? (
              <p className="text-lg">
                A plot belongs to a farm.{" "}
                <button type="button" onClick={() => setStep({ name: "farm" })} className="font-bold underline underline-offset-4">
                  Add a farm first.
                </button>
              </p>
            ) : (
              <div className="space-y-5">
                {step.knownCrop && (
                  <p className="rounded-lg bg-card px-4 py-3 text-base font-bold">We already know {step.knownCrop}, so we use the numbers we have for it.</p>
                )}
                <PlotForm
                  // A farm or crop that was just added arrives with the refreshed lists; a new key makes the selects start from them.
                  key={`${step.farm}-${step.crop}-${lists.farms.length}-${lists.crops.length}`}
                  {...lists}
                  defaults={{ farm: step.farm, crop: step.crop }}
                  onDone={close}
                  onNeedCrop={() => setStep({ name: "crop" })}
                />
              </div>
            ))}
        </Modal>
      )}
    </>
  );
}
