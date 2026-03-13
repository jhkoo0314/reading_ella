import type { Metadata } from "next";

import "./globals.css";


export const metadata: Metadata = {
  title: "Reading ELLA",
  description: "Reading ELLA frontend scaffold for the student learning flow.",
};


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
