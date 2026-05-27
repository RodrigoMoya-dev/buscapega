const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");
const express = require("express");

// ── Configuración ─────────────────────────────────────────────────────────────
const PORT = process.env.PORT || 3001;
const AUTH_DIR = process.env.AUTH_DIR || "/app/auth";
const DEFAULT_PHONE = (process.env.DEFAULT_PHONE || "56962075019").replace(/[^0-9]/g, "");

// ── Estado ────────────────────────────────────────────────────────────────────
let isConnected = false;
let connectionStatus = "initializing";
let waClient = null;

// ── Cliente WhatsApp ──────────────────────────────────────────────────────────
function createClient() {
  const client = new Client({
    authStrategy: new LocalAuth({ dataPath: AUTH_DIR }),
    puppeteer: {
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
      ],
    },
  });

  client.on("qr", (qr) => {
    connectionStatus = "waiting_qr";
    console.log("\n╔══════════════════════════════════════════════════════╗");
    console.log("║         ESCANEA EL QR CON WHATSAPP                  ║");
    console.log("║  WhatsApp → ⋮ → Dispositivos vinculados → Vincular  ║");
    console.log("╚══════════════════════════════════════════════════════╝\n");
    qrcode.generate(qr, { small: true });
    console.log("\n(El QR expira en ~20 segundos, se regenerará solo)\n");
  });

  client.on("authenticated", () => {
    console.log("[WhatsApp] ✅ Autenticado — guardando sesión...");
    connectionStatus = "authenticated";
  });

  client.on("ready", () => {
    console.log("[WhatsApp] ✅ ¡Listo y conectado!");
    isConnected = true;
    connectionStatus = "connected";
  });

  client.on("auth_failure", (msg) => {
    console.error("[WhatsApp] ❌ Fallo de autenticación:", msg);
    connectionStatus = "auth_failed";
    isConnected = false;
    // Reintentar en 10 segundos
    setTimeout(() => {
      console.log("[WhatsApp] Reiniciando cliente...");
      waClient = createClient();
      waClient.initialize();
    }, 10000);
  });

  client.on("disconnected", (reason) => {
    console.log("[WhatsApp] Desconectado:", reason);
    isConnected = false;
    connectionStatus = "disconnected";
    // Reintentar en 5 segundos
    setTimeout(() => {
      console.log("[WhatsApp] Reconectando...");
      waClient = createClient();
      waClient.initialize();
    }, 5000);
  });

  return client;
}

// ── Arrancar cliente ──────────────────────────────────────────────────────────
console.log("[WhatsApp] Iniciando whatsapp-web.js...");
waClient = createClient();
waClient.initialize();

// ── API HTTP ──────────────────────────────────────────────────────────────────
const app = express();
app.use(express.json());

app.get("/health", (_req, res) => {
  res.json({
    status: isConnected ? "ok" : "unavailable",
    connection: connectionStatus,
    service: "whatsapp",
  });
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
