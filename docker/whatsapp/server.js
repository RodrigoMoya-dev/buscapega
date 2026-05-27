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
import qrcode from "qrcode-terminal";
import { existsSync, mkdirSync } from "fs";

// ── Configuración ─────────────────────────────────────────────────────────────
const PORT = process.env.PORT || 3001;
const AUTH_DIR = process.env.AUTH_DIR || "/app/auth";
const DEFAULT_PHONE = process.env.DEFAULT_PHONE || "56962075019";

// ── Logger ────────────────────────────────────────────────────────────────────
const logger = pino({ level: "silent" });

// ── Estado global ─────────────────────────────────────────────────────────────
let sock = null;
let isConnected = false;
let connectionStatus = "disconnected";

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
    // Forzar QR (no pairing por número)
    printQRInTerminal: false,
  });

  sock.ev.on("creds.update", saveCreds);

  sock.ev.on("connection.update", async (update) => {
    const { connection, lastDisconnect, qr } = update;

    // ── Mostrar QR en consola ─────────────────────────────────────────────
    if (qr) {
      console.log("\n╔══════════════════════════════════════════════════════╗");
      console.log("║         ESCANEA EL QR CON WHATSAPP                  ║");
      console.log("║  WhatsApp → ⋮ → Dispositivos vinculados → Vincular  ║");
      console.log("╚══════════════════════════════════════════════════════╝\n");
      qrcode.generate(qr, { small: true });
      console.log("\n(El QR expira en ~60 segundos, se regenerará automáticamente)\n");
      connectionStatus = "waiting_qr";
    }

    if (connection === "close") {
      const reason = new Boom(lastDisconnect?.error)?.output?.statusCode;
      isConnected = false;
      connectionStatus = "disconnected";
      console.log(`[WhatsApp] Conexión cerrada. Código: ${reason}`);

      if (reason === DisconnectReason.loggedOut) {
        console.log("[WhatsApp] Sesión cerrada. Borra el volumen whatsapp_auth y reinicia.");
        connectionStatus = "logged_out";
      } else {
        console.log("[WhatsApp] Reconectando en 3 segundos...");
        setTimeout(connectToWhatsApp, 3000);
      }
    } else if (connection === "open") {
      console.log("\n[WhatsApp] ✅ ¡Conectado exitosamente!\n");
      isConnected = true;
      connectionStatus = "connected";
    } else if (connection === "connecting") {
      connectionStatus = "connecting";
    }
  });
}

// ── Express API ───────────────────────────────────────────────────────────────
const app = express();
app.use(express.json());

app.get("/health", (_req, res) => {
  res.json({ status: isConnected ? "ok" : "unavailable", connection: connectionStatus, service: "whatsapp" });
});

app.post("/send", async (req, res) => {
  if (!isConnected || !sock) {
    return res.status(503).json({ ok: false, error: "WhatsApp no conectado", status: connectionStatus });
  }
  const { message, to } = req.body;
  if (!message) return res.status(400).json({ ok: false, error: "Falta 'message'" });

  const jid = `${(to || DEFAULT_PHONE).replace(/[^0-9]/g, "")}@s.whatsapp.net`;
  try {
    await sock.sendMessage(jid, { text: message });
    console.log(`[WhatsApp] ✅ → ${jid}: ${message.substring(0, 60)}`);
    res.json({ ok: true, to: jid });
  } catch (err) {
    console.error(`[WhatsApp] ❌ Error:`, err.message);
    res.status(500).json({ ok: false, error: err.message });
  }
});

app.post("/send-bulk", async (req, res) => {
  const items = Array.isArray(req.body) ? req.body : [req.body];
  const results = [];
  for (const item of items) {
    if (!isConnected || !sock) { results.push({ ok: false, error: "No conectado" }); continue; }
    const jid = `${(item.to || DEFAULT_PHONE).replace(/[^0-9]/g, "")}@s.whatsapp.net`;
    try {
      await sock.sendMessage(jid, { text: item.message });
      results.push({ ok: true, to: jid });
      await new Promise((r) => setTimeout(r, 500));
    } catch (err) {
      results.push({ ok: false, error: err.message });
    }
  }
  res.json({ results });
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`[WhatsApp] Servicio HTTP en http://0.0.0.0:${PORT}`);
  console.log(`[WhatsApp] AUTH_DIR: ${AUTH_DIR}`);
});

connectToWhatsApp().catch((err) => {
  console.error("[WhatsApp] Error crítico:", err);
  process.exit(1);
});
