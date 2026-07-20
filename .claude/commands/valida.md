# Comando /valida

Evalúa si un portal de búsqueda de empleo puede ser automatizado por Buscapega.

## Uso

```
claude /valida <url_del_sitio>
```

## Descripción

Analiza el sitio indicado y verifica dos criterios:

1. **Permite scraping**: Revisa el archivo `robots.txt` del sitio. Si bloquea `User-Agent: *` o el path `/`, el sitio no permite scraping automatizado.

2. **Tiene autenticación Google**: Examina el HTML de la página principal buscando indicadores de OAuth de Google (`accounts.google.com`, `gsi/client`, botones de "Iniciar sesión con Google", etc.).

## Criterios de automatización

Un portal es automatizable si cumple **ambas** condiciones:
- `allows_scraping: true` — robots.txt es permisivo
- `has_google_auth: true` — el sitio usa Google para autenticarse

## Instrucciones para Claude

Cuando se invoque este comando con una URL:

1. Descarga y analiza el archivo `robots.txt` en `<url>/robots.txt`. Determina si bloquea scraping general.

2. Descarga la página principal (`<url>`) y busca en el HTML los siguientes indicadores de Google Auth:
   - `accounts.google.com`
   - `google-signin`, `g_id_signin`
   - `gsi/client`
   - `oauth2/auth`
   - "login with google", "sign in with google"
   - "iniciar sesión con google", "continuar con google"

3. Reporta el resultado con este formato:
   ```
   Portal: <url>
   ✓/✗ Permite scraping: <Sí / No — motivo>
   ✓/✗ Autenticación Google: <Sí / No detectada>
   Automatizable: <Sí / No>
   ```

4. Si el portal es automatizable, sugiere agregarlo al archivo `obsidian/persona/portales de trabajo.md`.

5. Si el portal ya existe en `portales de trabajo.md`, informa que ya está registrado.

## Ejemplo

```
claude /valida https://www.tecnoempleo.com
```

Resultado esperado:
```
Portal: https://www.tecnoempleo.com
✓ Permite scraping: Sí (robots.txt permisivo)
✓ Autenticación Google: Sí (gsi/client detectado)
Automatizable: Sí

¿Deseas agregarlo a portales de trabajo.md?
```
