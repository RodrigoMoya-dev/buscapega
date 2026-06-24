"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

// Íconos flat (line icons) en SVG inline — sin dependencias externas.
const ICONS: Record<string, ReactNode> = {
  ofertas: (
    <path d="M3 7h18M3 7l1.5 12a2 2 0 0 0 2 1.7h11a2 2 0 0 0 2-1.7L21 7M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
  ),
  portales: (
    <>
      <rect x="3" y="3" width="7" height="7" rx="1" />
      <rect x="14" y="3" width="7" height="7" rx="1" />
      <rect x="3" y="14" width="7" height="7" rx="1" />
      <rect x="14" y="14" width="7" height="7" rx="1" />
    </>
  ),
  perfil: (
    <>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21a8 8 0 0 1 16 0" />
    </>
  ),
  config: (
    <>
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-1.8-.3 1.6 1.6 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.6 1.6 0 0 0-1-1.5 1.6 1.6 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.6 1.6 0 0 0 .3-1.8 1.6 1.6 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.6 1.6 0 0 0 1.5-1 1.6 1.6 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.6 1.6 0 0 0 1.8.3H9a1.6 1.6 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.6 1.6 0 0 0 1 1.5 1.6 1.6 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0-.3 1.8V9a1.6 1.6 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.6 1.6 0 0 0-1.5 1z" />
    </>
  ),
};

const LINKS: { href: string; label: string; icon: keyof typeof ICONS }[] = [
  { href: "/", label: "Ofertas", icon: "ofertas" },
  { href: "/authenticate", label: "Portales", icon: "portales" },
  { href: "/about", label: "Configura tu perfil", icon: "perfil" },
  { href: "/settings", label: "Configuración", icon: "config" },
];

export default function NavLinks() {
  const pathname = usePathname();

  return (
    <>
      {LINKS.map(({ href, label, icon }) => {
        const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
        return (
          <Link
            key={href}
            href={href}
            prefetch
            className={`flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-md transition-colors ${
              active
                ? "text-white bg-gray-800"
                : "text-gray-400 hover:text-white hover:bg-gray-800"
            }`}
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
              {ICONS[icon]}
            </svg>
            {label}
          </Link>
        );
      })}
    </>
  );
}
