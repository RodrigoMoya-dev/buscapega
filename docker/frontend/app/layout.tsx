import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Wunen — Bandeja de propuestas",
  description: "Revisión de ofertas de trabajo",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="bg-gray-950 text-gray-100 min-h-screen">
        <nav className="border-b border-gray-800 bg-gray-950 sticky top-0 z-10">
          <div className="max-w-4xl mx-auto px-4 flex gap-6 h-12 items-center">
            <a href="/" className="text-sm font-semibold text-white hover:text-blue-400 transition-colors">
              Ofertas
            </a>
            <a href="/respuestas" className="text-sm font-semibold text-gray-400 hover:text-white transition-colors">
              Respuestas automáticas
            </a>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
