import makeWASocket, {
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
  makeCacheableSignalKeyStore,
  Browsers,
} from "@whiskeysockets/baileys";
import { Boom } from "@hapi/boom";
import express from "express";
import pino from "pino";
import { existsSync, mkdirSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));

// ── Configuración ─────────────────────────────────────────────────────────────
const PORT = process.env.PORT || 3001;
const AUTH_DIR = process.env.AUTH_DIR || "/app/auth";
const DEFAULT_PHONE = process.env.DEFAULT_PHONE || "+56962075019";
const PAIRING_PHONE = process.env.PAIRING_PHONE || "56962075019"; // sin + para Baileys

// ── Logger ────────────────────────────────────────────────────────────────────
const logger = pino({ level: "silent" }); // silenciamos logs internos de Baileys

// ── Estado global ─────────────────────────────────────────────────────────────
let sock = null;
let isConnected = false;
let connectionStatus = "disconnected";

// ── Asegurar directorio de auth ───────────────────────────────────────────────
if (!existsSync(AUTH_DIR)) {
  mkdirSync(AUTH_DIR, { recursive: true });
}

// ── Conexión WhatsApp ─────────────────────────────────────────────────────────
async function connectToWhatsApp() {
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
  const { version } = await fetchLatestBaileysVersion();

  console.log(`[WhatsApp] Usando Baileys v${version.join(".")}`);
  connectionStatus = "connecting";

  sock = makeWASocket({
    version,
    logger,
    auth: {
      creds: state.creds,
      keys: makeCacheableSignalKeyStore(state.keys, logger),
    },
    browser: Browsers.ubuntu("Chrome"),
    generateHighQualityLinkPreview: false,
    syncFullHistory: false,
  });

  // ── Pairing con número de teléfono (alternativa al QR) ──────────────────
  if (!sock.authState.creds.registered) {
    console.log("[WhatsApp] No hay sesión guardada. Iniciando pairing por código...");
    connectionStatus = "waiting_pairing";

    // Esperar que se establezca la conexión antes de pedir código
    await new Promise((resolve) => setTimeout(resolve, 3000));

    try {
      const code = await sock.requestPairingCode(PAIRING_PHONE);
      console.log("╔════════════════════════════════════════╗");
      console.log("║   CÓDIGO DE VINCULACIÓN WHATSAPP       ║");
      console.log(`║   Código: ${code.match(/.{1,4}/g).join("-").padEnd(30)}║`);
      console.log("╠════════════════════════════════════════╣");
      console.log("║  1. Abre WhatsApp en tu teléfono       ║");
      console.log("║  2. Dispositivos vinculados             ║");
      console.log("║  3. Vincular un dispositivo             ║");
      console.log("║  4. Ingresa el código de 8 dígitos     ║");
      console.log("╚════════════════════════════════════════╝");
    } catch (err) {
      console.error("[WhatsApp] Error al solicitar código de pairing:", err.message);
    }
  }

  // ── Eventos ──────────────────────────────────────────────────────────────
  sock.ev.on("creds.update", saveCreds);

  sock.ev.on("connection.update", async (update) => {
    const { connection, lastDisconnect } = update;

    if (connection === "close") {
      const reason = new Boom(lastDisconnect?.error)?.output?.statusCode;
      console.log(`[WhatsApp] Conexión cerrada. Razón: ${reason}`);
      isConnected = false;
      connectionStatus = "disconnected";

      if (reason === DisconnectReason.loggedOut) {
        console.log("[WhatsApp] Sesión cerrada. Borra el directorio de auth y reinicia.");
        connectionStatus = "logged_out";
      } else {
        console.log("[WhatsApp] Reconectando en 5 segundos...");
        setTimeout(connectToWhatsApp, 5000);
      }
    } else if (connection === "open") {
      console.log("[WhatsApp] ✅ Conectado exitosamente");
      isConnected = true;
      connectionStatus = "connected";
    } else if (connection === "connecting") {
      console.log("[WhatsApp] Conectando...");
      connectionStatus = "connecting";
    }
  });
}

// ── Express API ───────────────────────────────────────────────────────────────
const app = express();
app.use(express.json());

/**
 * GET /health
 * Verifica el estado del servicio
 */
app.get("/health", (req, res) => {
  res.json({
    status: isConnected ? "ok" : "unavailable",
    connection: connectionStatus,
    service: "whatsapp",
  });
});

/**
 * POST /send
 * Envía un mensaje de WhatsApp
 * Body: { message: string, to?: string }
 */
app.post("/send", async (req, res) => {
  if (!isConnected || !sock) {
    return res.status(503).json({
      ok: false,
      error: "WhatsApp no está conectado",
      status: connectionStatus,
    });
  }

  const { message, to } = req.body;

  if (!message) {
    return res.status(400).json({ ok: false, error: "Falta el campo 'message'" });
  }

  // Normalizar número: quitar el + y agregar @s.whatsapp.net
  const rawPhone = (to || DEFAULT_PHONE).replace(/[^0-9]/g, "");
  const jid = `${rawPhone}@s.whatsapp.net`;

  try {
    await sock.sendMessage(jid, { text: message });
    console.log(`[WhatsApp] ✅ Mensaje enviado a ${rawPhone}: ${message.substring(0, 50)}...`);
    res.json({ ok: true, to: rawPhone });
  } catch (err) {
    console.error(`[WhatsApp] ❌ Error al enviar a ${rawPhone}:`, err.message);
    res.status(500).json({ ok: false, error: err.message });
  }
});

/**
 * POST /send-bulk
 * Envía múltiples mensajes
 * Body: [{ message: string, to?: string }, ...]
 */
app.post("/send-bulk", async (req, res) => {
  const items = Array.isArray(req.body) ? req.body : [req.body];
  const results = [];

  for (const item of items) {
    if (!isConnected || !sock) {
      results.push({ ok: false, error: "No conectado" });
      continue;
    }
    const rawPhone = (item.to || DEFAULT_PHONE).replace(/[^0-9]/g, "");
    const jid = `${rawPhone}@s.whatsapp.net`;
    try {
      await sock.sendMessage(jid, { text: item.message });
      results.push({ ok: true, to: rawPhone });
      // Pequeña pausa para no spamear
      await new Promise((r) => setTimeout(r, 500));
    } catch (err) {
      results.push({ ok: false, error: err.message });
    }
  }

  res.json({ results });
});

// ── Arranque ──────────────────────────────────────────────────────────────────
app.listen(PORT, "0.0.0.0", () => {
  console.log(`[WhatsApp] Servicio escuchando en http://0.0.0.0:${PORT}`);
});

connectToWhatsApp().catch((err) => {
  console.error("[WhatsApp] Error crítico al conectar:", err);
  process.exit(1);
});
