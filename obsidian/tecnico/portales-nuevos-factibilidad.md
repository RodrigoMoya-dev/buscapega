# Factibilidad de Automatización — 5 Portales de Empleo

**Fecha de análisis:** 2026-06-04  
**Contexto:** Evaluación para integrar estos portales a la arquitectura de Wunen (scrapers + aplicadores Playwright)

---

## Resumen Ejecutivo

| Portal | Scraping | Auto-postulación | Prioridad | Esfuerzo estimado |
|---|---|---|---|---|
| Remote Latinos | MEDIO | MEDIO | Alta | 6–8 h |
| Virtual Latinos | FÁCIL | DIFÍCIL | Alta | 2–3 h solo scraper |
| Hire Latam | MEDIO | DIFÍCIL | Media | 12–18 h (depende de RecruiterFlow) |
| Deel | DIFÍCIL | MEDIO | Media | 10–14 h |
| Outlier | MUY DIFÍCIL | MUY DIFÍCIL | Baja / Diferir | 14–20 h, alto riesgo |

---

## 1. Remote Latinos — `remotelatinos.com/jobs`

### Estado actual en Wunen
- Aplicador existente: `applicator/remotelatinos.py` ✅  
- Scraper: **no existe** ❌

### Scraping — Dificultad: MEDIO

**Arquitectura del sitio:** Webflow CMS con HTML renderizado en servidor (no SPA). El contenido de los listados de empleos está en el HTML estático, lo que facilita el scraping con `httpx` + BeautifulSoup.

**Autenticación:** Requerida para ver detalles completos (portal en `app.remotelatinos.com`). Los listados básicos pueden estar disponibles sin login.

**robots.txt:** Permisivo — solo bloquea parámetros UTM y fbclid (duplicados), no crawling general.

**Anti-bot:** Sin Cloudflare ni CAPTCHA detectado. Usa CDN de Webflow.

**Estrategia:** Patrón `httpx.Client` similar a `getonbrd.py`, con cookies de sesión para acceder a detalles completos.

### Auto-postulación — Dificultad: MEDIO
El aplicador ya existe. Solo falta el scraper para cerrar el ciclo completo.

### Recomendación
**Implementar de inmediato.** Es la integración más rentable: el aplicador está listo y solo falta el scraper (6–8 h). Primera prioridad.

---

## 2. Deel — `deel.com/careers/open-roles`

### Estado actual en Wunen
- Scraper: **no existe** ❌  
- Aplicador: **no existe** ❌

### Scraping — Dificultad: DIFÍCIL

**Arquitectura del sitio:** Next.js SPA — el listado de empleos se carga completamente del lado del cliente (JavaScript). El HTML inicial está vacío.

**ATS externo:** Deel usa **Ashby** como plataforma de reclutamiento. Las ofertas tienen parámetro `ashby_jid` y podrían estar expuestas vía API interna de Ashby (requiere inspección de red para confirmarlo).

**Paginación:** Botón "Load more" dinámico (XHR/fetch).

**Autenticación:** NO requerida para ver listados (página de carreras pública).

**Anti-bot:** Sin CAPTCHA visible; usa Vercel/Edge Functions (posibles rate limits).

**Estrategia:** Playwright obligatorio. Navegar a la página, esperar hidratación de React (`networkidle`), hacer clic en "Load more" y extraer del DOM renderizado. Alternativa avanzada: interceptar llamadas de red para obtener la API de Ashby directamente.

### Auto-postulación — Dificultad: MEDIO
Sin autenticación para ver empleos, el flow de postulación depende de cada oferta individual (algunas pueden redirigir a Ashby). Es viable con Playwright una vez que se establezca sesión.

### Recomendación
**Implementar en segunda fase.** Alto esfuerzo pero Deel es una empresa grande con muchas ofertas remotas para LATAM. Conviene inspeccionar el tab de Network en browser primero para ver si Ashby expone una API pública.

---

## 3. Outlier — `app.outlier.ai/en/expert/opportunities`

### Estado actual en Wunen
- Scraper: **no existe** ❌  
- Aplicador: **no existe** ❌

### Scraping — Dificultad: MUY DIFÍCIL

**Arquitectura del sitio:** SPA completa — la página de oportunidades muestra "Loading opportunities..." hasta que JavaScript termina. Todo el contenido es client-side.

**Autenticación:** **OBLIGATORIA** para acceder a la lista de oportunidades. No hay vista pública de proyectos disponibles.

**Métodos de login:** Google OAuth o registro por email.

**Gestión de sesión:** OAuth con Google expira cada ~1 hora. Almacenar `storage_state` de Playwright puede funcionar, pero la sesión es frágil.

**robots.txt:** Devuelve 404 (no existe). 

**Anti-bot:** Sin CAPTCHA en el signup; sin Cloudflare detectado. Pero los rate limits en endpoints de auth pueden ser agresivos.

**Estrategia posible:**
1. Login inicial manual (setup de sesión con `setup_session.py`)
2. Guardar `storage_state` en cookies
3. Playwright navega con cookies guardadas
4. Problema: los tokens de Google OAuth expiran rápido → scraper falla frecuentemente

### Auto-postulación — Dificultad: MUY DIFÍCIL
Outlier no es un portal de empleos tradicional — es una plataforma de proyectos freelance donde uno se "registra" en proyectos, no "postula" con CV. El flujo de aplicación no es estándar.

### Recomendación
**Diferir por ahora.** Riesgo muy alto: OAuth complejo + sesiones frágiles + flujo de aplicación no estándar = inversión de 14–20 h con probabilidad alta de puntos muertos. Solo evaluar si hay demanda específica de proyectos Outlier.

---

## 4. Virtual Latinos — `join.virtuallatinos.com`

### Estado actual en Wunen
- Scraper: **no existe** ❌  
- Aplicador: **no existe** ❌

### Scraping — Dificultad: FÁCIL

**Arquitectura del sitio:** HTML estático renderizado en servidor (sitio tradicional). Sin JavaScript pesado.

**Autenticación:** NO requerida para navegar los listados de empleos.

**robots.txt:** Muy permisivo (sin disallows). Expone `sitemap_index.xml`.

**Anti-bot:** Sin Cloudflare ni CAPTCHA detectado.

**Estructura:** Las ofertas están organizadas por categorías (Admin, Sales/Marketing, Finance/HR, Specialized). La URL base y la paginación son simples.

**Estrategia:** `httpx.Client` + BeautifulSoup. Es el caso más simple de los 5. Pattern idéntico a `remoteok.py`.

### Auto-postulación — Dificultad: DIFÍCIL
Requerida autenticación para postular. El flujo de aplicación es probablemente un formulario custom. Necesita Playwright + sesión guardada.

### Recomendación
**Implementar el scraper de inmediato** (2–3 h, quick win). El aplicador puede esperar. Es el caso más sencillo técnicamente y permite empezar a capturar ofertas sin invertir en auth.

---

## 5. Hire Latam — `hirelatam.com`

### Estado actual en Wunen
- Scraper: **no existe** ❌  
- Aplicador: **no existe** ❌

### Scraping — Dificultad: MEDIO (pero con complicación)

**Arquitectura del sitio:** HTML con enhancements de JavaScript. Sin SPA pesada.

**Problema crítico:** Los empleos están hosteados en **RecruiterFlow** (ATS externo), embebido como iframe o con redirección directa a `recruiterflow.com/hirelatam/jobs/`. El sitio de Hire Latam actúa como landing page/marketing, no como repositorio de ofertas.

**robots.txt:** Muy permisivo + sitemap.

**Anti-bot:** Sin Cloudflare ni CAPTCHA detectado en Hire Latam. RecruiterFlow puede tener sus propias protecciones.

**Estrategia posible:**
- Opción A: Scraping directo de RecruiterFlow (implica navegar un ATS de terceros, posibles ToS issues)
- Opción B: Monitorear si Hire Latam alguna vez hostea las ofertas nativamente

### Auto-postulación — Dificultad: DIFÍCIL
Las postulaciones ocurren en RecruiterFlow, no en Hire Latam. Doble dependency.

### Recomendación
**Evaluar antes de implementar.** Verificar manualmente si `recruiterflow.com/hirelatam/jobs` tiene una API pública o permite scraping limpio. Si RecruiterFlow tiene API, el esfuerzo baja a 8–10 h. Si no, diferir.

---

## Plan de Implementación Recomendado

### Fase 1 — Quick Wins (semanas 1–2, ~10 h total)
1. **Virtual Latinos Scraper** (2–3 h) — httpx, HTML estático, sin auth
2. **Remote Latinos Scraper** (6–8 h) — Webflow, con cookies de sesión

### Fase 2 — Inspección y decisión (semana 3)
3. **Hire Latam** — Inspeccionar manualmente RecruiterFlow. Si hay API pública: implementar. Si no: diferir.

### Fase 3 — Esfuerzo alto (mes 2)
4. **Deel Scraper** (10–14 h) — Playwright + debugging de Ashby API

### Diferido indefinidamente
5. **Outlier** — Solo implementar si hay demanda específica y se acepta el riesgo de sesiones OAuth frágiles.

---

## Decisiones de Arquitectura

| Decisión | Opción elegida | Motivo |
|---|---|---|
| Cliente HTTP vs Playwright | httpx para HTML estático, Playwright para SPAs | Misma lógica que scrapers existentes |
| Gestión de sesión | Cookies guardadas via `setup_session.py` | Evita login automation, más estable |
| Cover letters | Claude Haiku via `cover_letter.py` | Ya integrado, bajo costo |
| Registro de aplicadores | `applicator/registry.py` | Patrón existente, solo agregar entradas |

---

## Referencias de Implementación

- Patrón HTTP: `docker/scraper/scrapers/getonbrd.py`
- Patrón Playwright scraper: `docker/scraper/scrapers/findjobit.py`
- Patrón aplicador: `docker/scraper/applicator/remotelatinos.py`
- Clase base aplicador: `docker/scraper/applicator/base.py`
- Setup de sesión: `setup/setup_session.py`
