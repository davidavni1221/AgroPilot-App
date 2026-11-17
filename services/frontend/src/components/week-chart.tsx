"use client";

import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";
import { type ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import type { PlanDay } from "@/lib/types";

const config = { minutes: { label: "Watering (minutes)", color: "var(--water)" } } satisfies ChartConfig;

const weekday = new Intl.DateTimeFormat("en-GB", { weekday: "short", timeZone: "UTC" });

/** Minutes of watering for each of the seven days. The table below has the same numbers. */
export function WeekChart({ days }: { days: PlanDay[] }) {
  const data = days.map((day, index) => ({
    day: index === 0 ? "Today" : weekday.format(new Date(`${day.date}T00:00:00Z`)),
    minutes: Math.round(day.run_minutes),
  }));
  return (
    <ChartContainer config={config} className="aspect-auto h-44 w-full" role="img" aria-label="Minutes of watering for each of the next 7 days">
      <BarChart data={data} margin={{ top: 8, right: 4, bottom: 0, left: 0 }}>
        <CartesianGrid vertical={false} />
        <XAxis dataKey="day" tickLine={false} axisLine={false} interval={0} />
        <YAxis width={32} tickLine={false} axisLine={false} />
        <ChartTooltip content={<ChartTooltipContent />} />
        <Bar dataKey="minutes" fill="var(--color-minutes)" radius={4} />
      </BarChart>
    </ChartContainer>
  );
}
