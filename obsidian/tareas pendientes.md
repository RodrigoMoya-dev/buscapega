
# Plan de trabajo — sesión 26-06-2026

Rama fix (`fix_setup_sessions_venv_26062026`):
- [x] F1. `setup-sessions.sh` usa el venv (corrige `ModuleNotFoundError: playwright`) — el wrapper llamaba a `python3` del sistema en vez del venv.
- [x] F2. Validar que Python 3 esté instalado en los scripts; si falta, mensaje claro de instalación.
- [x] F3. Si faltan librerías Python, avisar al usuario e instalarlas automáticamente vía el instalador.

Rama feature (`feature_setup_vistas_26062026`):
- [x] T1. Mover `setup/run_setup.sh` a la raíz como `instalar_dependencias_python.sh` (instalador de dependencias con validación de Python).
- [x] T2. Renombrar `whatsapp-qr.sh` → `vincular-whatsapp.sh` (y referencias).
- [x] T3. WhatsApp: alternativa de conexión por código de vinculación (pairing code) ante "No se pueden vincular dispositivos nuevos"; validación desde el portal documentada (botón "Enviar mensaje de prueba").
- [x] T4. Web/Portales: texto "Sesión activa / no iniciada" → "Incluido / No incluido en búsquedas".
- [x] T5. Web/Portales: el comando copiado para Claude Code incluye el portal (`claude /autentica <portal>`).
- [x] T6. Web/Configuración: botón "Enviar correo de prueba" para validar el "Correo de postulaciones".

Cierre:
- [x] Actualizar documentación en `obsidian/` (web + técnico).
- [ ] Push a gitea (`origin`) y github; merge de ambas ramas a `main` (sin `obsidian/`).
- [ ] Ejecutar `/prueba`.

---

# Comandos 

* Al ejecutar este comando me apareció este mensaje : ./setup-sessions.sh

Traceback (most recent call last):

  File "/Users/rodrigo/Proyectos/Moya.dev/Proyectos internos/wunen/demo/setup/setup_session.py", line 32, in <module>

    from playwright.sync_api import sync_playwright

**ModuleNotFoundError**: No module named 'playwright'
* Sería bueno que en general, si no están las librerías de Python necesarias, indique al usuario que debe cargarlas. 
* Respecto a lo anterior ¿Los scripts detectan si está Python en el sistema? Si no está ¿Puedes agregar una validación? 
* En la carpeta /setup ¿Podrías trasladar el comando run_setup.sh a la raíz del proyecto, y cambiarle el nombre a installar_dependencias_python.sh ? 
* Ejecuté el comando setup_session.py desde la terminal, luego de instalar los requeriminetos, pero sigue apareciendo el mensaje. Te adjunto la data completa. 

 `` python 

./run_setup.sh

🔧 Creando entorno virtual...

📦 Instalando dependencias...

WARNING: Cache entry deserialization failed, entry ignored

WARNING: Cache entry deserialization failed, entry ignored

WARNING: Cache entry deserialization failed, entry ignored

WARNING: Cache entry deserialization failed, entry ignored

  

**[**notice**]** A new release of pip is available: 26.1 -> 26.1.2

**[**notice**]** To update, run: pip install --upgrade pip

🌐 Instalando Chromium para Playwright...

  

Portales disponibles:

  

  findjobit       FindJobIT            ❌ Sin sesión

  getonbrd        GetOnBrd             ❌ Sin sesión

  tecnoempleo     Tecnoempleo          ❌ Sin sesión

  remotelatinos   RemoteLatinos        ❌ Sin sesión

  chiletrabajos   ChileTrabajos        ❌ Sin sesión

  chumiit         Chumi-IT             ❌ Sin sesión

  

❯ ./setup-sessions.sh

Traceback (most recent call last):

  File "/Users/rodrigo/Proyectos/Moya.dev/Proyectos internos/wunen/demo/setup/setup_session.py", line 32, in <module>

    from playwright.sync_api import sync_playwright

ModuleNotFoundError: No module named 'playwright'

zsh: parse error near `\n'

❯ python3 setup/setup_session.py tecnoempleo

/usr/local/Cellar/python@3.14/3.14.4_1/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python: can't open file '/Users/rodrigo/Proyectos/Moya.dev/Proyectos internos/wunen/demo/setup/setup/setup_session.py': [Errno 2] No such file or directory

❯ cd ..

❯ python3 setup/setup_session.py tecnoempleo

Traceback (most recent call last):

  File "/Users/rodrigo/Proyectos/Moya.dev/Proyectos internos/wunen/demo/setup/setup_session.py", line 32, in <module>

    from playwright.sync_api import sync_playwright

**ModuleNotFoundError**: No module named 'playwright'

 ``
* El comando /whatsapp-qr.sh ¿Puedes cambiarle el nombre a vincular-whatsapp.sh? ¿Esta sincronización, se puede validar desde el portal? 
* Quize probar el escaneo de whatsapp, y en teléfono me aparece el mensaje "No se pueden vincular dispositivos nuevos en este momento". Desde el bash ¿Se puede hacer algo para buscar una segunda alternativa de conexión? 
* 


# Web 

## Portales de empleo 

* Cambia el texto "Sesion activa / no iniciada" por "Incluir portal en búsquedas / no incluir en búsquedas". 
* Al momento de copiar la instrucción, en el caso de usar claude code, falta colocar la ruta del sitio web en el registro. 


## Configuración 

* Agrega una opción en "Correo de postulaciones" para poder validar que esté funcionando. 

