# Manual de creación — Sitio web de Buscapega en GitHub Pages

Documento operativo para publicar la página pública del proyecto. Responde primero a la
pregunta de fondo (¿se puede tener `buscapega.github.io`?) y luego entrega el paso a paso.

---

## 1. ¿Se puede hacer `buscapega.github.io`?

**Sí, pero no desde la cuenta `RodrigoMoya-dev`.** GitHub Pages arma el dominio a partir del
*nombre del dueño del repositorio*, no del nombre del proyecto:

| Tipo de sitio | Cómo se llama el repo | URL resultante |
|---|---|---|
| **De usuario/organización** | `<dueño>.github.io` | `https://<dueño>.github.io` |
| **De proyecto** | cualquier nombre | `https://<dueño>.github.io/<repo>` |

Con la cuenta actual, las opciones reales son:

- **Opción A — Sitio de proyecto (sin crear nada nuevo).**
  Se activa Pages sobre el repo `buscapega` y queda en
  `https://rodrigomoya-dev.github.io/buscapega`.
  Cero fricción, pero la URL no es la pedida.

- **Opción B — Organización nueva llamada `buscapega` (da la URL exacta).**
  Se crea una organización gratuita `buscapega`, y dentro un repo llamado
  `buscapega.github.io`. Queda en `https://buscapega.github.io`.
  Requiere que el nombre `buscapega` esté libre en GitHub.

- **Opción C — Dominio propio.**
  Cualquiera de las anteriores + un dominio (`buscapega.cl`, `buscapega.dev`) apuntado por
  DNS. Es la única forma de salir del sufijo `.github.io`.

> **Recomendación:** empezar con la **Opción A** (funciona hoy, sin trámites) y migrar a la
> **B** o **C** cuando se decida el nombre definitivo. Migrar después es barato: Pages
> permite cambiar el origen sin rehacer el sitio.

### Verificar disponibilidad del nombre

Antes de comprometerse con la Opción B, comprobar que `buscapega` no esté tomado:

```bash
curl -o /dev/null -s -w "%{http_code}\n" https://github.com/buscapega
```

- `404` → el nombre está libre.
- `200` → ya existe una cuenta u organización con ese nombre; hay que elegir otro
  (`buscapega-app`, `buscapega-cl`, …) o ir por dominio propio.

> **Comprobado el 20/07/2026:** `github.com/buscapega` y `buscapega.github.io` devuelven
> ambos `404`, es decir **el nombre está disponible**. La Opción B es viable hoy. Conviene
> tomar la organización pronto aunque el sitio se publique después, porque los nombres se
> asignan por orden de llegada.

---

## 2. Opción A — Sitio de proyecto (recomendada para partir)

**Requisito previo:** que el repo ya esté renombrado a `buscapega` en GitHub.

1. Crear la carpeta del sitio en la rama `main` del repo:

   ```
   docs/
   ├── index.html
   ├── logo.png          ← copiar desde grafica/ o docker/frontend/public/
   └── estilos.css
   ```

   Se usa `docs/` (y no una rama `gh-pages`) para que el sitio viva junto al código y no
   haya que mantener una rama aparte sincronizada a mano.

2. En GitHub: **Settings → Pages**.
3. En *Build and deployment*:
   - **Source:** `Deploy from a branch`
   - **Branch:** `main` · carpeta `/docs`
4. **Save**. El primer despliegue tarda 1–2 minutos.
5. Queda publicado en `https://rodrigomoya-dev.github.io/buscapega`.

> Ojo con las rutas: en un sitio de proyecto la raíz del sitio es `/buscapega/`, no `/`.
> Usar siempre **rutas relativas** (`./logo.png`, `./estilos.css`) y nunca absolutas
> (`/logo.png`), que apuntarían fuera del subdirectorio y darían 404.

---

## 3. Opción B — Organización `buscapega` (URL exacta)

1. GitHub → menú de perfil → **Your organizations** → **New organization** → plan **Free**.
2. Nombre de la organización: `buscapega`.
3. Dentro de la organización: **New repository** con el nombre **exacto**
   `buscapega.github.io` (si el nombre no calza con el de la organización, Pages lo trata
   como sitio de proyecto y la URL no funciona).
4. Visibilidad: **Public** (los sitios de Pages en cuentas Free deben ser públicos).
5. Subir el contenido del sitio a la raíz de la rama `main`:

   ```bash
   git clone https://github.com/buscapega/buscapega.github.io.git
   cd buscapega.github.io
   # copiar aquí index.html, logo.png, estilos.css
   git add .
   git commit -m "feat(web): publica sitio inicial de Buscapega"
   git push origin main
   ```

6. **Settings → Pages** → Source: `Deploy from a branch`, Branch: `main` / `(root)`.
7. Queda en `https://buscapega.github.io`.

Aquí sí la raíz del sitio es `/`, así que las rutas absolutas funcionan sin problema.

---

## 4. Opción C — Dominio propio

1. Comprar el dominio (ej. `buscapega.cl` en NIC Chile, o `buscapega.dev`).
2. En el repo del sitio, **Settings → Pages → Custom domain** → escribir el dominio →
   **Save**. Esto crea un archivo `CNAME` en el repo.
3. Configurar el DNS del dominio:

   | Tipo | Nombre | Valor |
   |---|---|---|
   | `A` | `@` | `185.199.108.153` |
   | `A` | `@` | `185.199.109.153` |
   | `A` | `@` | `185.199.110.153` |
   | `A` | `@` | `185.199.111.153` |
   | `CNAME` | `www` | `<dueño>.github.io` |

4. Esperar la propagación DNS (de minutos a 24 h) y marcar **Enforce HTTPS** en
   Settings → Pages cuando GitHub habilite la casilla.

---

## 5. Identidad gráfica del sitio

Los recursos oficiales están en `grafica/` y ya procesados en
`docker/frontend/public/`:

| Recurso | Ruta | Uso |
|---|---|---|
| Logo con transparencia | `docker/frontend/public/logo.png` (512×512) | Cabecera del sitio |
| Favicon | `docker/frontend/public/favicon.ico` | Pestaña del navegador |
| Icono iOS | `docker/frontend/public/apple-touch-icon.png` (180×180) | Acceso directo móvil |
| Logo original | `grafica/logobuscapega.jpg` | Fuente — **no usar directo en web** |

> El JPG original **no tiene transparencia**: su fondo a cuadros son píxeles reales y se
> vería un damero gris sobre cualquier fondo que no sea blanco. Usar siempre el `logo.png`
> ya procesado.

### Paleta

Definida en `grafica/palette.scss` y replicada en `docker/frontend/app/globals.css`
(variables CSS) y `tailwind.config.ts` (utilidades `marca-*`):

| Nombre | HEX | Uso sugerido |
|---|---|---|
| Celadon | `#bcd8c1` | Fondos suaves, texto sobre oscuro |
| Pine Blue | `#297373` | Color primario, cabeceras |
| Spicy Orange | `#c84c09` | Acentos, botones de acción |
| Night Bordeaux | `#420217` | Texto sobre claro, pies de página |
| Soft Blush | `#fad8d6` | Fondos de apoyo, detalles |

### Mensaje de marca

Incluir de forma destacada, igual que en el instalador:

> **Hecho desde Chile: Si es chileno, es bueno**

---

## 6. Verificación posterior

```bash
# ¿Responde el sitio?
curl -I https://rodrigomoya-dev.github.io/buscapega     # Opción A
curl -I https://buscapega.github.io                      # Opción B
```

Debe devolver `HTTP/2 200`. Si devuelve `404`:

- Confirmar que Pages quedó habilitado en Settings → Pages.
- Confirmar la rama y carpeta de origen (`main` + `/docs`, o `main` + `/(root)`).
- Revisar la pestaña **Actions**: el despliegue de Pages aparece ahí y muestra el error si
  falló.
- En Opción B, verificar que el repo se llame **exactamente** `buscapega.github.io`.

---

## Notas

- GitHub Pages sirve **solo contenido estático** (HTML, CSS, JS de navegador). La app de
  Buscapega —FastAPI, PostgreSQL, scrapers, Playwright— **no puede alojarse aquí**: el
  sitio es únicamente la página de presentación y descarga del proyecto.
- El límite blando de Pages es 1 GB por sitio y 100 GB de tráfico al mes; de sobra para una
  landing.
