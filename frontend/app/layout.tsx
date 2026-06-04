import type { Metadata, Viewport } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "The Giver — Information Integrity",
  description: "Cross-source corroboration and framing analysis for pasted news text.",
  manifest: "/manifest.webmanifest",
  applicationName: "The Giver",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "The Giver",
  },
  icons: {
    icon: "/icon.svg",
    apple: "/icon.svg",
  },
};

export const viewport: Viewport = {
  themeColor: "#2563eb",
  width: "device-width",
  initialScale: 1,
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
                  News Feed
                </Link>
                <Link
                  href="/check"
                  className="text-giver-slate hover:text-giver-accent transition-colors"
                >
                  Check
                </Link>
                <Link
                  href="/dashboard"
                  className="text-giver-slate hover:text-giver-accent transition-colors"
                >
                  Dashboard
                </Link>
                <Link
                  href="/creators"
                  className="text-giver-slate hover:text-giver-accent transition-colors"
                >
                  Creators
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
