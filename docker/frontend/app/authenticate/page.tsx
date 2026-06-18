"use client";

import { useEffect, useState } from "react";
import { getPortals, Portal } from "@/lib/api";

export default function AuthenticatePage() {
  const [portals, setPortals] = useState<Portal[]>([]);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    const data = await getPortals();
    setPortals(data);
    setLoading(false);
  }

  useEffect(() => { load(); }, []);

  async function handleCopy(text: string, key: string) {
    await navigator.clipboard.writeText(text);
    setCopied(key);
    setTimeout(() => setCopied(null), 2000);
  }

  const autoApplyPortals = portals.filter((p) => p.auto_apply);
  const manualPortals = portals.filter((p) => !p.auto_apply);
  const activeCount = autoApplyPortals.filter((p) => p.session_active).length;
  const inactiveCount = autoApplyPortals.filter((p) => !p.session_active).length;

  const cmd1 = "python3 setup/setup_session.py --lista";
  const cmd2 = "python3 setup/setup_session.py <portal>";
  const cmdClaude = "claude /autentica";

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-white mb-2">Portales de empleo</h1>
      <p className="text-gray-400 text-sm mb-8">
        Administra los portales registrados y el estado de autenticación de cada uno.
        Para activar un portal, captura la sesión desde la máquina local.
      </p>

      {/* Tip comandos */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 mb-6">
        <p className="text-xs text-gray-500 mb-3">
          Tip: Para autenticar portales inactivos, ejecuta estos comandos desde la terminal del proyecto:
        </p>
        <div className="space-y-2">
          <CopyRow text={cmd1} copied={copied} id="cmd1" onCopy={handleCopy} />
          <CopyRow text={cmd2} copied={copied} id="cmd2" onCopy={handleCopy} />
        </div>
        <p className="text-xs text-gray-600 mt-3">
          O usando Claude Code (alternativa):
        </p>
        <CopyRow text={cmdClaude} copied={copied} id="cmdClaude" onCopy={handleCopy} />
      </div>

      {/* Resumen */}
      {!loading && (
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 text-center">
            <p className="text-2xl font-bold text-white">{autoApplyPortals.length}</p>
            <p className="text-xs text-gray-500 mt-1">Portales con auto-postulación</p>
          </div>
          <div className="bg-green-950 border border-green-800 rounded-xl p-4 text-center">
            <p className="text-2xl font-bold text-green-400">{activeCount}</p>
            <p className="text-xs text-gray-500 mt-1">Sesiones activas</p>
          </div>
          <div className="bg-red-950 border border-red-800 rounded-xl p-4 text-center">
            <p className="text-2xl font-bold text-red-400">{inactiveCount}</p>
            <p className="text-xs text-gray-500 mt-1">Sesiones inactivas</p>
          </div>
        </div>
      )}

      {loading ? (
        <div className="text-center py-10 text-gray-500">Cargando portales...</div>
      ) : (
        <>
          {/* Portales con auto-postulación */}
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
            Portales con auto-postulación
          </h2>
          <div className="flex flex-col gap-3 mb-8">
            {autoApplyPortals.map((portal) => (
              <PortalRow key={portal.name} portal={portal} />
            ))}
          </div>

          {/* Portales manuales */}
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
            Portales sin auto-postulación (manual)
          </h2>
          <div className="flex flex-col gap-3">
            {manualPortals.map((portal) => (
              <PortalRow key={portal.name} portal={portal} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

function CopyRow({ text, copied, id, onCopy }: { text: string; copied: string | null; id: string; onCopy: (text: string, id: string) => void }) {
  return (
    <div className="flex items-center gap-2">
      <code className="flex-1 text-cyan-400 text-sm font-mono bg-gray-950 px-3 py-2 rounded">
        {text}
      </code>
      <button
        onClick={() => onCopy(text, id)}
        className="shrink-0 text-xs text-gray-400 hover:text-white bg-gray-800 hover:bg-gray-700 border border-gray-700 px-3 py-2 rounded transition-colors"
      >
        {copied === id ? "✓ Copiado" : "Copiar"}
      </button>
    </div>
  );
}

function PortalRow({ portal }: { portal: Portal }) {
  return (
    <div className="flex items-center justify-between bg-gray-900 border border-gray-800 rounded-xl px-5 py-4">
      <div className="flex-1">
        <div className="flex items-center gap-3 mb-1">
          <span className="text-white font-medium">{portal.name}</span>
          <span className="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded">{portal.market}</span>
          {portal.auto_apply && (
            <span className="text-xs text-blue-400 bg-blue-950 border border-blue-800 px-2 py-0.5 rounded">
              Auto-postulación
            </span>
          )}
        </div>
        <p className="text-gray-500 text-xs">{portal.url}</p>
        {portal.applications_count > 0 && (
          <p className="text-gray-400 text-xs mt-1">
            {portal.applications_count} postulación{portal.applications_count !== 1 ? "es" : ""} realizadas
          </p>
        )}
      </div>
      <div className="flex items-center gap-2">
        {portal.auto_apply ? (
          <span className={`flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full border ${
            portal.session_active
              ? "text-green-400 bg-green-950 border-green-800"
              : "text-red-400 bg-red-950 border-red-800"
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${portal.session_active ? "bg-green-400" : "bg-red-400"}`} />
            {portal.session_active ? "Activo" : "Inactivo"}
          </span>
        ) : (
          <span className="text-xs text-gray-600 px-3 py-1.5">Manual</span>
        )}
      </div>
    </div>
  );
}
