import { ChevronRight, MapPin, Sprout, Tractor } from "lucide-react";
import Link from "next/link";

const actions = [
  { href: "/farms/new", title: "Add a farm", text: "Just a name.", Icon: Tractor, main: false },
  { href: "/crops/new", title: "Add a crop", text: "Only when ours is not in the list.", Icon: Sprout, main: false },
  { href: "/plots/new", title: "Add a plot", text: "Pick the crop and soil, find the place.", Icon: MapPin, main: true },
];

/** The ways to add things, on the admin page. */
export function AddActions() {
  return (
    <section aria-labelledby="add" className="mt-8">
      <h2 id="add" className="text-2xl font-bold">
        Add
      </h2>
      <p className="mt-1 text-base text-muted-foreground">Start with a farm, then add its plots.</p>
      <ul className="mt-4 grid gap-3 sm:grid-cols-3">
        {actions.map(({ href, title, text, Icon, main }) => (
          <li key={href}>
            <Link
              href={href}
              className={`group flex h-full items-center gap-3 rounded-2xl p-4 ring-1 transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring sm:flex-col sm:items-start ${
                main
                  ? "bg-primary text-primary-foreground ring-primary hover:bg-primary/90"
                  : "bg-card ring-foreground/10 hover:bg-secondary"
              }`}
            >
              <span
                aria-hidden
                className={`flex size-11 shrink-0 items-center justify-center rounded-full ${
                  main ? "bg-primary-foreground/20" : "bg-secondary group-hover:bg-card"
                }`}
              >
                <Icon className="size-6" />
              </span>
              <span className="flex-1">
                <span className="block text-lg font-bold">{title}</span>
                <span className={`block text-base ${main ? "text-primary-foreground/90" : "text-muted-foreground"}`}>{text}</span>
              </span>
              <ChevronRight aria-hidden className="size-5 shrink-0 transition-transform group-hover:translate-x-0.5 sm:hidden" />
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
