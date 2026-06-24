# Vista: Configura tu perfil

**Ruta web:** `/about`
**Archivo:** `docker/frontend/app/about/page.tsx`
**API:** `GET/POST /api/cv/profile`, `POST /api/cv/{es|en}/upload`, `GET /api/cv/{es|en}/pdf[/exists]`

---

## ¿Qué es?
Vista donde el usuario carga su CV y completa su perfil. Wunen usa estos datos para que el
evaluador de IA puntúe ofertas y genere cartas de presentación.

## Rediseño 24/06/2026 (C1)
Antes había **tres pestañas**: CV (Español), CV (English) y Perfil, con formularios extensos para
capturar el CV de forma estructurada. Ahora:

- **Se eliminaron las pestañas.** La vista es una sola página.
- **Dos input file de CV en PDF** (Español e Inglés), en una grilla de dos columnas. Cada uno
  permite subir/reemplazar el PDF (`POST /api/cv/{lang}/upload`) y descargar el actual. Reusa el
  componente `CvPdfUpload`.
- **A continuación, el formulario de perfil** (`ProfileForm`): stack, modalidad, salario, idiomas,
  tipo de contrato, etc. El botón "Guardar perfil" persiste con `POST /api/cv/profile`.

> Los formularios estructurados de CV (`CvForm`) y sus endpoints `GET/POST /api/cv/{es|en}` siguen
> existiendo en el backend, pero ya no se editan desde esta vista: el CV se aporta como PDF.
