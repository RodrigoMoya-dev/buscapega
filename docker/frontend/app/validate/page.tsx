"use client";

import { useState } from "react";
import { validatePortal } from "@/lib/api";

interface ValidationResult {
  url: string;
  allows_scraping: boolean;
  has_google_auth: boolean;
  automatable: boolean;
  notes: string[];
}

export default function ValidatePage() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ValidationResult | null>(null);

  async function handleValidate() {
    if (!url.trim()) return;
    setLoading(true);
    setResult(null);
    const data = await validatePortal(url.trim());
    setResult(data);
    setLoading(false);
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-white mb-2">Validar sitio</h1>
      <p className="text-gray-400 text-sm mb-8">
        Ingresa la URL de un portal de empleo para evaluar si es posible automatizarlo.
        Se verifican dos criterios: que el sitio permita scraping y que tenga autenticación con Google.
      </p>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 mb-6">
        <p className="text-xs text-gray-500 mb-3 uppercase tracking-wide">Equivalente al comando Claude:</p>
        <code className="text-cyan-400 text-sm font-mono bg-gray-950 px-3 py-2 rounded block">
          claude /valida &lt;url del sitio&gt;
        </code>
      </div>

      <div className="flex gap-3 mb-8">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleValidate()}
          placeholder="https://www.ejemplo.com"
          className="flex-1 bg-gray-900 border border-gray-700 text-white rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-blue-500 placeholder-gray-600"
        />
        <button
          onClick={handleValidate}
          disabled={loading || !url.trim()}
          className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 disabled:text-gray-600 text-white font-semibold px-5 py-2.5 rounded-lg transition-colors text-sm"
        >
          {loading ? "Validando..." : "Validar"}
        </button>
      </div>

      {result && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-5">
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

          <div className="grid grid-cols-2 gap-4 mb-5">
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
            <div>
              <p className="text-xs uppercase tracking-wide text-gray-500 mb-2">Detalles</p>
              <ul className="space-y-1">
                {result.notes.map((note, i) => (
                  <li key={i} className="text-gray-400 text-sm flex gap-2">
                    <span className="text-gray-600">·</span>
                    {note}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
