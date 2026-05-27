"use client";

import { useEffect, useState } from "react";
import { Answer, getAnswers, createAnswer, updateAnswer, deleteAnswer } from "@/lib/api";

const PORTALES = ["chiletrabajos", "tecnoempleo", "getonbrd", "remotelatinos", "chumiit"];

const EMPTY_FORM = { descripcion: "", keywords: "", respuesta: "", portal: "" };

export default function RespuestasPage() {
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);

  async function load() {
    setLoading(true);
    setAnswers(await getAnswers());
    setLoading(false);
  }

  useEffect(() => { load(); }, []);

  function openAdd() {
    setEditingId(null);
    setForm(EMPTY_FORM);
    setShowForm(true);
  }

  function openEdit(a: Answer) {
    setEditingId(a.id);
    setForm({
      descripcion: a.descripcion,
      keywords: a.keywords.join(", "),
      respuesta: a.respuesta,
      portal: a.portal ?? "",
    });
    setShowForm(true);
  }

  function cancel() {
    setShowForm(false);
    setEditingId(null);
    setForm(EMPTY_FORM);
  }

  async function save() {
    const keywords = form.keywords.split(",").map((k) => k.trim()).filter(Boolean);
    if (!form.descripcion || !form.respuesta || keywords.length === 0) return;
    setSaving(true);
    const payload = {
      descripcion: form.descripcion,
      keywords,
      respuesta: form.respuesta,
      portal: form.portal || null,
    };
    if (editingId !== null) {
      await updateAnswer(editingId, payload);
    } else {
      await createAnswer(payload);
    }
    await load();
    cancel();
    setSaving(false);
  }

  async function remove(id: number) {
    if (!confirm("¿Eliminar esta respuesta?")) return;
    await deleteAnswer(id);
    await load();
  }

  async function toggle(a: Answer) {
    await updateAnswer(a.id, { activo: !a.activo });
    await load();
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">Respuestas automáticas</h1>
          <p className="text-gray-400 text-sm mt-1">
            Wunen usa estas respuestas para completar formularios de postulación
          </p>
        </div>
        <button
          onClick={openAdd}
          className="bg-blue-600 hover:bg-blue-500 text-white font-semibold px-4 py-2 rounded-lg text-sm transition-colors"
        >
          + Agregar respuesta
        </button>
      </div>

      {/* Tip de keywords especiales */}
      <div className="mb-6 p-4 bg-gray-900 border border-gray-700 rounded-xl text-sm text-gray-400">
        <p className="font-medium text-gray-300 mb-1">Keywords especiales para ChileTrabajos</p>
        <div className="flex flex-wrap gap-3 mt-2">
          {[
            { kw: "pretensiones_renta", desc: 'Renta pretendida. Respuesta: "1500000"' },
            { kw: "disponibilidad_inmediata", desc: 'Respuesta: "true" o "false"' },
          ].map(({ kw, desc }) => (
            <div key={kw} className="flex items-center gap-2">
              <code className="bg-gray-800 text-blue-300 px-2 py-0.5 rounded text-xs">{kw}</code>
              <span className="text-xs text-gray-500">→ {desc}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Formulario inline */}
      {showForm && (
        <div className="mb-6 p-5 bg-gray-900 border border-blue-700 rounded-xl">
          <h2 className="text-sm font-semibold text-white mb-4">
            {editingId !== null ? "Editar respuesta" : "Nueva respuesta"}
          </h2>
          <div className="flex flex-col gap-3">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Descripción</label>
              <input
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                placeholder='Ej: "Formación académica"'
                value={form.descripcion}
                onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">
                Keywords para matching{" "}
                <span className="text-gray-600">(separados por coma)</span>
              </label>
              <input
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                placeholder='Ej: "formación, estudios, nivel académico"'
                value={form.keywords}
                onChange={(e) => setForm({ ...form, keywords: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Respuesta</label>
              <textarea
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500 resize-none"
                rows={4}
                placeholder="Texto que se llenará en el campo del formulario..."
                value={form.respuesta}
                onChange={(e) => setForm({ ...form, respuesta: e.target.value })}
              />
              <p className="text-xs text-gray-600 mt-1">{form.respuesta.length}/255 caracteres</p>
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">
                Portal <span className="text-gray-600">(vacío = todos)</span>
              </label>
              <select
                className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                value={form.portal}
                onChange={(e) => setForm({ ...form, portal: e.target.value })}
              >
                <option value="">Todos los portales</option>
                {PORTALES.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex gap-3 mt-4">
            <button
              onClick={save}
              disabled={saving}
              className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold px-4 py-2 rounded-lg text-sm transition-colors"
            >
              {saving ? "Guardando..." : "Guardar"}
            </button>
            <button
              onClick={cancel}
              className="text-gray-400 hover:text-white px-4 py-2 text-sm transition-colors"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      {/* Lista */}
      {loading ? (
        <div className="text-center py-20 text-gray-500">Cargando...</div>
      ) : answers.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-gray-500">Aún no hay respuestas configuradas.</p>
          <p className="text-gray-600 text-sm mt-2">
            Agrega respuestas para que Wunen complete los formularios automáticamente.
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {answers.map((a) => (
            <div
              key={a.id}
              className={`p-4 rounded-xl border transition-colors ${
                a.activo
                  ? "bg-gray-900 border-gray-800"
                  : "bg-gray-950 border-gray-800 opacity-50"
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    <span className="text-sm font-semibold text-white">{a.descripcion}</span>
                    {a.portal && (
                      <span className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded-full border border-gray-700">
                        {a.portal}
                      </span>
                    )}
                  </div>
                  <div className="flex flex-wrap gap-1 mb-3">
                    {a.keywords.map((kw) => (
                      <span
                        key={kw}
                        className="text-xs bg-blue-950 text-blue-300 px-2 py-0.5 rounded border border-blue-900"
                      >
                        {kw}
                      </span>
                    ))}
                  </div>
                  <p className="text-sm text-gray-300 leading-relaxed line-clamp-3">{a.respuesta}</p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={() => toggle(a)}
                    title={a.activo ? "Desactivar" : "Activar"}
                    className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs transition-colors border ${
                      a.activo
                        ? "border-green-800 text-green-400 hover:bg-green-950"
                        : "border-gray-700 text-gray-600 hover:bg-gray-800"
                    }`}
                  >
                    {a.activo ? "●" : "○"}
                  </button>
                  <button
                    onClick={() => openEdit(a)}
                    className="w-8 h-8 rounded-lg border border-gray-700 text-gray-400 hover:text-white hover:bg-gray-800 flex items-center justify-center text-xs transition-colors"
                  >
                    ✎
                  </button>
                  <button
                    onClick={() => remove(a.id)}
                    className="w-8 h-8 rounded-lg border border-gray-700 text-gray-600 hover:text-red-400 hover:border-red-900 flex items-center justify-center text-xs transition-colors"
                  >
                    ✕
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
