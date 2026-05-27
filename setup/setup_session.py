#!/usr/bin/env python3
"""
Wunen — Setup de sesión por portal

Uso:
    python3 setup_session.py <portal>
    python3 setup_session.py <portal> --browser brave|chrome
    python3 setup_session.py --lista

Portales disponibles: findjobit, getonbrd, tecnoempleo, remotelatinos, chiletrabajos, chumiit

El script abre el navegador elegido con un perfil persistente real, navegas al
portal, haces login con Google, y las cookies quedan guardadas y sincronizadas
con Presto automáticamente.
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright

from portales_config import PORTALES

COOKIES_DIR = Path(__file__).parent / "cookies"
PROFILES_DIR = Path(__file__).parent / "profiles"
PRESTO_COOKIES_PATH = "rodrigo@presto:~/docker/wunen/cookies/"
TIMEOUT_LOGIN = 5 * 60 * 1000  # 5 minutos para completar el login

BROWSERS = {
    "chrome": {"channel": "chrome", "exe": None},
    "brave":  {"channel": None,     "exe": "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"},
}

# Flags que ocultan las señales de automatización a Google OAuth
STEALTH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--start-maximized",
]


def listar_portales():
    print("\nPortales disponibles:\n")
    for key, config in PORTALES.items():
        session_file = COOKIES_DIR / f"{key}_session.json"
        if session_file.exists():
            mtime = datetime.fromtimestamp(session_file.stat().st_mtime)
            estado = f"✅ Sesión guardada ({mtime.strftime('%d/%m/%Y %H:%M')})"
        else:
            estado = "❌ Sin sesión"
        print(f"  {key:<15} {config['nombre']:<20} {estado}")
    print()


def sincronizar_con_presto(portal: str):
    session_file = COOKIES_DIR / f"{portal}_session.json"
    print(f"\n📡 Sincronizando con Presto...")
    result = subprocess.run(
        ["rsync", "-av", str(session_file), PRESTO_COOKIES_PATH],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("✅ Cookies sincronizadas con Presto correctamente.")
    else:
        print(f"⚠️  Error al sincronizar: {result.stderr}")
        print(f"   Puedes hacerlo manualmente:\n   rsync -av {session_file} {PRESTO_COOKIES_PATH}")


def setup_portal(portal: str, browser_name: str = "chrome"):
    if portal not in PORTALES:
        print(f"❌ Portal '{portal}' no reconocido.")
        listar_portales()
        sys.exit(1)

    if browser_name not in BROWSERS:
        print(f"❌ Navegador '{browser_name}' no válido. Opciones: {', '.join(BROWSERS)}")
        sys.exit(1)

    config = PORTALES[portal]
    COOKIES_DIR.mkdir(exist_ok=True)
    PROFILES_DIR.mkdir(exist_ok=True)
    session_file = COOKIES_DIR / f"{portal}_session.json"

    # Directorio de perfil persistente — uno por navegador, compartido entre portales
    # para que el login de Google ya esté hecho en sesiones posteriores.
    profile_dir = PROFILES_DIR / browser_name

    print(f"""
╔══════════════════════════════════════════════════════╗
║  Wunen — Setup sesión: {config['nombre']:<30}║
╚══════════════════════════════════════════════════════╝

Navegador: {browser_name}  (Vivaldi no es compatible con Playwright)

Se abrirá el navegador. Sigue estos pasos:

  1. Haz click en "Sign in with Google" (o el botón de login)
  2. Completa el login con tu cuenta de Google
  3. Espera a que el portal cargue tu perfil
  4. El script detectará el login y cerrará el navegador solo

Tienes 5 minutos para completar el proceso.
""")

    input("Presiona Enter para abrir el navegador...")

    browser_cfg = BROWSERS[browser_name]

    with sync_playwright() as p:
        # launch_persistent_context usa un perfil real del sistema operativo.
        # Google acepta el login porque el navegador tiene historial, cookies
        # previas y no aparece como perfil vacío automatizado.
        launch_kwargs = {
            "headless": False,
            "args": STEALTH_ARGS,
        }
        if browser_cfg["channel"]:
            launch_kwargs["channel"] = browser_cfg["channel"]
        if browser_cfg["exe"]:
            launch_kwargs["executable_path"] = browser_cfg["exe"]

        context = p.chromium.launch_persistent_context(
            str(profile_dir),
            **launch_kwargs,
        )

        page = context.new_page()
        page.goto(config["login_url"], wait_until="domcontentloaded")

        print(f"\n🌐 Navegando a {config['login_url']}")
        print("⏳ Esperando que completes el login...\n")

        login_detectado = False
        login_url_base = config["login_url"].rstrip("/")

        # Estrategia 1: ya logueado — la página redirigió fuera del login de inmediato
        page.wait_for_load_state("domcontentloaded")
        if not page.url.rstrip("/").startswith(login_url_base):
            print(f"ℹ️  Ya había sesión activa (redirigido a {page.url})")
            login_detectado = True

        if not login_detectado:
            try:
                # Estrategia 2: esperar redirección a URL de éxito tras hacer login
                page.wait_for_url(
                    f"**{config['login_exitoso_url']}**",
                    timeout=TIMEOUT_LOGIN
                )
                login_detectado = True
            except Exception:
                pass

        if not login_detectado:
            try:
                # Estrategia 3: esperar elemento que solo aparece logueado
                page.wait_for_selector(
                    config["login_exitoso_selector"],
                    timeout=30_000
                )
                login_detectado = True
            except Exception:
                pass

        if not login_detectado:
            # Estrategia 4: confirmar manual
            print("⚠️  No detecté el login automáticamente.")
            respuesta = input("¿Completaste el login exitosamente? (s/n): ").strip().lower()
            login_detectado = respuesta == "s"

        if not login_detectado:
            print("❌ Login no completado. Sesión no guardada.")
            context.close()
            return

        # Exportar cookies + localStorage al formato que usa el scraper
        context.storage_state(path=str(session_file))
        context.close()

        with open(session_file) as f:
            data = json.load(f)
        n_cookies = len(data.get("cookies", []))
        print(f"\n✅ Sesión guardada: {session_file.name}")
        print(f"   {n_cookies} cookies almacenadas")

        sincronizar_con_presto(portal)

        print(f"""
╔══════════════════════════════════════════════════════╗
║  ✅ Setup completado para {config['nombre']:<26}║
╚══════════════════════════════════════════════════════╝

La sesión está lista en Presto. Wunen puede ahora
postular automáticamente en {config['nombre']}.

Recuerda renovar la sesión si ves errores de login
(normalmente cada 30-90 días).
""")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] in ("--lista", "-l", "lista"):
        listar_portales()
        sys.exit(0)

    portal = args[0].lower().strip()

    browser_name = "chrome"
    if "--browser" in args:
        idx = args.index("--browser")
        if idx + 1 < len(args):
            browser_name = args[idx + 1].lower().strip()
        else:
            print("❌ Falta el nombre del navegador después de --browser")
            sys.exit(1)

    setup_portal(portal, browser_name)
