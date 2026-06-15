import type { Metadata } from "next";
import "./globals.css";
import NavGreeting from "@/components/NavGreeting";

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
            <a href="/" className="text-blue-400 font-bold text-lg mr-4 hover:text-blue-300 transition-colors">Wunen</a>
            <NavLink href="/">Ofertas</NavLink>
            <NavLink href="/validate">Validar sitio</NavLink>
            <NavLink href="/authenticate">Portales</NavLink>
            <NavLink href="/about">Configura tu perfil</NavLink>
            <NavLink href="/respuestas">Auto respuestas</NavLink>
            <NavLink href="/settings">Configuración</NavLink>
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

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <a
      href={href}
      className="px-3 py-1.5 text-sm text-gray-400 hover:text-white hover:bg-gray-800 rounded-md transition-colors"
    >
      {children}
    </a>
  );
}
