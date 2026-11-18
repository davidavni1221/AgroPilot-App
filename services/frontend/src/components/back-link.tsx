import Link from "next/link";

export function BackLink({ href = "/admin", children = "Back to admin" }: { href?: string; children?: React.ReactNode }) {
  return (
    <Link href={href} className="text-base font-bold underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring">
      {children}
    </Link>
  );
}
