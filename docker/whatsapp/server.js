const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");
const QRCode = require("qrcode");
const express = require("express");

// ── Configuración ─────────────────────────────────────────────────────────────
const PORT = process.env.PORT || 3001;
const AUTH_DIR = process.env.AUTH_DIR || "/app/auth";
const DEFAULT_PHONE = (process.env.DEFAULT_PHONE || "56962075019").replace(/[^0-9]/g, "");

const RECONNECT_DELAY_MS = 15000;   // esperar 15s antes de reconectar
const MAX_RECONNECT_RETRIES = 5;    // máximo reintentos antes de rendirse

// ── Estado ────────────────────────────────────────────────────────────────────
let isConnected = false;
let connectionStatus = "initializing";
let waClient = null;
let reconnectAttempts = 0;
let reconnectTimer = null;
let lastQrData = null;  // QR data para endpoint /qr

// ── Puppeteer args (sin sandbox, bajo uso de memoria) ─────────────────────────
const PUPPETEER_OPTS = {
  headless: true,
  executablePath: process.env.CHROME_PATH || "/usr/bin/chromium",
  args: [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-accelerated-2d-canvas",
    "--no-first-run",
    "--no-zygote",
    "--disable-gpu",
    "--disable-extensions",
    "--disable-background-networking",
    "--disable-sync",
    "--metrics-recording-only",
    "--mute-audio",
    "--safebrowsing-disable-auto-update",
    "--single-process",   // reduce memory footprint en contenedores
  ],
  timeout: 60000,  // 60s para que Chromium arranque (puede ser lento con poca RAM)
};

// ── Función de reconexión con backoff ─────────────────────────────────────────
function scheduleReconnect(reason) {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }

  reconnectAttempts++;
  if (reconnectAttempts > MAX_RECONNECT_RETRIES) {
    console.error(`[WhatsApp] ❌ Se alcanzó el máximo de ${MAX_RECONNECT_RETRIES} reintentos. El contenedor se reiniciará.`);
    process.exit(1);  // Docker reinicia el contenedor → empieza desde cero
  }

  const delay = RECONNECT_DELAY_MS * reconnectAttempts;
  console.log(`[WhatsApp] Reintento ${reconnectAttempts}/${MAX_RECONNECT_RETRIES} en ${delay / 1000}s (motivo: ${reason})`);

  reconnectTimer = setTimeout(async () => {
    reconnectTimer = null;
    if (waClient) {
      try {
        await waClient.destroy();
      } catch (_) {}
      waClient = null;
    }
    startClient();
  }, delay);
}

// ── Crear e inicializar el cliente ────────────────────────────────────────────
async function startClient() {
  console.log("[WhatsApp] Iniciando cliente...");
  connectionStatus = "initializing";

  const client = new Client({
    authStrategy: new LocalAuth({ dataPath: AUTH_DIR }),
    puppeteer: PUPPETEER_OPTS,
  });

  client.on("qr", (qr) => {
    connectionStatus = "waiting_qr";
    reconnectAttempts = 0;  // reset: el QR es señal de vida del browser
    lastQrData = qr;
    console.log("\n╔══════════════════════════════════════════════════════╗");
    console.log("║         ESCANEA EL QR CON WHATSAPP                  ║");
    console.log(`║  Abre http://presto.local:3002/qr en el navegador   ║`);
    console.log("║  WhatsApp → ⋮ → Dispositivos vinculados → Vincular  ║");
    console.log("╚══════════════════════════════════════════════════════╝\n");
    qrcode.generate(qr, { small: true });
    console.log("\n(El QR expira en ~20 segundos, se regenerará solo)\n");
  });

  client.on("authenticated", () => {
    console.log("[WhatsApp] ✅ Autenticado — guardando sesión...");
    connectionStatus = "authenticated";
    reconnectAttempts = 0;
  });

  client.on("ready", () => {
    console.log("[WhatsApp] ✅ ¡Listo y conectado!");
    isConnected = true;
    connectionStatus = "connected";
    reconnectAttempts = 0;
    lastQrData = null;  // ya no necesitamos el QR
  });

  client.on("auth_failure", (msg) => {
    console.error("[WhatsApp] ❌ Fallo de autenticación:", msg);
    connectionStatus = "auth_failed";
    isConnected = false;
    scheduleReconnect("auth_failure");
  });

  client.on("disconnected", (reason) => {
    console.log("[WhatsApp] Desconectado:", reason);
    isConnected = false;
    connectionStatus = "disconnected";
    scheduleReconnect(reason);
  });

  waClient = client;

  try {
    await client.initialize();
  } catch (err) {
    console.error("[WhatsApp] ❌ Error al inicializar:", err.message || err);
    isConnected = false;
    waClient = null;
    scheduleReconnect(err.message || "init_error");
  }
}

// ── Capturar errores no manejados para evitar crash del proceso ───────────────
process.on("unhandledRejection", (reason) => {
  console.error("[WhatsApp] Unhandled rejection:", reason?.message || reason);
  // No terminar el proceso — dejar que el ciclo de reconexión maneje
});
process.on("uncaughtException", (err) => {
  console.error("[WhatsApp] Uncaught exception:", err.message);
  // No terminar el proceso — dejar que el ciclo de reconexión maneje
});

// ── Arrancar ──────────────────────────────────────────────────────────────────
console.log("[WhatsApp] Iniciando whatsapp-web.js...");
startClient();

// ── API HTTP ──────────────────────────────────────────────────────────────────
const app = express();
app.use(express.json());

app.get("/health", (_req, res) => {
  res.json({
    status: isConnected ? "ok" : "unavailable",
    connection: connectionStatus,
    reconnect_attempts: reconnectAttempts,
    service: "whatsapp",
  });
});

/**
 * GET /qr
 * Devuelve el QR actual como imagen PNG o página HTML con auto-refresh.
 * Útil para escanear desde el navegador cuando el terminal no es suficiente.
 */
app.get("/qr", async (_req, res) => {
  if (isConnected) {
    return res.send(`<html><body style="font-family:sans-serif;text-align:center;padding:40px">
      <h2>✅ WhatsApp ya está conectado</h2>
      <p>No es necesario escanear el QR.</p>
    </body></html>`);
  }
  if (!lastQrData) {
    return res.send(`<html><meta http-equiv="refresh" content="3"><body style="font-family:sans-serif;text-align:center;padding:40px">
      <h2>⏳ Esperando QR...</h2>
      <p>Estado: ${connectionStatus}. Esta página se recarga sola.</p>
    </body></html>`);
  }
  try {
    const qrDataUrl = await QRCode.toDataURL(lastQrData, { width: 300, margin: 2 });
    res.send(`<html>
    <head>
      <meta http-equiv="refresh" content="20">
      <style>body{font-family:sans-serif;text-align:center;padding:40px;background:#fff}</style>
    </head>
    <body>
      <h2>📱 Escanea con WhatsApp</h2>
      <p>WhatsApp → ⋮ → <strong>Dispositivos vinculados</strong> → Vincular dispositivo</p>
      <img src="${qrDataUrl}" style="border:2px solid #25D366;border-radius:8px;padding:10px" />
      <p style="color:#666;font-size:12px">El QR expira en ~20 segundos. Esta página se recarga automáticamente.</p>
    </body>
    </html>`);
  } catch (err) {
    res.status(500).send("Error generando QR: " + err.message);
  }
});

/**
 * POST /send
 * Body: { message: string, to?: string }
 */
app.post("/send", async (req, res) => {
  if (!isConnected || !waClient) {
    return res.status(503).json({
      ok: false,
      error: "WhatsApp no está conectado",
      status: connectionStatus,
    });
  }

  const { message, to } = req.body;
  if (!message) return res.status(400).json({ ok: false, error: "Falta 'message'" });

  const phone = (to || DEFAULT_PHONE).replace(/[^0-9]/g, "");
  const chatId = `${phone}@c.us`;

  try {
    await waClient.sendMessage(chatId, message);
    console.log(`[WhatsApp] ✅ Enviado a ${phone}: ${message.substring(0, 60)}`);
    res.json({ ok: true, to: phone });
  } catch (err) {
    console.error(`[WhatsApp] ❌ Error al enviar:`, err.message);
    res.status(500).json({ ok: false, error: err.message });
  }
});

/**
 * POST /send-bulk
 * Body: [{ message, to? }, ...]
 */
app.post("/send-bulk", async (req, res) => {
  const items = Array.isArray(req.body) ? req.body : [req.body];
  const results = [];

  for (const item of items) {
    if (!isConnected || !waClient) {
      results.push({ ok: false, error: "No conectado" });
      continue;
    }
    const phone = (item.to || DEFAULT_PHONE).replace(/[^0-9]/g, "");
    try {
      await waClient.sendMessage(`${phone}@c.us`, item.message);
      results.push({ ok: true, to: phone });
      await new Promise((r) => setTimeout(r, 500));
    } catch (err) {
      results.push({ ok: false, error: err.message });
    }
  }

  res.json({ results });
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`[WhatsApp] API HTTP escuchando en http://0.0.0.0:${PORT}`);
});
