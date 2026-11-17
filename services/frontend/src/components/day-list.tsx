import { WeekChart } from "@/components/week-chart";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { dayLabel, number, wholeMinutes } from "@/lib/format";
import type { Plan } from "@/lib/types";

/** The plan for the week: a chart of the watering, then one table row per day. */
export function DayList({ plan }: { plan: Plan }) {
  return (
    <section aria-labelledby="week">
      <h2 id="week" className="text-2xl font-bold">
        The next 7 days
      </h2>
      <div className="mt-3 rounded-xl bg-card p-3">
        <WeekChart days={plan.days} />
      </div>
      <div className="mt-3 rounded-xl bg-card p-1">
        <Table aria-label="Plan for the next 7 days" className="text-base">
          <TableHeader>
            <TableRow>
              <TableHead>Day</TableHead>
              <TableHead className="text-end">Water</TableHead>
              <TableHead className="text-end">Rain</TableHead>
              <TableHead className="text-end">Soil</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {plan.days.map((day, index) => {
              const waters = day.run_minutes > 0;
              return (
                <TableRow key={day.date}>
                  <TableCell className="font-bold">
                    {dayLabel(day.date, index)}
                    {day.stale && <span className="block text-sm text-stale">Old forecast</span>}
                  </TableCell>
                  <TableCell className={`text-end font-bold ${waters ? "text-water" : "text-dry"}`}>
                    {waters ? `${wholeMinutes(day.run_minutes)} min` : "None"}
                    {waters && <span className="block text-sm font-normal text-muted-foreground">{number(day.litres, 0)} L</span>}
                  </TableCell>
                  <TableCell className="text-end">{day.rain_mm > 0 ? `${number(day.rain_mm)} mm` : "-"}</TableCell>
                  <TableCell className="text-end">{number(day.bucket_end_mm)} mm</TableCell>
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
