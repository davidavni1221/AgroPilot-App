import { Suspense } from "react";
import { PlotView } from "@/components/plot-view";

export default function PlotPage({ params }: { params: Promise<{ id: string }> }) {
  return (
    <main>
      <Suspense fallback={<p className="text-lg">Working out today&apos;s plan. This can take a few seconds.</p>}>
        <PlotContent params={params} />
      </Suspense>
    </main>
  );
}

async function PlotContent({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <PlotView id={id} />;
}
