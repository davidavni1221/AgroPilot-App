import { getServiceStatuses, serviceLabel } from "@/lib/services";

export async function ServiceStatusLine() {
  const statuses = await getServiceStatuses();
  return (
    <ul className="flex flex-wrap gap-x-5 gap-y-1 text-sm text-muted-foreground" aria-label="Service status">
      {statuses.map(({ service, up }) => (
        <li key={service} className="flex items-center gap-1.5">
          <span aria-hidden className={`size-2.5 rounded-full ${up ? "bg-dry" : "bg-destructive"}`} />
          <span>
            {serviceLabel[service]} {up ? "is up" : "is down"}
          </span>
        </li>
      ))}
    </ul>
  );
}
