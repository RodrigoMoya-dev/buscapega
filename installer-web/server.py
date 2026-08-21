#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Buscapega — Servidor del instalador web
=======================================

Pequeño servicio HTTP (solo librería estándar de Python, sin dependencias) que
levanta el asistente de instalación estilo WordPress. Lo lanza `install.sh`:

    install.sh  (modo web, por defecto)
        └── detecta IP + genera token
        └── exec python3 installer-web/server.py
                 └── sirve el formulario en http://<IP>:<puerto>/?token=<token>
                 └── al enviar el formulario ejecuta:  install.sh --apply
                     pasándole las respuestas por variables de entorno, y
                     transmite su salida en vivo al navegador (SSE).

No reimplementa nada de la lógica de instalación: el trabajo real (generar
.env / settings.json, construir imágenes, levantar servicios) lo hace el propio
install.sh en modo --apply. Este servidor es solo la interfaz.
"""

import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# ── Configuración (viene de install.sh por variables de entorno) ──────────────
HERE = Path(__file__).resolve().parent
SCRIPT_DIR = Path(os.environ.get("BUSCAPEGA_SCRIPT_DIR", HERE.parent)).resolve()
INSTALL_SH = SCRIPT_DIR / "install.sh"
HOST = os.environ.get("BUSCAPEGA_WEB_HOST", "0.0.0.0")
PORT = int(os.environ.get("BUSCAPEGA_WEB_PORT", "8090"))
TOKEN = os.environ.get("BUSCAPEGA_WEB_TOKEN", "")
ENGINE = os.environ.get("BUSCAPEGA_ENGINE", "")          # motor ya detectado por install.sh (opcional)
ENGINE_LABEL = os.environ.get("BUSCAPEGA_ENGINE_LABEL", "")
LAN_IP = os.environ.get("BUSCAPEGA_LAN_IP", "")          # IP ya detectada por install.sh (opcional)

# Regex para limpiar códigos de color ANSI que emite install.sh: en el navegador
# se muestran como texto plano monoespaciado, así que las secuencias de escape
# solo ensuciarían la consola de logs.
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def detect_ip() -> str:
    """IP de la interfaz por la que sale el tráfico (sin enviar paquetes reales)."""
    if LAN_IP:
        return LAN_IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


# ── Estado global de la instalación (compartido entre hilos) ──────────────────
class InstallState:
    def __init__(self):
        self.lock = threading.Lock()
        self.status = "idle"          # idle | running | done | failed
        self.lines = []               # líneas de log acumuladas
        self.proc = None
        self.answers = {}             # respuestas usadas (para armar la URL final)
        self.exit_code = None

    def append(self, line):
        with self.lock:
            self.lines.append(line)

    def snapshot(self, from_index):
        with self.lock:
            return self.status, self.lines[from_index:], len(self.lines), self.exit_code


STATE = InstallState()


def run_install(answers: dict):
    """Ejecuta `install.sh --apply` pasando las respuestas por entorno y
    volcando su salida (stdout+stderr) al buffer de logs en vivo."""
    env = os.environ.copy()
    env["BUSCAPEGA_USER_NAME"] = answers.get("user_name", "")
    env["BUSCAPEGA_ANTHROPIC_API_KEY"] = answers.get("anthropic_api_key", "")
    env["BUSCAPEGA_WHATSAPP_PHONE"] = answers.get("whatsapp_phone", "")
    env["BUSCAPEGA_GMAIL_USER"] = answers.get("gmail_user", "")
    env["BUSCAPEGA_GMAIL_APP_PASSWORD"] = answers.get("gmail_app_password", "")
    env["BUSCAPEGA_FRONTEND_PORT"] = str(answers.get("frontend_port", "3000"))
    env["BUSCAPEGA_BACKEND_PORT"] = str(answers.get("backend_port", "8000"))
    if answers.get("engine"):
        env["ENGINE"] = answers["engine"]
    # Fuerza salida sin buffering en Python hijo y desactiva color donde se pueda.
    env["PYTHONUNBUFFERED"] = "1"

    try:
        proc = subprocess.Popen(
            ["bash", str(INSTALL_SH), "--apply"],
            cwd=str(SCRIPT_DIR),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except Exception as exc:  # noqa: BLE001
        STATE.append("✗ No se pudo iniciar install.sh: %s" % exc)
        with STATE.lock:
            STATE.status = "failed"
            STATE.exit_code = -1
        return

    with STATE.lock:
        STATE.proc = proc

    for raw in proc.stdout:
        STATE.append(strip_ansi(raw.rstrip("\n")))

    proc.wait()
    with STATE.lock:
        STATE.exit_code = proc.returncode
        STATE.status = "done" if proc.returncode == 0 else "failed"


# ── Servidor HTTP ─────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    server_version = "BuscapegaInstaller/1.0"

    # Silencia el log por defecto (una línea por request ensucia la terminal).
    def log_message(self, fmt, *args):  # noqa: A003
        pass

    # --- helpers ---
    def _token_ok(self):
        if not TOKEN:
            return True
        q = parse_qs(urlparse(self.path).query)
        if q.get("token", [""])[0] == TOKEN:
            return True
        if self.headers.get("X-Install-Token", "") == TOKEN:
            return True
        return False

    def _send(self, code, body, content_type="text/html; charset=utf-8", extra=None):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _send_json(self, code, obj):
        self._send(code, json.dumps(obj), "application/json; charset=utf-8")

    def _serve_file(self, name, content_type):
        path = HERE / name
        try:
            data = path.read_bytes()
        except FileNotFoundError:
            self._send(404, "no encontrado")
            return
        self._send(200, data, content_type)

    # --- GET ---
    def do_GET(self):
        route = urlparse(self.path).path

        # Los assets estáticos no exigen token (no filtran nada sensible).
        if route == "/assets/app.js":
            return self._serve_file("app.js", "application/javascript; charset=utf-8")
        if route == "/assets/style.css":
            return self._serve_file("style.css", "text/css; charset=utf-8")

        if not self._token_ok():
            return self._send(403, "<h1>403</h1><p>Token inválido o ausente. "
                              "Usa el enlace exacto que imprimió el instalador en la terminal.</p>")

        if route == "/":
            return self._serve_file("index.html", "text/html; charset=utf-8")

        if route == "/api/info":
            return self._send_json(200, {
                "ip": detect_ip(),
                "engine": ENGINE,
                "engine_label": ENGINE_LABEL or (ENGINE.capitalize() if ENGINE else ""),
                "status": STATE.status,
            })

        if route == "/api/stream":
            return self._stream_logs()

        return self._send(404, "no encontrado")

    # --- POST ---
    def do_POST(self):
        route = urlparse(self.path).path
        if not self._token_ok():
            return self._send_json(403, {"error": "token inválido"})

        if route == "/api/install":
            return self._start_install()

        if route == "/api/shutdown":
            self._send_json(200, {"ok": True})
            threading.Thread(target=self._shutdown_soon, daemon=True).start()
            return

        return self._send_json(404, {"error": "ruta desconocida"})

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return {}

    def _start_install(self):
        with STATE.lock:
            if STATE.status == "running":
                return self._send_json(409, {"error": "ya hay una instalación en curso"})
            STATE.status = "running"
            STATE.lines = []
            STATE.exit_code = None

        answers = self._read_json_body()
        STATE.answers = answers
        threading.Thread(target=run_install, args=(answers,), daemon=True).start()
        return self._send_json(200, {"ok": True})

    def _stream_logs(self):
        """Server-Sent Events: envía las líneas nuevas de log y el estado."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        idx = 0
        try:
            while True:
                status, new_lines, total, code = STATE.snapshot(idx)
                idx = total
                for line in new_lines:
                    payload = json.dumps({"line": line})
                    self.wfile.write(("event: log\ndata: %s\n\n" % payload).encode("utf-8"))
                if status in ("done", "failed"):
                    final_url = ""
                    if status == "done":
                        port = STATE.answers.get("frontend_port", "3000")
                        final_url = "http://%s:%s" % (detect_ip(), port)
                    payload = json.dumps({"status": status, "url": final_url, "code": code})
                    self.wfile.write(("event: end\ndata: %s\n\n" % payload).encode("utf-8"))
                    self.wfile.flush()
                    break
                # Comentario keep-alive para que el proxy/navegador no corte la conexión.
                self.wfile.write(b": keep-alive\n\n")
                self.wfile.flush()
                time.sleep(0.6)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _shutdown_soon(self):
        time.sleep(1.0)
        os._exit(0)


def main():
    if not INSTALL_SH.exists():
        print("ERROR: no encontré install.sh en %s" % SCRIPT_DIR, file=sys.stderr)
        sys.exit(1)

    ip = detect_ip()
    qs = ("?token=%s" % TOKEN) if TOKEN else ""
    url_local = "http://localhost:%s/%s" % (PORT, qs)
    url_lan = "http://%s:%s/%s" % (ip, PORT, qs)

    try:
        httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError as exc:
        print("ERROR: no pude abrir el puerto %s: %s" % (PORT, exc), file=sys.stderr)
        print("       Prueba otro puerto:  BUSCAPEGA_WEB_PORT=8099 ./install.sh", file=sys.stderr)
        sys.exit(1)

    # Banner en la terminal — es lo que el usuario copia en su navegador. Se ofrecen
    # dos enlaces para que sirva en cualquier escenario: quien instala en su propio
    # equipo usa el de localhost; quien instala en otra máquina (un servidor, otro PC)
    # y entra desde su navegador usa el de la IP.
    print("")
    print("  ╔══════════════════════════════════════════════════════════════╗")
    print("  ║   Instalador web de Buscapega en marcha                       ║")
    print("  ╚══════════════════════════════════════════════════════════════╝")
    print("")
    print("  Abre una de estas URL en tu navegador:")
    print("")
    print("    • En este mismo equipo:   %s" % url_local)
    if ip not in ("127.0.0.1", "localhost"):
        print("    • Desde otro equipo:      %s" % url_lan)
    print("")
    print("  El token protege el acceso: solo quien tenga este enlace puede entrar.")
    print("  Para detener el instalador: Ctrl-C aquí.")
    print("")
    sys.stdout.flush()   # asegura que el banner (y las URL) se vean aunque stdout esté bufferizado

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Instalador web detenido.")
        httpd.shutdown()


if __name__ == "__main__":
    main()
