import type { Metadata } from "next";
import { Atkinson_Hyperlegible } from "next/font/google";
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
        <header className="mx-auto flex w-full max-w-7xl items-center px-4 pt-5">
          <Link href="/" className="text-lg font-bold underline-offset-4 hover:underline focus-visible:underline">
            AgroPilot
          </Link>
        </header>
        <div className="mx-auto w-full max-w-7xl flex-1 px-4 py-6">{children}</div>
        <footer className="mx-auto w-full max-w-7xl px-4 pb-6">
          <Suspense fallback={<p className="text-sm text-muted-foreground">Checking services.</p>}>
            <ServiceStatusLine />
          </Suspense>
        </footer>
      </body>
    </html>
  );
}
