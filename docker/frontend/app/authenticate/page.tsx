"use client";

import { useEffect, useState } from "react";
import { getPortals, Portal, validatePortal, togglePortal, addPortal } from "@/lib/api";

const GITHUB_REPO = "https://github.com/RodrigoMoya-dev/buscapega";

// ── Banderas por mercado ──────────────────────────────────────────────────────
const MARKET_FLAG: Record<string, { flag: string; country: string }> = {
  "Chile": { flag: "🇨🇱", country: "Chile" },
  "España": { flag: "🇪🇸", country: "España" },
  "Internacional": { flag: "🌍", country: "Internacional" },
  "LATAM/EEUU": { flag: "🌎", country: "LATAM / EE. UU." },
  "LATAM/España": { flag: "🌎", country: "LATAM / España" },
  "LATAM/Chile": { flag: "🌎", country: "LATAM / Chile" },
};

function marketInfo(market: string) {
  return MARKET_FLAG[market] || { flag: "🌐", country: market };
}

// Slug del portal para el comando de captura de sesión (coincide con session_key).
function portalSlug(name: string): string {
  return name.toLowerCase().replace(/[\s.\-]/g, "");
}

// ── Validación de URL (cliente) ───────────────────────────────────────────────
function normalizeUrl(url: string): string {
  const trimmed = url.trim();
  if (trimmed && !trimmed.startsWith("http://") && !trimmed.startsWith("https://")) {
    return "https://" + trimmed;
  }
  return trimmed;
}
const DOMAIN_RE = /^https?:\/\/([a-z0-9]([a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}(:\d+)?(\/.*)?$/i;

interface ValidationResult {
  url: string;
  allows_scraping: boolean;
  has_google_auth: boolean;
  automatable: boolean;
  notes: string[];
  already_configured?: boolean;
  error?: string;
}

export default function PortalesPage() {
  const [portals, setPortals] = useState<Portal[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  async function load() {
    setLoading(true);
    const data = await getPortals();
    setPortals(data);
    setLoading(false);
  }
  useEffect(() => { load(); }, []);

  // Filtro por nombre (buscador de la zona superior).
  const query = search.trim().toLowerCase();
  const filtered = query
    ? portals.filter((p) => p.name.toLowerCase().includes(query) || p.url.toLowerCase().includes(query))
    : portals;

  // Las tres categorías. "No permite scraping" usa el flag allows_scraping del backend.
  const autoApply = filtered.filter((p) => p.allows_scraping !== false && p.auto_apply);
  const reviewable = filtered.filter((p) => p.allows_scraping !== false && !p.auto_apply);
  const noScraping = filtered.filter((p) => p.allows_scraping === false);

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-white mb-2">Portales de empleo</h1>
      <p className="text-gray-400 text-sm mb-8">
        Valida un sitio nuevo y administra los portales registrados y su estado de sesión.
      </p>

      {/* ── Sección: Validar sitio (destacada) ── */}
      <ValidateSection onAdded={load} />

      {/* ── Buscador de portales (entre "Validar sitio" y "Portales de empleo") ── */}
      <div className="mt-6 relative">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"
          className="w-4 h-4 text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" aria-hidden="true">
          <circle cx="11" cy="11" r="7" /><path d="m21 21-4.3-4.3" />
        </svg>
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar un portal por nombre…"
          className="w-full bg-gray-950 border border-gray-700 text-white rounded-lg pl-9 pr-9 py-2.5 text-sm focus:outline-none focus:border-blue-500 placeholder-gray-600"
        />
        {search && (
          <button
            onClick={() => setSearch("")}
            aria-label="Limpiar búsqueda"
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white text-lg leading-none"
          >
            ×
          </button>
        )}
      </div>

      {/* ── Sección: Portales de empleo (otro color) ── */}
      <div className="bg-slate-900/60 border border-slate-700 rounded-2xl p-5 mt-4">
        <h2 className="text-lg font-semibold text-white mb-1">Portales de empleo</h2>
        <p className="text-gray-400 text-xs mb-5">
          Activa o desactiva portales y registra tu sesión en los que lo permitan.
        </p>

        {loading ? (
          <div className="text-center py-10 text-gray-500">Cargando portales...</div>
        ) : query && autoApply.length + reviewable.length + noScraping.length === 0 ? (
          <p className="text-gray-500 text-sm py-6 text-center">
            Ningún portal coincide con “{search}”.
          </p>
        ) : (
          <div className="flex flex-col gap-3">
            {/* key con `query` para que los acordeones se reabran al buscar y muestren resultados */}
            <Accordion key={`auto-${query}`} title="Portales con auto-postulación" count={autoApply.length} defaultOpen>
              {/* Por qué hace falta registrar la sesión: sin esto el botón "Registrar sesión
                  con Google" parece un trámite opcional y la gente lo salta. */}
              <div className="mb-3 px-3 py-2.5 bg-slate-800/60 border border-slate-600 rounded text-gray-300 text-xs leading-relaxed">
                <strong className="text-white">¿Por qué registrar tu sesión con Google?</strong>{" "}
                Estos portales solo muestran sus ofertas y aceptan postulaciones si estás
                identificado. Al registrar la sesión, Buscapega puede{" "}
                <strong className="text-white">buscar ofertas y postular automáticamente</strong>{" "}
                por ti según tus criterios. La sesión queda guardada{" "}
                <strong className="text-white">solo en tu equipo</strong>.
              </div>
              {autoApply.map((p) => (
                <PortalRow key={p.name} portal={p} onToggle={load} />
              ))}
            </Accordion>

            <Accordion key={`rev-${query}`} title="Portales revisables (sin auto-postulación)" count={reviewable.length} defaultOpen={!!query}>
              {reviewable.map((p) => (
                <PortalRow key={p.name} portal={p} onToggle={load} />
              ))}
            </Accordion>

            <Accordion key={`nos-${query}`} title="Portales que no permiten scraping" count={noScraping.length} defaultOpen={!!query}>
              {noScraping.length === 0 ? (
                <p className="text-gray-500 text-xs px-1 py-2">
                  Ningún portal en esta categoría por ahora.
                </p>
              ) : (
                noScraping.map((p) => <PortalRow key={p.name} portal={p} onToggle={load} />)
              )}
            </Accordion>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Sección Validar sitio ─────────────────────────────────────────────────────
function ValidateSection({ onAdded }: { onAdded: () => void }) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ValidationResult | null>(null);
  const [showHelp, setShowHelp] = useState(false);
  const [adding, setAdding] = useState(false);
  const [added, setAdded] = useState<{ name: string; category: string } | null>(null);

  async function handleValidate() {
    setAdded(null);
    const normalized = normalizeUrl(url);
    if (!normalized) return;
    if (normalized !== url) setUrl(normalized);
    if (!DOMAIN_RE.test(normalized)) {
      setResult({
        url: normalized, allows_scraping: false, has_google_auth: false,
        automatable: false, notes: [],
        error: "URL inválida — debe tener una estructura tipo 'sitio.com' (ej: buscapega.app).",
      });
      return;
    }
    setLoading(true);
    setResult(null);
    const data = await validatePortal(normalized);
    if (!data) {
      setResult({
        url: normalized, allows_scraping: false, has_google_auth: false,
        automatable: false, notes: [],
        error: "No se pudo contactar al servidor de validación. Verifica que el backend esté corriendo.",
      });
      setLoading(false);
      return;
    }
    setResult(data);
    setLoading(false);
  }

  const CATEGORY_LABEL: Record<string, string> = {
    auto_apply: "Portales con auto-postulación",
    reviewable: "Portales revisables (sin auto-postulación)",
    no_scraping: "Portales que no permiten scraping",
  };

  async function handleAdd() {
    if (!result) return;
    setAdding(true);
    const res = await addPortal({
      url: result.url,
      allows_scraping: result.allows_scraping,
      has_google_auth: result.has_google_auth,
    });
    setAdding(false);
    if (res && res.name && res.category) {
      setAdded({ name: res.name, category: res.category });
      onAdded();
    } else {
      setResult({ ...result, error: res?.error || "No se pudo agregar el portal." });
    }
  }

  // Enlace a GitHub con un issue prellenado para compartir el portal con la comunidad.
  function shareUrl(): string {
    const body = `## Portal de empleo propuesto\n\n- **URL:** ${result?.url}\n- **Permite scraping:** ${result?.allows_scraping ? "Sí" : "No"}\n- **Login con Google:** ${result?.has_google_auth ? "Sí" : "No detectado"}\n\n_Compartido desde la vista Validar sitio de Buscapega._`;
    return `${GITHUB_REPO}/issues/new?title=${encodeURIComponent("[Portal] " + (added?.name || result?.url || ""))}&body=${encodeURIComponent(body)}`;
  }

  return (
    <div className="bg-indigo-950/60 border border-indigo-700 rounded-2xl p-5">
      <div className="flex items-center gap-2 mb-2">
        <h2 className="text-lg font-semibold text-white">Validar sitio</h2>
        <button
          onClick={() => setShowHelp((v) => !v)}
          title="¿Qué hace validar un sitio?"
          aria-label="Ayuda sobre validar sitio"
          className="w-5 h-5 flex items-center justify-center rounded-full border border-indigo-500 text-indigo-300 text-xs hover:bg-indigo-800 hover:text-white transition-colors"
        >
          ?
        </button>
      </div>

      <p className="text-indigo-200/80 text-sm mb-3">
        Comprueba si un portal de empleo puede automatizarse: verifica que el sitio
        <strong> permita scraping</strong> (no lo bloquee en su <code>robots.txt</code>) y que ofrezca
        <strong> inicio de sesión con Google</strong>. Con ambos, Buscapega puede capturar la sesión y
        auto-postular.
      </p>

      {showHelp && (
        <div className="mb-3 px-4 py-3 bg-indigo-900/60 border border-indigo-700 rounded-lg text-indigo-100 text-xs leading-relaxed">
          <p className="font-semibold mb-1">¿Qué hace "Validar sitio"?</p>
          <ul className="list-disc list-inside space-y-1">
            <li>Lee el <code>robots.txt</code> del dominio para ver si permite scraping.</li>
            <li>Inspecciona la página en busca de autenticación con Google.</li>
            <li>Si el portal ya está registrado en Buscapega, lo indica.</li>
          </ul>
          <p className="mt-2">No guarda nada: es solo un diagnóstico de factibilidad.</p>
        </div>
      )}

      <p className="text-indigo-200/70 text-xs mb-2">
        Ingresa la URL de un portal de empleo para evaluar si es posible automatizarlo.
      </p>

      <div className="flex gap-3">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleValidate()}
          placeholder="https://www.ejemplo.com"
          className="flex-1 bg-gray-950 border border-indigo-700 text-white rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-400 placeholder-gray-600"
        />
        <button
          onClick={handleValidate}
          disabled={loading || !url.trim()}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-800 disabled:text-gray-600 text-white font-semibold px-5 py-2.5 rounded-lg transition-colors text-sm"
        >
          {loading ? "Validando..." : "Validar"}
        </button>
      </div>

      {/* Atajo con Claude Code (T7) */}
      <p className="text-indigo-200/60 text-xs mt-2">
        ¿Tienes Claude Code? También puedes validar desde la terminal con{" "}
        <code className="text-cyan-300 bg-indigo-900/60 px-1.5 py-0.5 rounded font-mono">claude /valida &lt;sitio&gt;</code>.
      </p>

      {result && result.error && (
        <div className="mt-4 px-4 py-3 bg-red-950 border border-red-800 rounded-lg">
          <p className="text-red-300 text-sm">{result.error}</p>
        </div>
      )}

      {result && !result.error && (
        <div className="mt-4 bg-gray-900 border border-gray-800 rounded-xl p-5">
          {result.already_configured && (
            <div className="mb-4 px-4 py-3 bg-yellow-950 border border-yellow-800 rounded-lg">
              <p className="text-yellow-300 text-sm">Este portal ya está registrado en Buscapega.</p>
            </div>
          )}
          <div className="flex items-center gap-3 mb-4">
            <span className={`text-2xl ${result.automatable ? "text-green-400" : "text-red-400"}`}>
              {result.automatable ? "✓" : "✗"}
            </span>
            <div>
              <p className="text-white font-semibold">
                {result.automatable ? "Sitio automatizable" : "No se puede automatizar"}
              </p>
              <p className="text-gray-500 text-xs">{result.url}</p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className={`rounded-lg p-4 border ${result.allows_scraping ? "bg-green-950 border-green-800" : "bg-red-950 border-red-800"}`}>
              <p className="text-xs uppercase tracking-wide text-gray-400 mb-1">Permite scraping</p>
              <p className={`text-lg font-bold ${result.allows_scraping ? "text-green-400" : "text-red-400"}`}>
                {result.allows_scraping ? "Sí" : "No"}
              </p>
            </div>
            <div className={`rounded-lg p-4 border ${result.has_google_auth ? "bg-green-950 border-green-800" : "bg-yellow-950 border-yellow-800"}`}>
              <p className="text-xs uppercase tracking-wide text-gray-400 mb-1">Auth con Google</p>
              <p className={`text-lg font-bold ${result.has_google_auth ? "text-green-400" : "text-yellow-400"}`}>
                {result.has_google_auth ? "Sí" : "No detectada"}
              </p>
            </div>
          </div>
          {result.notes.length > 0 && (
            <ul className="mt-4 space-y-1">
              {result.notes.map((note, i) => (
                <li key={i} className="text-gray-400 text-sm flex gap-2">
                  <span className="text-gray-600">·</span>{note}
                </li>
              ))}
            </ul>
          )}

          {/* Agregar a portales (T5) + compartir en GitHub (T6) */}
          {added ? (
            <div className="mt-5 px-4 py-3 bg-green-950 border border-green-800 rounded-lg">
              <p className="text-green-300 text-sm">
                ✓ <span className="font-semibold">{added.name}</span> se agregó a{" "}
                <span className="font-semibold">{CATEGORY_LABEL[added.category] || added.category}</span>.
              </p>
              <a
                href={shareUrl()}
                target="_blank"
                rel="noopener noreferrer"
                title="Abrirá una página de GitHub para proponer este portal a la comunidad"
                className="inline-flex items-center gap-2 mt-3 text-sm text-white bg-gray-800 hover:bg-gray-700 border border-gray-700 px-4 py-2 rounded-lg transition-colors"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4" aria-hidden="true">
                  <path d="M12 2C6.48 2 2 6.58 2 12.25c0 4.53 2.87 8.37 6.84 9.73.5.1.68-.22.68-.49 0-.24-.01-.87-.01-1.71-2.78.62-3.37-1.37-3.37-1.37-.45-1.18-1.11-1.5-1.11-1.5-.91-.64.07-.62.07-.62 1 .07 1.53 1.06 1.53 1.06.89 1.56 2.34 1.11 2.91.85.09-.66.35-1.11.63-1.37-2.22-.26-4.56-1.14-4.56-5.06 0-1.12.39-2.03 1.03-2.75-.1-.26-.45-1.3.1-2.71 0 0 .84-.27 2.75 1.05a9.4 9.4 0 0 1 5 0c1.91-1.32 2.75-1.05 2.75-1.05.55 1.41.2 2.45.1 2.71.64.72 1.03 1.63 1.03 2.75 0 3.93-2.34 4.79-4.57 5.05.36.32.68.94.68 1.9 0 1.37-.01 2.48-.01 2.81 0 .27.18.59.69.49A10.02 10.02 0 0 0 22 12.25C22 6.58 17.52 2 12 2z" />
                </svg>
                Compartir en GitHub
              </a>
            </div>
          ) : (
            result.automatable && !result.already_configured && (
              <div className="mt-5 flex items-center gap-3">
                <button
                  onClick={handleAdd}
                  disabled={adding}
                  className="bg-green-700 hover:bg-green-600 disabled:opacity-50 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
                >
                  {adding ? "Agregando..." : "Agregar a mis portales"}
                </button>
                <span className="text-gray-500 text-xs">
                  Se clasificará automáticamente según scraping y login con Google.
                </span>
              </div>
            )
          )}
        </div>
      )}
    </div>
  );
}

// ── Acordeón ──────────────────────────────────────────────────────────────────
function Accordion({
  title, count, defaultOpen = false, children,
}: { title: string; count: number; defaultOpen?: boolean; children: React.ReactNode }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-850 transition-colors"
      >
        <span className="flex items-center gap-2">
          <span className={`text-gray-500 transition-transform ${open ? "rotate-90" : ""}`}>▶</span>
          <span className="text-sm font-semibold text-gray-200">{title}</span>
        </span>
        <span className="text-xs text-gray-400 bg-gray-800 px-2 py-0.5 rounded-full">
          {count} {count === 1 ? "portal" : "portales"}
        </span>
      </button>
      {open && <div className="px-3 pb-3 flex flex-col gap-2">{children}</div>}
    </div>
  );
}

// ── Switch ────────────────────────────────────────────────────────────────────
function Switch({ on, onChange, disabled }: { on: boolean; onChange: () => void; disabled?: boolean }) {
  return (
    <button
      role="switch"
      aria-checked={on}
      disabled={disabled}
      onClick={onChange}
      className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors disabled:opacity-50 ${
        on ? "bg-green-600" : "bg-gray-600"
      }`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
          on ? "translate-x-6" : "translate-x-1"
        }`}
      />
    </button>
  );
}

// ── Fila de portal ────────────────────────────────────────────────────────────
function PortalRow({ portal, onToggle }: { portal: Portal; onToggle: () => void }) {
  const [active, setActive] = useState(portal.active);
  const [showSession, setShowSession] = useState(false);
  const { flag, country } = marketInfo(portal.market);

  async function handleSwitch() {
    const next = !active;
    setActive(next); // optimista
    const ok = await togglePortal(portal.name, next);
    if (!ok) setActive(!next); // revertir si falla
    else onToggle();
  }

  return (
    <div className="bg-gray-950/60 border border-gray-800 rounded-lg px-4 py-3">
      <div className="flex items-center justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <span className="text-white font-medium">{portal.name}</span>
            <span className="text-base cursor-default" title={country} aria-label={country}>{flag}</span>
            {portal.auto_apply && (
              <span className="text-xs text-blue-400 bg-blue-950 border border-blue-800 px-2 py-0.5 rounded">
                Auto-postulación
              </span>
            )}
          </div>
          <p className="text-gray-500 text-xs truncate">{portal.url}</p>
          {portal.applications_count > 0 && (
            <p className="text-gray-400 text-xs mt-1">
              {portal.applications_count} postulación{portal.applications_count !== 1 ? "es" : ""} realizadas
            </p>
          )}
        </div>

        <div className="flex items-center gap-3 shrink-0">
          {portal.auto_apply ? (
            <span className={`text-xs ${active ? "text-green-400" : "text-gray-500"}`}>
              {active ? "Incluido en búsquedas" : "No incluido en búsquedas"}
            </span>
          ) : (
            <a
              href={portal.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-xs text-gray-300 bg-gray-800 hover:bg-gray-700 border border-gray-700 px-3 py-1.5 rounded-lg transition-colors"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5" aria-hidden="true">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                <path d="M15 3h6v6M10 14 21 3" />
              </svg>
              Visitar
            </a>
          )}
          <Switch on={active} onChange={handleSwitch} />
        </div>
      </div>

      {/* Aviso destacado: el portal necesita sesión y todavía no está registrada. Es la
          causa más común de "activé el portal y no llega nada", así que va en rojo y por
          delante del resto de avisos. */}
      {portal.requires_auth && !portal.session_active && (
        <div className="mt-2 px-3 py-2.5 bg-red-950/70 border border-red-700 rounded text-red-200 text-xs flex items-start gap-2">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4 shrink-0 mt-0.5" aria-hidden="true">
            <path d="M12 9v4M12 17h.01" />
            <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
          </svg>
          <span>
            <strong className="text-white">Sesión con Google no iniciada.</strong> Este portal
            no buscará ofertas ni podrá postular hasta que la registres con el botón de abajo.
          </span>
        </div>
      )}

      {/* Aviso para portales activos sin auto-postulación (revisión manual) */}
      {active && !portal.auto_apply && (
        <div className="mt-2 px-3 py-2 bg-amber-950/60 border border-amber-800 rounded text-amber-300 text-xs">
          Portal activado. Importante: te llegarán las ofertas pero deberás postular manualmente.
        </div>
      )}

      {/* Botón "Registrar sesión con Google" — portales con auto-postulación o revisables */}
      <div className="mt-2">
        <button
          onClick={() => setShowSession(true)}
          className="flex items-center gap-1.5 text-xs text-gray-300 hover:text-white bg-gray-800 hover:bg-gray-700 border border-gray-700 px-3 py-1.5 rounded-lg transition-colors"
        >
          <svg viewBox="0 0 24 24" className="w-3.5 h-3.5" aria-hidden="true">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.27-4.74 3.27-8.1z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.99.66-2.26 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84A11 11 0 0 0 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.1a6.6 6.6 0 0 1 0-4.2V7.06H2.18a11 11 0 0 0 0 9.88l3.66-2.84z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84C6.71 7.31 9.14 5.38 12 5.38z"/>
          </svg>
          Registrar sesión con Google
        </button>
      </div>

      {showSession && (
        <SessionDialog portal={portal} onClose={() => setShowSession(false)} />
      )}
    </div>
  );
}

// ── Diálogo de registro de sesión (persistente) ───────────────────────────────
function SessionDialog({ portal, onClose }: { portal: Portal; onClose: () => void }) {
  const [copied, setCopied] = useState<string | null>(null);
  const slug = portalSlug(portal.name);
  // Wrapper que crea el venv e instala playwright automáticamente la primera vez
  // (evita el ModuleNotFoundError de ejecutar python3 setup/setup_session.py directo).
  const cmdPython = `./configuraciones/setup-sessions.sh ${slug}`;
  const cmdClaude = `claude /autentica ${slug}`;

  async function copy(text: string, id: string) {
    await navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 w-full max-w-lg shadow-2xl">
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-white font-semibold text-lg">Registrar sesión — {portal.name}</h3>
          <button onClick={onClose} aria-label="Cerrar" className="text-gray-400 hover:text-white text-xl leading-none">×</button>
        </div>

        <p className="text-gray-300 text-sm mb-4">
          Registra tu sesión con Google aquí. Esta sesión quedará guardada <strong>solo en tu equipo</strong>.
        </p>

        <p className="text-xs text-gray-500 mb-1">Ejecuta este comando en la terminal del proyecto:</p>
        <div className="flex items-center gap-2 mb-4">
          <code className="flex-1 text-cyan-400 text-sm font-mono bg-gray-950 px-3 py-2 rounded break-all">{cmdPython}</code>
          <button
            onClick={() => copy(cmdPython, "py")}
            className="shrink-0 text-xs text-gray-400 hover:text-white bg-gray-800 hover:bg-gray-700 border border-gray-700 px-3 py-2 rounded transition-colors"
          >
            {copied === "py" ? "✓ Copiado" : "Copiar"}
          </button>
        </div>

        <p className="text-xs text-gray-500 mb-1">Alternativa con Claude Code:</p>
        <div className="flex items-center gap-2">
          <code className="flex-1 text-cyan-400 text-sm font-mono bg-gray-950 px-3 py-2 rounded break-all">{cmdClaude}</code>
          <button
            onClick={() => copy(cmdClaude, "claude")}
            className="shrink-0 text-xs text-gray-400 hover:text-white bg-gray-800 hover:bg-gray-700 border border-gray-700 px-3 py-2 rounded transition-colors"
          >
            {copied === "claude" ? "✓ Copiado" : "Copiar"}
          </button>
        </div>

        <div className="mt-6 text-right">
          <button onClick={onClose} className="text-sm text-gray-300 hover:text-white bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-lg transition-colors">
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}
