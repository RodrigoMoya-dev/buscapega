# Comando /autentica

Automatiza el proceso de obtención de cookies de autenticación para los portales de empleo registrados en Wunen.

## Uso

```
claude /autentica
```

## Descripción

Lee los portales registrados en `obsidian/persona/portales de trabajo.md` y ejecuta el proceso de autenticación para cada portal que no tenga una sesión activa.

El proceso de autenticación captura las cookies de la sesión autenticada con Google y las almacena en `setup/cookies/<portal>.json`, que luego son sincronizadas al servidor Presto.

## Instrucciones para Claude

Cuando se invoque este comando:

1. Lee el archivo `obsidian/persona/portales de trabajo.md` y extrae la lista de portales con auto-postulación (columna "Autopostulación" = ✅).

2. Para cada portal, verifica si ya existe un archivo de cookies activo:
   - Ruta: `setup/cookies/<key>_session.json`
   - Las keys son: `findjobit`, `getonbrd`, `tecnoempleo`, `remotelatinos`, `chiletrabajos`, `chumiit`

3. Para los portales sin sesión activa, informa al usuario cuáles necesitan autenticación.

4. Para cada portal que requiera autenticación, ejecuta:
   ```bash
   cd setup && python3 setup_session.py <nombre_portal>
   ```
   Esto abrirá un navegador visible donde el usuario deberá completar el login con Google.

5. Tras capturar cada sesión, el script rsync automáticamente las cookies a `rodrigo@presto:~/docker/wunen/cookies/`.

6. Al finalizar, muestra un resumen del estado de todos los portales.

## Portales con auto-postulación

Los portales que soportan auto-postulación son (extraídos de `portales de trabajo.md`):

| Portal | Archivo de cookies |
|---|---|
| Tecnoempleo | `tecnoempleo_session.json` |
| ChileTrabajos | `chiletrabajos_session.json` |
| Chumi-IT | `chumiit_session.json` |
| RemoteLatinos | `remotelatinos_session.json` |
| GetOnBrd | `getonbrd_session.json` |
| FindJobIT | `findjobit_session.json` |

## Prerequisitos

```bash
cd setup
pip3 install -r requirements.txt
playwright install chromium
```

## Ejemplo de flujo

```
claude /autentica

→ Verificando portales...
  ✓ Tecnoempleo — sesión activa
  ✗ ChileTrabajos — sin sesión
  ✓ Chumi-IT — sesión activa
  ✗ GetOnBrd — sin sesión

→ Se autenticarán 2 portales: ChileTrabajos, GetOnBrd

→ [1/2] Autenticando ChileTrabajos...
  Abriendo navegador. Completa el login con Google.
  ✓ Sesión capturada. Sincronizando a Presto...

→ [2/2] Autenticando GetOnBrd...
  ...
```
