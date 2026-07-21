# Creación de página en GitHub Pages

Manual para publicar una página de **Buscapega** en GitHub Pages.

## Primero: ¿puede llamarse `buscapega.github.io`?

Es la duda de partida, y la respuesta depende de una regla de GitHub que conviene tener
clara antes de empezar: **el subdominio `X.github.io` lo determina el nombre de la CUENTA,
no el del repositorio.**

Comprobado el 21/07/2026 vía API de GitHub:

| Nombre | Estado | Qué implica |
|---|---|---|
| Usuario/organización `buscapega` | **libre** (HTTP 404) | Se puede crear |
| `RodrigoMoya-dev.github.io` | no existe aún | Disponible para tu cuenta |
| Pages en `RodrigoMoya-dev/buscapega` | no activado | Hay que activarlo |

Entonces tienes **dos caminos**:

### Opción A — `rodrigomoya-dev.github.io/buscapega` (la simple)
No creas nada nuevo: activas Pages en el repo `buscapega` que ya existe. La URL lleva el
proyecto como subcarpeta. Es lo que hace la mayoría de los proyectos.

### Opción B — `buscapega.github.io` (la del nombre limpio)
Requiere **crear una organización** llamada `buscapega` (el nombre está libre) y, dentro de
ella, un repositorio llamado exactamente `buscapega.github.io`. La página queda en la raíz
del subdominio.

> **Ojo con la opción B.** El repositorio de código seguiría siendo
> `RodrigoMoya-dev/buscapega`; la organización sería solo para la página, o habría que
> trasladar el repo a la organización. Son dos cuentas que mantener. Si la página es una
> landing del proyecto, la opción A es más que suficiente y no agrega administración.

**Recomendación: opción A.** Empieza ahí; siempre puedes migrar a B después, porque el
nombre `buscapega` seguirá libre mientras nadie lo tome (no hay forma de reservarlo).

---

## Opción A, paso a paso

### 1. Crear la carpeta de la página

En la raíz del proyecto, en la rama `main`:

```bash
mkdir -p docs
```

GitHub Pages puede servir desde `/docs` en `main`, que es lo más cómodo: no hace falta una
rama aparte ni un flujo de build.

### 2. Escribir la página

Crea `docs/index.html`. Un punto de partida con la identidad del proyecto
(los colores salen de [[recursos/Paleta de colores]]):

```html
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Buscapega — Automatización de búsqueda de empleo</title>
  <style>
    :root { --pine:#297373; --orange:#c84c09; --celadon:#bcd8c1; --blush:#fad8d6; }
    * { box-sizing:border-box; }
    body {
      margin:0; padding:3rem 1.5rem;
      font-family:system-ui,-apple-system,"Segoe UI",sans-serif;
      background:#0b0f10; color:#e8eced; line-height:1.6;
    }
    main { max-width:44rem; margin:0 auto; }
    h1 { color:var(--orange); font-size:clamp(2rem,6vw,3rem); margin:0 0 .5rem; }
    .lead { color:var(--celadon); font-size:1.15rem; margin:0 0 2.5rem; }
    a.cta {
      display:inline-block; background:var(--pine); color:#fff;
      padding:.75rem 1.5rem; border-radius:.5rem; text-decoration:none; font-weight:600;
    }
    a.cta:hover { background:#1f5a5a; }
    footer { margin-top:4rem; color:#7d8a8b; font-size:.875rem; }
  </style>
</head>
<body>
  <main>
    <h1>Buscapega</h1>
    <p class="lead">Automatización de búsqueda de empleo. Hecho desde Chile.</p>
    <p>
      Busca ofertas en varios portales, las evalúa contra tu perfil y postula
      automáticamente en los portales compatibles.
    </p>
    <p><a class="cta" href="https://github.com/RodrigoMoya-dev/buscapega">Ver en GitHub</a></p>
    <footer>Proyecto personal · <span id="anio"></span></footer>
  </main>
  <script>document.getElementById("anio").textContent = new Date().getFullYear();</script>
</body>
</html>
```

> **No pongas nada privado en `docs/`.** `main` es la rama pública: todo lo que entre ahí
> queda visible para cualquiera. Ver [[tecnico/credenciales-git]].

### 3. Evitar que Jekyll procese la carpeta

GitHub Pages pasa el contenido por Jekyll, que **ignora los archivos y carpetas que
empiezan con `_`**. Si algún día agregas `_assets/` o similar, dejarán de servirse sin
ningún mensaje de error. Para desactivarlo:

```bash
touch docs/.nojekyll
```

### 4. Subir los cambios

```bash
git add docs/
git commit -m "feat(pages): landing de Buscapega en /docs"
git push github main
git push origin main       # mantener gitea sincronizado
```

### 5. Activar Pages en GitHub

1. Entra a `https://github.com/RodrigoMoya-dev/buscapega/settings/pages`
2. En **Source**, elige `Deploy from a branch`
3. En **Branch**, elige `main` y la carpeta `/docs`
4. **Save**

La primera publicación tarda entre 1 y 3 minutos. La URL final será:

```
https://rodrigomoya-dev.github.io/buscapega/
```

> El nombre de usuario va **en minúsculas** en la URL, aunque la cuenta se llame
> `RodrigoMoya-dev`.

### 6. Verificar

```bash
curl -sI https://rodrigomoya-dev.github.io/buscapega/ | head -1
```

Debe responder `HTTP/2 200`. Si da 404, revisa que Pages esté activado y que el commit
haya llegado a `main` en **GitHub** (no solo en Gitea).

---

## Opción B, paso a paso (`buscapega.github.io`)

Solo si quieres el subdominio limpio.

1. Crea la organización: https://github.com/organizations/plan → nombre `buscapega`
   (verificado libre al 21/07/2026, pero puede tomarlo alguien en cualquier momento).
2. Dentro de la organización, crea un repositorio **público** llamado exactamente
   `buscapega.github.io`. El nombre debe coincidir con el de la organización; si no,
   Pages no lo sirve en la raíz del subdominio.
3. Sube el `index.html` a la **raíz** del repo (aquí no se usa `/docs`):

```bash
git clone https://github.com/buscapega/buscapega.github.io.git
cd buscapega.github.io
# copiar el index.html
git add index.html .nojekyll
git commit -m "feat: landing inicial"
git push
```

4. En repos con ese nombre exacto, Pages se activa **solo**, sirviendo desde la raíz de la
   rama por defecto. La URL es `https://buscapega.github.io/`.

---

## Dominio propio (opcional)

Si más adelante compras `buscapega.cl` o similar:

1. En Settings → Pages → **Custom domain**, escribe el dominio y guarda.
2. En tu proveedor DNS, crea los registros:
   - `A` hacia `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - o un `CNAME` hacia `rodrigomoya-dev.github.io` si usas un subdominio (`www`).
3. Espera la validación y marca **Enforce HTTPS** (el certificado lo emite GitHub gratis).

GitHub crea un archivo `CNAME` en el repo. **No lo borres**, o la página vuelve a la URL
`.github.io`.

---

## Problemas frecuentes

| Síntoma | Causa habitual | Solución |
|---|---|---|
| 404 tras activar Pages | El build aún no termina | Espera 1-3 min y recarga con caché limpia |
| 404 permanente | Falta `index.html` en la carpeta elegida | Debe llamarse exactamente `index.html` |
| Los estilos no cargan | Rutas absolutas (`/estilo.css`) en opción A | Usa rutas **relativas** (`estilo.css`): la página cuelga de `/buscapega/` |
| Una carpeta no se publica | Empieza con `_` y Jekyll la ignora | Agrega `docs/.nojekyll` |
| Se publica una versión vieja | El push fue solo a Gitea | `git push github main` |

## Cómo actualizar la página

Editas `docs/index.html`, commit y push a `main` en GitHub. Pages reconstruye solo en cada
push; no hay que volver a tocar la configuración.
