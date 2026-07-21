"use client";

/**
 * Aviso persistente con botón de cierre.
 *
 * Antes los mensajes de resultado (prueba de WhatsApp, prueba de correo, "Guardado")
 * se borraban solos con un setTimeout de 2 a 6 segundos. Si el usuario estaba mirando
 * otra parte de la pantalla, el resultado se perdía y no había forma de recuperarlo.
 * Ahora quedan fijos hasta que se cierran a mano.
 */
export type AvisoTipo = "ok" | "error" | "info";

const ESTILOS: Record<AvisoTipo, { caja: string; texto: string; boton: string }> = {
  ok: {
    caja: "bg-green-950/70 border-green-700",
    texto: "text-green-200",
    boton: "text-green-400 hover:text-green-100 hover:bg-green-900/60",
  },
  error: {
    caja: "bg-red-950/70 border-red-700",
    texto: "text-red-200",
    boton: "text-red-400 hover:text-red-100 hover:bg-red-900/60",
  },
  info: {
    caja: "bg-slate-800/70 border-slate-600",
    texto: "text-gray-200",
    boton: "text-gray-400 hover:text-white hover:bg-slate-700/60",
  },
};

export default function Aviso({
  tipo,
  mensaje,
  onClose,
}: {
  tipo: AvisoTipo;
  mensaje: string;
  onClose: () => void;
}) {
  const e = ESTILOS[tipo];
  return (
    <div
      // role=status para que los lectores de pantalla anuncien el resultado al aparecer.
      role="status"
      className={`flex items-start gap-2 px-3 py-2.5 border rounded-lg text-sm ${e.caja} ${e.texto}`}
    >
      <span className="flex-1 leading-relaxed">{mensaje}</span>
      <button
        onClick={onClose}
        aria-label="Cerrar aviso"
        title="Cerrar"
        className={`shrink-0 -mr-1 -mt-0.5 w-6 h-6 flex items-center justify-center rounded transition-colors ${e.boton}`}
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="w-3.5 h-3.5" aria-hidden="true">
          <path d="M18 6 6 18M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}
