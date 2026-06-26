import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ActiveMap Reviewer — Дизайн-система",
  description: "Дизайн-система ActiveMap Reviewer — Префектура САО",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
