#!/usr/bin/env python3
"""
Buscapega — Setup de sesión por portal

Uso:
    python3 setup_session.py <portal>
    python3 setup_session.py <portal> --browser brave|chrome
    python3 setup_session.py <portal> --real-chrome    # usa el perfil real de Chrome (útil para Google OAuth)
    python3 setup_session.py --lista

Portales disponibles: findjobit, getonbrd, tecnoempleo, remotelatinos, chiletrabajos, chumiit

El script abre el navegador elegido con un perfil persistente real, navegas al
portal, haces login con Google, y las cookies quedan guardadas localmente y
disponibles para el contenedor local de Buscapega automáticamente.

--real-chrome: usa el perfil real de Chrome del sistema (~/.../Chrome/Default).
  Requiere cerrar Chrome antes de ejecutar. Útil cuando el portal usa Google OAuth
  y en el perfil vacío de Playwright Google no completa el login.

--presto: (uso interno del desarrollador) además sincroniza las cookies al
  servidor Presto vía rsync. NO usar en instalaciones locales: Buscapega funciona
  100% local en el equipo de quien lo instala.
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
TIMEOUT_LOGIN = 5 * 60 * 1000  # 5 minutos para completar el login

# Contenedor local del scraper (definido en docker/docker-compose.yml). Su
# volumen playwright_cookies está montado en /app/cookies con permiso de escritura.
SCRAPER_CONTAINER = "buscapega_scraper"
SCRAPER_COOKIES_DIR = "/app/cookies"

# Sincronización opcional al servidor Presto (uso interno del desarrollador).
# NO se usa en instalaciones locales: Buscapega funciona 100% local.
PRESTO_COOKIES_PATH = "rodrigo@presto:~/docker/buscapega/cookies/"

BROWSERS = {
    "chrome": {"channel": "chrome", "exe": None},
    "brave":  {"channel": None,     "exe": "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"},
}

# Perfil real de Chrome en macOS — tiene la sesión de Google activa
REAL_CHROME_PROFILE = Path.home() / "Library/Application Support/Google/Chrome/Default"

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


def sincronizar_local(portal: str):
    """Copia la sesión al volumen del contenedor scraper local.

    Buscapega funciona 100% en el equipo de quien lo instala: las cookies deben
    quedar en el volumen `playwright_cookies` que lee el scraper, no en ningún
    servidor remoto. Si el contenedor no está corriendo, deja la sesión guardada
    localmente e indica el comando manual para copiarla cuando levante.
    """
    session_file = COOKIES_DIR / f"{portal}_session.json"
    print("\n📦 Cargando la sesión en el contenedor local de Buscapega...")
    result = subprocess.run(
        ["docker", "cp", str(session_file), f"{SCRAPER_CONTAINER}:{SCRAPER_COOKIES_DIR}/"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("✅ Sesión disponible para Buscapega. Ya puede postular automáticamente con ella.")
    else:
        print("ℹ️  No se pudo copiar al contenedor (¿está Buscapega corriendo?).")
        print(f"   La sesión quedó guardada en: {session_file}")
        print("   Cuando los servicios estén arriba, cópiala con:")
        print(f"   docker cp {session_file} {SCRAPER_CONTAINER}:{SCRAPER_COOKIES_DIR}/")


def sincronizar_con_presto(portal: str):
    """Sincroniza las cookies al servidor Presto (uso interno del desarrollador)."""
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


def _finalizar_guardado(session_file: Path, portal: str, config: dict):
    """Imprime resumen de cookies guardadas."""
    with open(session_file) as f:
        data = json.load(f)
    cookies = data.get("cookies", [])
    home = config.get("home_url", "").replace("https://www.", "").replace("https://", "").split("/")[0]
    portal_cookies = [c for c in cookies
                      if portal.lower() in c.get("domain", "").lower()
                      or home in c.get("domain", "").lower()]
    print(f"\n✅ Sesión guardada: {session_file.name}")
    print(f"   {len(cookies)} cookies totales, {len(portal_cookies)} del portal")
    if not portal_cookies:
        print(f"\n⚠️  ADVERTENCIA: No se encontraron cookies del portal {config['nombre']}.")
        print(f"   Es posible que el login no se haya completado correctamente.")
        print(f"   Vuelve a ejecutar el setup y asegúrate de hacer login con tu cuenta.")
    print(f"""
╔══════════════════════════════════════════════════════╗
║  ✅ Setup completado para {config['nombre']:<26}║
╚══════════════════════════════════════════════════════╝

La sesión quedó guardada localmente. Buscapega puede ahora
postular automáticamente en {config['nombre']}.

Recuerda renovar la sesión si ves errores de login
(normalmente cada 30-90 días).
""")


def setup_portal(portal: str, browser_name: str = "chrome", use_real_chrome: bool = False,
                 sync_presto: bool = False):
    def sincronizar(p: str):
        # Por defecto, instalación local: copia al contenedor local.
        # Con --presto (uso interno del dev) además sincroniza al servidor remoto.
        sincronizar_local(p)
        if sync_presto:
            sincronizar_con_presto(p)

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

    if use_real_chrome:
        if not REAL_CHROME_PROFILE.exists():
            print(f"❌ No se encontró el perfil real de Chrome en:\n   {REAL_CHROME_PROFILE}")
            sys.exit(1)
        profile_dir = REAL_CHROME_PROFILE
        print(f"\n⚠️  IMPORTANTE: Cierra TODAS las ventanas de Chrome antes de continuar.")
        print(f"   Chrome no puede abrirse dos veces con el mismo perfil.\n")
        input("Presiona Enter cuando Chrome esté cerrado...")
    else:
        # Directorio de perfil persistente — uno por navegador, compartido entre portales
        # para que el login de Google ya esté hecho en sesiones posteriores.
        profile_dir = PROFILES_DIR / browser_name

    print(f"""
╔══════════════════════════════════════════════════════╗
║  Buscapega — Setup sesión: {config['nombre']:<30}║
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
        if use_real_chrome:
            # Con el perfil real usamos el ejecutable de Chrome directamente
            launch_kwargs["channel"] = "chrome"
        else:
            if browser_cfg["channel"]:
                launch_kwargs["channel"] = browser_cfg["channel"]
            if browser_cfg["exe"]:
                launch_kwargs["executable_path"] = browser_cfg["exe"]

        context = p.chromium.launch_persistent_context(
            str(profile_dir),
            **launch_kwargs,
        )

        page = context.new_page()

        # Con --real-chrome: intentar el home directamente primero.
        # Si el perfil de Chrome ya tiene la sesión activa, cargará logueado
        # y nos saltamos el OAuth por completo.
        if use_real_chrome and config.get("home_url"):
            print(f"\n🌐 Intentando home directamente: {config['home_url']}")
            page.goto(config["home_url"], wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
            already_logged = bool(page.query_selector(config["login_exitoso_selector"]))
            if not already_logged:
                # Verificar por URL — si NO estamos en login, es que hay sesión
                already_logged = "login" not in page.url.lower() and "auth" not in page.url.lower()
            if already_logged:
                print(f"✅ Sesión activa detectada directamente en: {page.url}")
                context.storage_state(path=str(session_file))
                context.close()
                _finalizar_guardado(session_file, portal, config)
                sincronizar(portal)
                return
            print("ℹ️  Sin sesión activa en el home — continuando con login OAuth...\n")

        page.goto(config["login_url"], wait_until="domcontentloaded")

        print(f"\n🌐 Navegando a {config['login_url']}")
        print("⏳ Esperando que completes el login...\n")

        login_detectado = False
        login_url_base = config["login_url"].rstrip("/")
        skip_strategy_1 = config.get("skip_strategy_1", False)

        # Estrategia 1: ya logueado — la página redirigió fuera del login de inmediato
        # (desactivada para portales donde el redirect ocurre sin auth real)
        page.wait_for_load_state("domcontentloaded")
        if not skip_strategy_1 and not page.url.rstrip("/").startswith(login_url_base):
            print(f"ℹ️  Ya había sesión activa (redirigido a {page.url})")
            login_detectado = True
        elif skip_strategy_1 and not page.url.rstrip("/").startswith(login_url_base):
            print(f"ℹ️  Redirigido a {page.url} — verificando si el login es real...")
            # No confiar solo en el redirect; continúa a Strategy 3 para confirmar

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

        _finalizar_guardado(session_file, portal, config)
        sincronizar(portal)


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

    use_real_chrome = "--real-chrome" in args
    sync_presto = "--presto" in args  # uso interno del desarrollador

    setup_portal(portal, browser_name, use_real_chrome, sync_presto)
