"use client";

import { useEffect, useState } from "react";
import { getSettings, saveSettings } from "@/lib/api";

export default function SettingsPage() {
  const [form, setForm] = useState({
    whatsapp_phone: "",
    notification_email: "",
    reply_email: "",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    getSettings().then((data) => {
      if (data) setForm({ ...form, ...data });
      setLoading(false);
    });
  }, []);

  async function handleSave() {
    setSaving(true);
    await saveSettings(form);
    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  function set(field: string, val: string) {
    setForm((prev) => ({ ...prev, [field]: val }));
  }

  return (
    <div className="max-w-xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold text-white mb-2">Configuración</h1>
      <p className="text-gray-400 text-sm mb-8">
        Ajustes generales del sistema de postulación.
      </p>

      {loading ? (
        <div className="text-gray-500 text-center py-10">Cargando...</div>
      ) : (
        <div className="space-y-8">
          {/* WhatsApp */}
          <section className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <h2 className="text-base font-semibold text-white mb-1">Notificaciones WhatsApp</h2>
            <p className="text-gray-500 text-xs mb-5">
              Número de teléfono que recibirá las notificaciones de postulaciones via Baileys.
            </p>
            <div>
              <label className="block text-xs text-gray-500 mb-1.5">Número de teléfono</label>
              <input
                type="tel"
                value={form.whatsapp_phone}
                onChange={(e) => set("whatsapp_phone", e.target.value)}
                placeholder="+56912345678"
                className="w-full bg-gray-950 border border-gray-700 text-white rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-blue-500 placeholder-gray-600"
              />
              <p className="text-gray-600 text-xs mt-1.5">Incluir código de país (ej: +56 para Chile)</p>
            </div>
          </section>

          {/* Email */}
          <section className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <h2 className="text-base font-semibold text-white mb-1">Correo de postulaciones</h2>
            <p className="text-gray-500 text-xs mb-5">
              Correo usado para el envío y recepción de respuestas de las postulaciones automáticas.
            </p>
            <div className="space-y-4">
              <div>
                <label className="block text-xs text-gray-500 mb-1.5">Correo de envío</label>
                <input
                  type="email"
                  value={form.notification_email}
                  onChange={(e) => set("notification_email", e.target.value)}
                  placeholder="correo@ejemplo.com"
                  className="w-full bg-gray-950 border border-gray-700 text-white rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-blue-500 placeholder-gray-600"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1.5">Correo de respuesta (reply-to)</label>
                <input
                  type="email"
                  value={form.reply_email}
                  onChange={(e) => set("reply_email", e.target.value)}
                  placeholder="respuesta@ejemplo.com"
                  className="w-full bg-gray-950 border border-gray-700 text-white rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-blue-500 placeholder-gray-600"
                />
              </div>
            </div>
          </section>

          <div className="flex items-center gap-4">
            <button
              onClick={handleSave}
              disabled={saving}
              className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 text-white font-semibold px-6 py-2.5 rounded-lg transition-colors text-sm"
            >
              {saving ? "Guardando..." : "Guardar configuración"}
            </button>
            {saved && <span className="text-green-400 text-sm">✓ Guardado</span>}
          </div>
        </div>
      )}
    </div>
  );
}
