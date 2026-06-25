"use client";

import { useEffect, useState } from "react";
import { getSettings, saveSettings, testWhatsapp } from "@/lib/api";

export default function SettingsPage() {
  const [form, setForm] = useState({
    user_name: "",
    whatsapp_phone: "",
    notification_email: "",
    reply_email: "",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [testingWa, setTestingWa] = useState(false);
  const [waTestResult, setWaTestResult] = useState<{ status: string; message: string } | null>(null);
  // T11: cuando está activo, el reply-to replica el correo de envío.
  const [sameReply, setSameReply] = useState(false);

  useEffect(() => {
    getSettings().then((data) => {
      if (data) {
        setForm((prev) => ({ ...prev, ...data }));
        // Si reply == envío (o no hay reply), inicia el checkbox marcado.
        if (!data.reply_email || data.reply_email === data.notification_email) setSameReply(true);
      }
      setLoading(false);
    });
  }, []);

  async function handleSave() {
    setSaving(true);
    // Si el checkbox está activo, el reply-to replica el correo de envío.
    const payload = sameReply ? { ...form, reply_email: form.notification_email } : form;
    if (sameReply && form.reply_email !== form.notification_email) {
      setForm(payload);
    }
    await saveSettings(payload);
    setSaving(false);
    setSaved(true);
    // T9: refrescar el saludo del menú sin recargar la página.
    window.dispatchEvent(new CustomEvent("wunen:settings-updated", { detail: { user_name: payload.user_name } }));
    setTimeout(() => setSaved(false), 2000);
  }

  async function handleTestWhatsapp() {
    setTestingWa(true);
    setWaTestResult(null);
    const result = await testWhatsapp();
    setWaTestResult(result ?? { status: "error", message: "Sin respuesta del servidor" });
    setTestingWa(false);
    setTimeout(() => setWaTestResult(null), 5000);
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
          {/* Nombre de usuario */}
          <section className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <h2 className="text-base font-semibold text-white mb-1">Tu nombre</h2>
            <p className="text-gray-500 text-xs mb-5">
              Se muestra en el saludo del menú superior.
            </p>
            <div>
              <label className="block text-xs text-gray-500 mb-1.5">Nombre</label>
              <input
                type="text"
                value={form.user_name}
                onChange={(e) => set("user_name", e.target.value)}
                placeholder="Rodrigo"
                className="w-full bg-gray-950 border border-gray-700 text-white rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-blue-500 placeholder-gray-600"
              />
            </div>
          </section>

          {/* WhatsApp */}
          <section className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <h2 className="text-base font-semibold text-white mb-1">Notificaciones WhatsApp</h2>
            <p className="text-gray-500 text-xs mb-5">
              Número que recibirá las notificaciones de postulaciones via Baileys.
            </p>
            <div className="mb-4">
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
            <div className="flex items-center gap-3">
              <button
                onClick={handleTestWhatsapp}
                disabled={testingWa || !form.whatsapp_phone.trim()}
                className="bg-gray-800 hover:bg-gray-700 disabled:opacity-40 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors border border-gray-700"
              >
                {testingWa ? "Enviando..." : "Enviar mensaje de prueba"}
              </button>
              {waTestResult && (
                <span className={`text-sm ${waTestResult.status === "ok" ? "text-green-400" : "text-red-400"}`}>
                  {waTestResult.message}
                </span>
              )}
            </div>

            {/* Setup WhatsApp */}
            <div className="mt-6 border-t border-gray-800 pt-5">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Configurar WhatsApp (Baileys)</p>
              <ol className="space-y-2 text-xs text-gray-500">
                <li><span className="text-gray-400 font-medium">1.</span> Accede al servidor: <code className="text-cyan-400 bg-gray-800 px-1.5 py-0.5 rounded">ssh rodrigo@presto</code></li>
                <li><span className="text-gray-400 font-medium">2.</span> Entra al contenedor WhatsApp: <code className="text-cyan-400 bg-gray-800 px-1.5 py-0.5 rounded">docker exec -it wunen_whatsapp sh</code></li>
                <li><span className="text-gray-400 font-medium">3.</span> Ejecuta el script de vinculación: <code className="text-cyan-400 bg-gray-800 px-1.5 py-0.5 rounded">node link.js</code></li>
                <li><span className="text-gray-400 font-medium">4.</span> Escanea el código QR con tu WhatsApp (Ajustes → Dispositivos vinculados)</li>
                <li><span className="text-gray-400 font-medium">5.</span> Usa el botón "Enviar mensaje de prueba" para verificar</li>
              </ol>
            </div>
          </section>

          {/* Email */}
          <section className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <h2 className="text-base font-semibold text-white mb-1">Correo de postulaciones</h2>
            <p className="text-gray-500 text-xs mb-5">
              Correo usado para envío y recepción de respuestas en postulaciones automáticas.
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
                <label className="flex items-center gap-2 mb-2 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={sameReply}
                    onChange={(e) => {
                      const checked = e.target.checked;
                      setSameReply(checked);
                      if (checked) set("reply_email", form.notification_email);
                    }}
                    className="accent-blue-500 w-4 h-4"
                  />
                  <span className="text-xs text-gray-400">Usar el mismo correo de envío</span>
                </label>
                <input
                  type="email"
                  value={sameReply ? form.notification_email : form.reply_email}
                  onChange={(e) => set("reply_email", e.target.value)}
                  disabled={sameReply}
                  placeholder="respuesta@ejemplo.com"
                  className="w-full bg-gray-950 border border-gray-700 text-white rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-blue-500 placeholder-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
                />
              </div>
            </div>

            {/* Setup Gmail */}
            <div className="mt-6 border-t border-gray-800 pt-5">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Configurar envío con Gmail</p>
              <ol className="space-y-2 text-xs text-gray-500">
                <li><span className="text-gray-400 font-medium">1.</span> Ve a <a href="https://myaccount.google.com/apppasswords" target="_blank" rel="noreferrer" className="text-cyan-400 hover:underline">myaccount.google.com/apppasswords</a> y genera una contraseña de aplicación</li>
                <li><span className="text-gray-400 font-medium">2.</span> En el servidor, edita <code className="text-cyan-400 bg-gray-800 px-1.5 py-0.5 rounded">docker/.env</code> y agrega:</li>
                <li className="pl-4"><code className="text-cyan-400 bg-gray-800 px-2 py-1 rounded block mt-1">GMAIL_USER=tucorreo@gmail.com<br/>GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx</code></li>
                <li><span className="text-gray-400 font-medium">3.</span> Reinicia el scraper: <code className="text-cyan-400 bg-gray-800 px-1.5 py-0.5 rounded">docker compose up -d scraper</code></li>
              </ol>
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
