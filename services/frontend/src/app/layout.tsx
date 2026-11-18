import type { Metadata } from "next";
import { Atkinson_Hyperlegible } from "next/font/google";
import { Settings } from "lucide-react";
import Link from "next/link";
import { Suspense } from "react";
import { ServiceStatusLine } from "@/components/service-status";
import "./globals.css";

// Made for reading in poor conditions, such as a phone in sunlight.
const atkinson = Atkinson_Hyperlegible({
  variable: "--font-atkinson",
  subsets: ["latin"],
  weight: ["400", "700"],
});

export const metadata: Metadata = {
  title: "AgroPilot",
  description: "Should I water this plot today, and for how long?",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${atkinson.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col font-sans text-base">
        <header className="mx-auto flex w-full max-w-2xl items-center justify-between px-4 pt-5">
          <Link href="/" className="text-lg font-bold underline-offset-4 hover:underline focus-visible:underline">
            AgroPilot
          </Link>
          <Link
            href="/admin"
            className="inline-flex h-10 items-center gap-2 rounded-xl px-3 text-base font-bold text-muted-foreground ring-1 ring-foreground/15 transition-colors hover:bg-secondary hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
          >
            <Settings aria-hidden className="size-4" />
            Admin
          </Link>
        </header>
        <div className="mx-auto w-full max-w-2xl flex-1 px-4 py-6">{children}</div>
        <footer className="mx-auto w-full max-w-2xl px-4 pb-6">
          <Suspense fallback={<p className="text-sm text-muted-foreground">Checking services.</p>}>
            <ServiceStatusLine />
          </Suspense>
        </footer>
      </body>
    </html>
  );
}
