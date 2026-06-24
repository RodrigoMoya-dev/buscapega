# Vista: Header / Navegación

Barra superior persistente (`docker/frontend/app/layout.tsx` + `components/NavLinks.tsx`).

## Menú de navegación (`NavLinks.tsx`)
Cada enlace lleva un **ícono flat** (SVG inline, sin dependencias) acorde al texto:

| Enlace | Ruta | Ícono |
|---|---|---|
| Ofertas | `/` | bandeja/maletín |
| Portales | `/authenticate` | grilla |
| Configura tu perfil | `/about` | usuario |
| Configuración | `/settings` | engranaje |

- **"Auto respuestas" queda oculta del menú** (iteración futura). La página `/respuestas`
  sigue existiendo, pero sin entrada en el nav.
- **"Validar sitio" se fusionará con "Portales"** (ver `obsidian/web/portales.md`); por eso ya
  no aparece como enlace independiente.

## Reportar problema (issue en GitHub)
A la derecha del nav hay un enlace **"Reportar problema"** (ícono de alerta) que abre
`github.com/RodrigoMoya-dev/wunen/issues/new` con título y cuerpo **prellenados por URL**
(plantilla de descripción / pasos / esperado-vs-obtenido). No usa token: el usuario confirma y
envía el issue desde GitHub. Decisión: enlace directo en vez de integración por API (sin
secretos en el frontend).
