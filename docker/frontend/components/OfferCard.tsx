"use client";

import { Offer, applyOffer, discardOffer, blockCompany } from "@/lib/api";

interface Props {
  offer: Offer;
  onAction: () => void;
}

const PORTAL_COLORS: Record<string, string> = {
  Remotive: "bg-emerald-600",
  RemoteOK: "bg-blue-600",
  Tecnoempleo: "bg-orange-600",
  "Chumi-IT": "bg-purple-600",
  ChileTrabajos: "bg-red-600",
  RemoteLatinos: "bg-teal-600",
  LaraJobs: "bg-pink-600",
  FlexJobs: "bg-yellow-600",
  GetOnBrd: "bg-indigo-600",
  "Torre.ai": "bg-cyan-600",
  InfoJobs: "bg-sky-600",
  default: "bg-gray-600",
};

const PORTAL_LOGOS: Record<string, string> = {
  Remotive: "https://remotive.com/favicon.ico",
  RemoteOK: "https://remoteok.com/favicon.ico",
  Tecnoempleo: "https://www.tecnoempleo.com/favicon.ico",
  "Chumi-IT": "https://chumi-it.com/favicon.ico",
  ChileTrabajos: "https://www.chiletrabajos.cl/favicon.ico",
  RemoteLatinos: "https://www.remotelatinos.com/favicon.ico",
  LaraJobs: "https://larajobs.com/favicon.ico",
  FlexJobs: "https://www.flexjobs.com/favicon.ico",
  GetOnBrd: "https://www.getonbrd.com/favicon.ico",
  "Torre.ai": "https://torre.ai/favicon.ico",
  InfoJobs: "https://www.infojobs.net/favicon.ico",
};

// Portales con formulario propio: la postulación se puede automatizar
// Portales externos: redirigen al portal de la empresa
const PORTAL_AUTO_APPLY = new Set([
  "Tecnoempleo",
  "Chumi-IT",
  "ChileTrabajos",
  "RemoteLatinos",
  "GetOnBrd",
  "Torre.ai",
  "InfoJobs",
]);

function ScoreBadge({ score }: { score: number | null }) {
  if (score === null) return <span className="text-gray-500 text-sm">Sin evaluar</span>;
  const color =
    score >= 80 ? "bg-green-500" : score >= 60 ? "bg-yellow-500" : score >= 40 ? "bg-orange-500" : "bg-red-500";
  return (
    <span className={`${color} text-white text-sm font-bold px-2 py-1 rounded`}>
      {score}/100
    </span>
  );
}

export default function OfferCard({ offer, onAction }: Props) {
  const portalColor = PORTAL_COLORS[offer.portal] || PORTAL_COLORS.default;
  const portalLogo = PORTAL_LOGOS[offer.portal];
  const techs: string[] = offer.technologies ? JSON.parse(offer.technologies) : [];

  async function handleApply() {
    window.open(offer.url, "_blank", "noopener,noreferrer");
    await applyOffer(offer.id);
    onAction();
  }

  async function handleDiscard() {
    await discardOffer(offer.id);
    onAction();
  }

  async function handleBlock() {
    if (confirm(`¿Bloquear todas las ofertas de "${offer.company}"?`)) {
      await blockCompany(offer.company);
      await discardOffer(offer.id);
      onAction();
    }
  }

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-xl p-5 flex flex-col gap-3 hover:border-gray-500 transition-colors">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            {portalLogo && (
              <img
                src={portalLogo}
                alt={offer.portal}
                className="w-7 h-7 rounded-lg object-contain bg-white p-0.5 shadow"
                onError={(e) => { e.currentTarget.style.display = "none"; }}
              />
            )}
            <span className={`${portalColor} text-white text-xs font-semibold px-2 py-1 rounded`}>
              {offer.portal}
            </span>
            {offer.modality && (
              <span className="bg-gray-700 text-gray-300 text-xs px-2 py-0.5 rounded">
                {offer.modality}
              </span>
            )}
          </div>
          <a
            href={offer.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-white font-semibold text-lg hover:text-blue-400 transition-colors line-clamp-2"
          >
            {offer.title}
          </a>
          <p className="text-gray-400 text-sm mt-0.5">{offer.company}</p>
        </div>
        <div className="flex-shrink-0">
          <ScoreBadge score={offer.score} />
        </div>
      </div>

      {/* Summary */}
      {offer.summary && (
        <p className="text-gray-300 text-sm leading-relaxed">{offer.summary}</p>
      )}

      {/* Technologies */}
      {techs.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {techs.map((t) => (
            <span
              key={t}
              className="bg-gray-800 text-gray-300 text-xs px-2 py-0.5 rounded border border-gray-700"
            >
              {t}
            </span>
          ))}
        </div>
      )}

      {/* Salary + Reason */}
      <div className="flex items-center justify-between gap-3 text-sm flex-wrap">
        {offer.salary && (
          <span className="text-green-400 font-medium">{offer.salary}</span>
        )}
        {offer.reason && (
          <span className="text-gray-500 italic text-xs flex-1 text-right">{offer.reason}</span>
        )}
      </div>

      {/* Actions */}
      <div className="flex gap-2 pt-1 border-t border-gray-800">
        {PORTAL_AUTO_APPLY.has(offer.portal) ? (
          <button
            onClick={handleApply}
            className="flex-1 bg-blue-700 hover:bg-blue-600 text-white text-sm font-semibold py-2 rounded-lg transition-colors"
          >
            Postular
          </button>
        ) : (
          <button
            onClick={handleApply}
            className="flex-1 bg-gray-600 hover:bg-gray-500 text-white text-xs font-semibold py-2 px-2 rounded-lg transition-colors"
          >
            Acceder (Abre una ventana nueva)
          </button>
        )}
        <button
          onClick={handleDiscard}
          className="flex-1 bg-gray-700 hover:bg-gray-600 text-white text-sm font-semibold py-2 rounded-lg transition-colors"
        >
          Descartar
        </button>
        <button
          onClick={handleBlock}
          className="bg-red-900 hover:bg-red-800 text-red-300 text-sm font-semibold px-3 py-2 rounded-lg transition-colors"
          title={`Bloquear ${offer.company}`}
        >
          Bloquear empresa
        </button>
      </div>
    </div>
  );
}
