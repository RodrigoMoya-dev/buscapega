"use client";

import { useEffect, useState } from "react";
import { getSettings } from "@/lib/api";

export default function NavGreeting() {
  const [name, setName] = useState<string | null>(null);

  useEffect(() => {
    function refresh() {
      getSettings().then((s) => setName(s?.user_name || null));
    }
    refresh();
    // La vista de Configuración dispara este evento al guardar el nombre,
    // para refrescar el saludo sin recargar la página (T9).
    function onUpdate(e: Event) {
      const detail = (e as CustomEvent<{ user_name?: string }>).detail;
      if (detail && typeof detail.user_name === "string") setName(detail.user_name || null);
      else refresh();
    }
    window.addEventListener("buscapega:settings-updated", onUpdate);
    return () => window.removeEventListener("buscapega:settings-updated", onUpdate);
  }, []);

  if (!name) return null;

  return (
    <span className="text-sm text-gray-400">
      Hola, <span className="text-white font-medium">{name}</span>
    </span>
  );
}
