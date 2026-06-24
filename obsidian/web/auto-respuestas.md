# Vista: Auto respuestas

**Ruta web:** `/respuestas`
**Archivo:** `docker/frontend/app/respuestas/page.tsx`
**API:** `GET/POST/PUT/DELETE /api/answers` (`docker/backend/app/routers/answers.py`)

> **Oculta del menú (24/06/2026):** esta vista quedó **fuera del nav** a la espera de una
> siguiente iteración. La página `/respuestas` sigue funcionando si se accede por URL, pero no
> hay enlace en el header. Ver `obsidian/web/header.md`.

---

## ¿Qué es?

Catálogo de respuestas que **el usuario define manualmente** para que Wunen complete los
formularios de las postulaciones automáticas. **No se obtienen de ningún sitio web.**

## ¿Cómo funcionan? (lógica de matching)

1. Cada respuesta tiene: `descripción`, una lista de `keywords`, el `texto de respuesta` y un
   `portal` opcional (vacío = aplica a todos).
2. Cuando un aplicador de Playwright encuentra un campo/pregunta en el formulario de postulación,
   compara el texto del campo contra las `keywords` de cada respuesta activa.
3. Si una respuesta coincide (y su portal corresponde), Wunen escribe su `texto` en el campo.
4. Si ningún campo coincide, ese campo queda vacío y la postulación puede quedar marcada como
   `PARCIAL` para completarla a mano.

## Keywords especiales (opcionales)

Algunos portales tienen campos fijos que aceptan keywords reservadas. **Solo se usan si se
postula a ese portal**; si no se usa el portal, se ignoran. Ejemplos para ChileTrabajos:

| Keyword | Respuesta esperada |
|---|---|
| `pretensiones_renta` | Monto de renta pretendida, ej: `1500000` |
| `disponibilidad_inmediata` | `true` o `false` |

> Nota: la UI muestra estas keywords como ejemplo. ChileTrabajos sí está registrado en el
> sistema (`documentos/portales.json`), pero requiere capturar sesión para auto-postular.

## Cambios sesión 17/06/2026

- Se agregó un recuadro "¿Cómo funcionan?" explicando que las respuestas las define el usuario
  y el mecanismo de matching por keywords.
- Las "keywords especiales para ChileTrabajos" se reformularon como "Keywords especiales
  (opcionales)" con la aclaración de que solo aplican si se usa ese portal.
