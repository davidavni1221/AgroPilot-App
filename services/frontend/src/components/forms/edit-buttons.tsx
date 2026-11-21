"use client";

import { Pencil } from "lucide-react";
import { useState } from "react";
import { removeFarm, removePlot } from "@/app/actions";
import { DeleteButton } from "@/components/forms/delete-button";
import { FarmForm } from "@/components/forms/farm-form";
import { iconButton } from "@/components/forms/icon-button";
import { useLists } from "@/components/forms/lists";
import { PlotForm } from "@/components/forms/plot-form";
import { Modal } from "@/components/modal";
import type { Farm, Plot } from "@/lib/types";

/** Beside a farm's name: change the name, and delete the farm when it has no plots left. */
export function FarmActions({ farm, empty }: { farm: Farm; empty: boolean }) {
  const [editing, setEditing] = useState(false);
  return (
    <div className="flex gap-2">
      <button type="button" onClick={() => setEditing(true)} aria-label={`Change the name of ${farm.name}`} title="Change the name" className={iconButton}>
        <Pencil aria-hidden className="size-5" />
      </button>
      {empty && (
        <DeleteButton
          action={removeFarm}
          fields={{ id: farm.id }}
          label={`Delete ${farm.name}`}
          title="Delete this farm?"
          question={`Delete ${farm.name}? It has no plots. This cannot be undone.`}
        />
      )}
      {editing && (
        <Modal title="Change the farm name" onClose={() => setEditing(false)}>
          <FarmForm farm={farm} onDone={() => setEditing(false)} />
        </Modal>
      )}
    </div>
  );
}

/** Beside a plot: change it, delete it. Deleting the last plot of a farm deletes the farm too, and the question says so. */
export function PlotActions({ plot, farmName, last }: { plot: Plot; farmName: string; last: boolean }) {
  const [editing, setEditing] = useState(false);
  const lists = useLists();
  return (
    <div className="flex gap-2">
      <button type="button" onClick={() => setEditing(true)} aria-label={`Change ${plot.name}`} title="Change this plot" className={iconButton}>
        <Pencil aria-hidden className="size-5" />
      </button>
      <DeleteButton
        action={removePlot}
        fields={{ id: plot.id, farm_id: plot.farm_id }}
        label={`Delete ${plot.name}`}
        title="Delete this plot?"
        question={`Delete ${plot.name}? This cannot be undone.${last ? ` It is the last plot on ${farmName}, so the farm is deleted too.` : ""}`}
      />
      {editing && (
        <Modal title="Change this plot" onClose={() => setEditing(false)}>
          <PlotForm {...lists} defaults={{}} plot={plot} onDone={() => setEditing(false)} />
        </Modal>
      )}
    </div>
  );
}
