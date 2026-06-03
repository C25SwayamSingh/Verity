import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "The Giver — Information Integrity",
  description: "Cross-source corroboration and framing analysis for pasted news text.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <header className="border-b border-slate-200 bg-white">
          <div className="mx-auto max-w-4xl px-4 py-4">
            <h1 className="text-xl font-semibold text-giver-ink">The Giver</h1>
            <p className="text-sm text-giver-slate">
              Information integrity — Phase 1 Core Checker
            </p>
          </div>
        </header>
        <main className="mx-auto max-w-4xl px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
