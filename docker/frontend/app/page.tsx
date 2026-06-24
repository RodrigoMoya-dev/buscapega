"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import { Offer, Stats, getOffers, getStats, triggerScraping, getPortals } from "@/lib/api";
import OfferCard from "@/components/OfferCard";

const AUTO_APPLY_PORTALS = new Set([
  "Tecnoempleo", "Chumi-IT", "ChileTrabajos", "RemoteLatinos",
  "GetOnBrd", "Torre.ai", "InfoJobs",
]);


export default function Home() {
  const [offers, setOffers] = useState<Offer[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [scrapeStatus, setScrapeStatus] = useState<string | null>(null);
  const [tab, setTab] = useState<"PENDIENTE" | "ENVIADA" | "DESCARTADA">("PENDIENTE");
  const [onlyAutoApply, setOnlyAutoApply] = useState(false);
  const [selectedTechs, setSelectedTechs] = useState<Set<string>>(new Set());

  function toggleTech(tech: string) {
    setSelectedTechs((prev) => {
      const next = new Set(prev);
      next.has(tech) ? next.delete(tech) : next.add(tech);
      return next;
    });
  }

  const load = useCallback(async () => {
    setLoading(true);
    const [data, statsData] = await Promise.all([getOffers(tab), getStats()]);
    setOffers(data);
    setStats(statsData);
    setLoading(false);
  }, [tab]);

  useEffect(() => {
    load();
    const interval = setInterval(load, 30000);
    return () => clearInterval(interval);
  }, [load]);

  async function handleScrape() {
    setScraping(true);
    setScrapeStatus(null);

    // Lista de portales para mostrar el progreso de la búsqueda.
    let portalNames: string[] = [];
    try {
      const portals = await getPortals();
      portalNames = portals.map((p) => p.name);
    } catch {
      /* sin lista: se muestra un progreso genérico */
    }
    if (portalNames.length === 0) portalNames = ["los portales configurados"];

    // Dispara el scraping real (corre en segundo plano en el backend).
    const scrape = triggerScraping().catch(() => {});

    // Anima el progreso portal por portal mientras el backend trabaja.
    for (const name of portalNames) {
      setScrapeStatus(name);
      await new Promise((r) => setTimeout(r, 1100));
    }

    setScrapeStatus(null); // fase "Finalizando…"
    await scrape;
    await new Promise((r) => setTimeout(r, 700));

    setScraping(false);
    setScrapeStatus(null);
    await load();
  }

  const availableTechs = useMemo(() => {
    const counts: Record<string, number> = {};
    offers.forEach((o) => {
      const techs: string[] = o.technologies ? JSON.parse(o.technologies) : [];
      techs.forEach((t) => { counts[t] = (counts[t] ?? 0) + 1; });
    });
    return Object.keys(counts).sort((a, b) => counts[b] - counts[a]);
  }, [offers]);

  const visibleOffers = offers.filter((o) => {
    if (onlyAutoApply && !AUTO_APPLY_PORTALS.has(o.portal)) return false;
    if (selectedTechs.size > 0) {
      const offerTechs: string[] = o.technologies ? JSON.parse(o.technologies) : [];
      const offerTechsLower = offerTechs.map((t) => t.toLowerCase());
      const matches = [...selectedTechs].some((sel) =>
        offerTechsLower.some((t) => t.includes(sel.toLowerCase()))
      );
      if (!matches) return false;
    }
    return true;
  });

  const tabs: Array<{ key: "PENDIENTE" | "ENVIADA" | "DESCARTADA"; label: string }> = [
    { key: "PENDIENTE", label: "Pendientes" },
    { key: "ENVIADA", label: "Enviadas" },
    { key: "DESCARTADA", label: "Descartadas" },
  ];

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Diálogo de progreso de búsqueda de ofertas */}
      {scraping && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
          <div className="bg-gray-900 border border-gray-700 rounded-2xl px-10 py-8 mx-4 w-full max-w-sm flex flex-col items-center gap-5 shadow-2xl">
            {/* Spinner flat */}
            <div className="w-12 h-12 rounded-full border-4 border-gray-700 border-t-blue-500 animate-spin" />
            <p className="text-white font-semibold text-lg">Cargando…</p>
            <p className="text-blue-300 text-sm text-center min-h-[1.25rem]">
              {scrapeStatus ? (
                <>Buscando en <span className="font-semibold text-white">{scrapeStatus}</span>…</>
              ) : (
                "Finalizando…"
              )}
            </p>
          </div>
        </div>
      )}

      {/* Stats banner */}
      {stats && (
        <div className="mb-6 p-4 bg-blue-950 border border-blue-800 rounded-xl text-sm text-blue-200">
          Ya se ha postulado a un total de{" "}
          <span className="font-bold text-white">{stats.sent_this_week}</span>{" "}
          oferta{stats.sent_this_week !== 1 ? "s" : ""} laborale{stats.sent_this_week !== 1 ? "s" : ""} durante esta semana
          {stats.total_sent > 0 && (
            <span className="text-blue-400">
              {" "}· {stats.total_sent} total en total
            </span>
          )}
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Ofertas</h1>
          <p className="text-gray-400 text-sm mt-1">Bandeja de propuestas de trabajo</p>
        </div>
        <button
          onClick={handleScrape}
          disabled={scraping}
          className="bg-blue-600 hover:bg-blue-500 disabled:bg-blue-900 disabled:text-blue-600 text-white font-semibold px-4 py-2 rounded-lg transition-colors text-sm"
        >
          {scraping ? "Buscando..." : "Buscar ofertas"}
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-4 bg-gray-900 rounded-lg p-1 w-fit">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              tab === t.key
                ? "bg-gray-700 text-white"
                : "text-gray-400 hover:text-gray-200"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Filtros */}
      <div className="flex flex-col gap-3 mb-6 p-4 bg-gray-900 rounded-xl border border-gray-800">
        {/* Autopostulación */}
        <button
          onClick={() => setOnlyAutoApply((v) => !v)}
          className={`flex items-center gap-2 w-fit px-3 py-1.5 rounded-lg text-sm font-medium transition-colors border ${
            onlyAutoApply
              ? "bg-blue-700 border-blue-600 text-white"
              : "border-gray-700 text-gray-400 hover:text-gray-200"
          }`}
        >
          <span className={`w-4 h-4 rounded border flex items-center justify-center text-xs ${
            onlyAutoApply ? "bg-blue-500 border-blue-400" : "border-gray-500"
          }`}>
            {onlyAutoApply && "✓"}
          </span>
          Solo autopostulación
        </button>

        {/* Tecnologías */}
        <div>
          <p className="text-gray-500 text-xs mb-2 uppercase tracking-wide">Tecnología</p>
          <div className="flex flex-wrap gap-2">
            {availableTechs.map((tech) => {
              const active = selectedTechs.has(tech);
              return (
                <button
                  key={tech}
                  onClick={() => toggleTech(tech)}
                  className={`px-3 py-1 rounded-full text-xs font-medium transition-colors border ${
                    active
                      ? "bg-indigo-700 border-indigo-500 text-white"
                      : "border-gray-700 text-gray-400 hover:border-gray-500 hover:text-gray-200"
                  }`}
                >
                  {tech}
                </button>
              );
            })}
            {selectedTechs.size > 0 && (
              <button
                onClick={() => setSelectedTechs(new Set())}
                className="px-3 py-1 rounded-full text-xs font-medium text-gray-500 hover:text-gray-300 transition-colors"
              >
                Limpiar
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="text-center py-20 text-gray-500">Cargando ofertas...</div>
      ) : visibleOffers.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-gray-500 text-lg">
            {onlyAutoApply || selectedTechs.size > 0
              ? "Ninguna oferta coincide con los filtros aplicados"
              : `No hay ofertas ${tab.toLowerCase()}s`}
          </p>
          {tab === "PENDIENTE" && !onlyAutoApply && selectedTechs.size === 0 && (
            <p className="text-gray-600 text-sm mt-2">
              Presiona "Buscar ofertas" para traer nuevas propuestas
            </p>
          )}
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          <p className="text-gray-500 text-sm">
            {visibleOffers.length} oferta{visibleOffers.length !== 1 ? "s" : ""}
            {(onlyAutoApply || selectedTechs.size > 0) && ` (de ${offers.length} total)`}
          </p>
          {visibleOffers.map((offer) => (
            <OfferCard key={offer.id} offer={offer} onAction={load} />
          ))}
        </div>
      )}
    </div>
  );
}
