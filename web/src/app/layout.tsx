import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AfriProp — Property Intelligence Platform",
  description: "Find, buy, rent and invest in African property with AI-powered insights",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 min-h-screen">
        {children}
      </body>
    </html>
  );
}
