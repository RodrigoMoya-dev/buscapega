"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS: { href: string; label: string }[] = [
  { href: "/", label: "Ofertas" },
  { href: "/validate", label: "Validar sitio" },
  { href: "/authenticate", label: "Portales" },
  { href: "/about", label: "Configura tu perfil" },
  { href: "/respuestas", label: "Auto respuestas" },
  { href: "/settings", label: "Configuración" },
];

export default function NavLinks() {
  const pathname = usePathname();

  return (
    <>
      {LINKS.map(({ href, label }) => {
        const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
        return (
          <Link
            key={href}
            href={href}
            prefetch
            className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
              active
                ? "text-white bg-gray-800"
                : "text-gray-400 hover:text-white hover:bg-gray-800"
            }`}
          >
            {label}
          </Link>
        );
      })}
    </>
  );
}
