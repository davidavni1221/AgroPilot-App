import Link from "next/link";

export default function NotFound() {
  return (
    <main>
      <h1 className="text-3xl font-bold">We cannot find that page</h1>
      <p className="mt-3 text-lg">
        The plot may have been removed. <Link className="underline" href="/">Go to your fields</Link>.
      </p>
    </main>
  );
}
