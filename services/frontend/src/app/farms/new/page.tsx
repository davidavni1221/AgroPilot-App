import type { Metadata } from "next";
import { BackLink } from "@/components/back-link";
import { FarmForm } from "@/components/forms/farm-form";

export const metadata: Metadata = { title: "Add farm | AgroPilot" };

export default function NewFarmPage() {
  return (
    <main className="space-y-6">
      <BackLink />
      <h1 className="text-4xl font-bold tracking-tight">Add a farm</h1>
      <FarmForm />
    </main>
  );
}
