import { WeekChart } from "@/components/week-chart";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { dayLabel, number, wholeMinutes } from "@/lib/format";
import type { Plan } from "@/lib/types";

/** The plan for the week: a chart of the watering, then one table row per day. */
export function DayList({ plan }: { plan: Plan }) {
  return (
    <section aria-labelledby={`week-${plan.plot_id}`}>
      <h2 id={`week-${plan.plot_id}`} className="text-2xl font-bold">
        The next 7 days
      </h2>
      <div className="mt-3 rounded-xl bg-card p-3">
        <p className="mb-2 text-sm text-muted-foreground">Minutes of watering each day</p>
        <WeekChart days={plan.days} />
      </div>
      <div className="mt-3 rounded-xl bg-card p-1">
        <Table aria-label="Plan for the next 7 days" className="text-sm">
          <TableHeader>
            <TableRow>
              <TableHead className="px-1.5">Day</TableHead>
              <TableHead className="px-1.5 text-end">Water</TableHead>
              <TableHead className="px-1.5 text-end leading-tight">
                Rain<span className="block text-xs font-normal text-muted-foreground">mm</span>
              </TableHead>
              <TableHead className="px-1.5 text-end leading-tight">
                Soil<span className="block text-xs font-normal text-muted-foreground">mm</span>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {plan.days.map((day, index) => {
              const waters = day.run_minutes > 0;
              return (
                <TableRow key={day.date}>
                  <TableCell className="px-1.5 font-bold whitespace-normal">
                    {dayLabel(day.date, index)}
                    {day.stale && <span className="block text-sm text-stale">Old forecast</span>}
                  </TableCell>
                  <TableCell className={`px-1.5 text-end font-bold ${waters ? "text-water" : "text-dry"}`}>
                    {waters ? `${wholeMinutes(day.run_minutes)} min` : "None"}
                    {waters && <span className="block text-sm font-normal text-muted-foreground">{number(day.litres, 0)} L</span>}
                  </TableCell>
                  <TableCell className="px-1.5 text-end">{day.rain_mm > 0 ? number(day.rain_mm) : "-"}</TableCell>
                  <TableCell className="px-1.5 text-end">{number(day.bucket_end_mm)}</TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
      <p className="mt-2 text-sm text-muted-foreground">
        Rain is the forecast total for the day. Soil is the estimated water in the soil at the end of the day, out of {number(plan.bucket_capacity_mm)} mm.
      </p>
    </section>
  );
}
