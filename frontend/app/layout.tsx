import type { Metadata } from "next";
import Link from "next/link";
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
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-xl font-semibold text-giver-ink">The Giver</h1>
                <p className="text-sm text-giver-slate">Information integrity</p>
              </div>
              <nav className="flex gap-4 text-sm font-medium">
                <Link
                  href="/"
                  className="text-giver-slate hover:text-giver-accent transition-colors"
                >
                  Core Checker
                </Link>
                <Link
                  href="/dashboard"
                  className="text-giver-slate hover:text-giver-accent transition-colors"
                >
                  Dashboard
                </Link>
              </nav>
            </div>
          </div>
        </header>
        <main className="mx-auto max-w-4xl px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
