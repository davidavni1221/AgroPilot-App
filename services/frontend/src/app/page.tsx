import { Suspense } from "react";
import { FailureNotice } from "@/components/failure-notice";
import { FieldList } from "@/components/field-list";
import { AddButton } from "@/components/add-button";
import { ListsProvider } from "@/components/forms/lists";
import { getCrops, getEmitters, getFarms, getPlots, getSoils } from "@/lib/registry";

export default function Home() {
  return (
    <main>
      <Suspense
        fallback={
          <>
            <Title />
            <p className="mt-6 text-lg">Loading farms and plots.</p>
          </>
        }
      >
        <Farms />
      </Suspense>
    </main>
  );
}

/** The page title on the left, and on the right whatever goes with it (the Add button). */
function Title({ children }: { children?: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <h1 className="text-4xl font-bold tracking-tight">Your fields</h1>
      {children}
    </div>
  );
}

async function Farms() {
  const [farms, plots, crops, soils, emitters] = await Promise.all([getFarms(), getPlots(), getCrops(), getSoils(), getEmitters()]);
  if (!farms.ok) return <div><Title /><div className="mt-6"><FailureNotice title="The farms are not available" failure={farms} /></div></div>;
  if (!plots.ok) return <div><Title /><div className="mt-6"><FailureNotice title="The plots are not available" failure={plots} /></div></div>;
  if (!crops.ok) return <div><Title /><div className="mt-6"><FailureNotice title="The crops are not available" failure={crops} /></div></div>;
  if (!soils.ok) return <div><Title /><div className="mt-6"><FailureNotice title="The soils are not available" failure={soils} /></div></div>;
  if (!emitters.ok) return <div><Title /><div className="mt-6"><FailureNotice title="The emitters are not available" failure={emitters} /></div></div>;

  return (
    <ListsProvider lists={{ farms: farms.data, crops: crops.data, soils: soils.data, emitters: emitters.data }}>
      <Title>
        <AddButton />
      </Title>
      <FieldList farms={farms.data} plots={plots.data} />
    </ListsProvider>
  );
}
