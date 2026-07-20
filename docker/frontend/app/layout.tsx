import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import "./globals.css";
import NavGreeting from "@/components/NavGreeting";
import NavLinks from "@/components/NavLinks";

export const metadata: Metadata = {
  title: "Buscapega — Automatización de búsqueda laboral",
  description: "Sistema personal de automatización de búsqueda de empleo",
  icons: {
    icon: "/favicon.ico",
    apple: "/apple-touch-icon.png",
  },
};

// Enlace directo a GitHub con el issue prellenado (sin token en el frontend).
const ISSUE_BODY = `## Descripción del problema
(describe qué ocurrió)

## Pasos para reproducir
1.
2.

## Resultado esperado vs. obtenido


---
_Reportado desde la interfaz web de Buscapega_`;

const REPORT_ISSUE_URL =
  "https://github.com/RodrigoMoya-dev/buscapega/issues/new?title=" +
  encodeURIComponent("[Reporte] ") +
  "&body=" +
  encodeURIComponent(ISSUE_BODY);

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="bg-gray-950 text-gray-100 min-h-screen">
        <nav className="border-b border-gray-800 bg-gray-950 sticky top-0 z-10">
          <div className="max-w-5xl mx-auto px-4 flex gap-1 h-12 items-center">
            <Link
              href="/"
              className="flex items-center gap-2 font-bold text-lg mr-4 text-marca-celadon hover:text-white transition-colors"
            >
              <Image
                src="/logo.png"
                alt=""
                width={28}
                height={28}
                priority
                className="w-7 h-7 shrink-0"
              />
              <span>Buscapega</span>
            </Link>
            <NavLinks />
            <div className="ml-auto flex items-center gap-4">
              <a
                href={REPORT_ISSUE_URL}
                target="_blank"
                rel="noopener noreferrer"
                title="Se abrirá una página de GitHub para describir y subir el problema"
                className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-white transition-colors"
              >
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="w-4 h-4 shrink-0"
                  aria-hidden="true"
                >
                  <path d="M12 9v4M12 17h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z" />
                </svg>
                <span className="hidden sm:inline">Reportar problema</span>
              </a>
              <NavGreeting />
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
