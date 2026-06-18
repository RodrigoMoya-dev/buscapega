import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import NavGreeting from "@/components/NavGreeting";
import NavLinks from "@/components/NavLinks";

export const metadata: Metadata = {
  title: "Wunen — Automatización de búsqueda laboral",
  description: "Sistema personal de automatización de búsqueda de empleo",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="bg-gray-950 text-gray-100 min-h-screen">
        <nav className="border-b border-gray-800 bg-gray-950 sticky top-0 z-10">
          <div className="max-w-5xl mx-auto px-4 flex gap-1 h-12 items-center">
            <Link href="/" className="text-blue-400 font-bold text-lg mr-4 hover:text-blue-300 transition-colors">Wunen</Link>
            <NavLinks />
            <div className="ml-auto">
              <NavGreeting />
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
