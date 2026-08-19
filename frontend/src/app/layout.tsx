import type { Metadata } from "next";

import { Providers } from "./providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "Automated Report Generator",
  description: "Upload a CSV, let Claude decide what matters, download the PDF report.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">
        <div className="ambient-backdrop" aria-hidden="true" />
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
