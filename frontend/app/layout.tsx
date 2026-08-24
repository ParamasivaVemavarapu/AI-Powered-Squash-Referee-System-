import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "CourtSense | Squash Referee",
  description: "Explainable squash decision support and live scorekeeping.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
