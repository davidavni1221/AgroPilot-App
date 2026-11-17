import Link from "next/link";

export function BackLink() {
  return (
    <Link href="/" className="text-base font-bold underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring">
      Back to your fields
    </Link>
  );
}
