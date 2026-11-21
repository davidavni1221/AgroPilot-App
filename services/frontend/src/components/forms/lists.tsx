"use client";

import { createContext, useContext } from "react";
import type { Crop, Emitter, Farm, Soil } from "@/lib/types";

export type Lists = { farms: Farm[]; crops: Crop[]; soils: Soil[]; emitters: Emitter[] };

const ListsContext = createContext<Lists | null>(null);

/** The farms, crops, soils and emitters, loaded once on the server, for every form in the windows on the page. */
export function ListsProvider({ lists, children }: { lists: Lists; children: React.ReactNode }) {
  return <ListsContext value={lists}>{children}</ListsContext>;
}

export function useLists(): Lists {
  const lists = useContext(ListsContext);
  if (!lists) throw new Error("useLists needs a ListsProvider above it.");
  return lists;
}
