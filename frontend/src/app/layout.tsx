import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { QueryProvider } from "@/components/QueryProvider";

export const metadata: Metadata = {
  title: "PricePilot — Your Smart Pricing Co-Pilot",
  description: "Know the right price — instantly, automatically and with confidence.",
  icons: { icon: "/favicon.ico" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <QueryProvider>
          <div className="flex h-screen overflow-hidden">
            <Sidebar />
            {/* pt-14 on mobile reserves space for the fixed top bar; md:pt-0 removes it on desktop */}
            <main className="flex-1 overflow-y-auto bg-gray-50 pt-14 md:pt-0">
              {children}
            </main>
          </div>
        </QueryProvider>
      </body>
    </html>
  );
}
