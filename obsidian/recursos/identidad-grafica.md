# Identidad gráfica de Buscapega

Definida el 20/07/2026 junto con el cambio de nombre público (antes *Wunen*).
Reemplaza a la paleta azul anterior de [[Paleta de colores]].

## Archivos fuente

Viven en `grafica/` en la raíz del proyecto:

| Archivo | Qué es |
|---|---|
| `grafica/logobuscapega.jpg` | Logo original, 1024×1024, **sin canal alfa** |
| `grafica/palette.scss` | Export de Coolors con la paleta oficial |

## Logo

El robot: antena, audífonos, cara de pantalla, maletín de viaje e insignia con la bandera
chilena en el pecho.

> **Cuidado con el original.** `logobuscapega.jpg` es JPG y **no tiene transparencia**: el
> fondo a cuadros que se ve en el visor son píxeles grises reales, no un canal alfa. Usado
> directo sobre el nav oscuro se vería un damero. Por eso se generaron derivados con alfa.

### Derivados generados

En `docker/frontend/public/`:

| Archivo | Tamaño | Uso |
|---|---|---|
| `logo.png` | 512×512 | Logo del nav y de la web |
| `apple-touch-icon.png` | 180×180 | Acceso directo en iOS |
| `favicon.ico` | 16/32/48 | Pestaña del navegador |

**Cómo se generaron:** con Pillow, mediante *relleno por inundación (BFS) desde los bordes*
en vez de un umbral global tipo «quitar todo lo claro». El robot es blanco por dentro, así
que un umbral global le habría perforado el cuerpo, la cara y el maletín. El BFS solo
vuelve transparente el fondo **conectado al exterior**, dejando intactos los blancos
interiores.

Tras recortar, el dibujo queda en 483×692 (vertical). Se centra sobre un lienzo cuadrado
transparente antes de escalar — escalar directo a NxN deformaría el robot.

## Paleta

Fuente: `grafica/palette.scss`. Replicada en:

- `docker/frontend/app/globals.css` → variables CSS `--bp-*`
- `docker/frontend/tailwind.config.ts` → utilidades `marca-*` (`bg-marca-pino`, …)
- `install.sh` → secuencias ANSI truecolor

| Nombre | Tailwind | HEX | Uso |
|---|---|---|---|
| Celadon | `marca-celadon` | `#bcd8c1` | Texto sobre oscuro, fondos suaves |
| Pine Blue | `marca-pino` | `#297373` | Color primario |
| Spicy Orange | `marca-naranja` | `#c84c09` | Acentos y llamadas a la acción |
| Night Bordeaux | `marca-bordeaux` | `#420217` | Texto sobre claro, pies |
| Soft Blush | `marca-blush` | `#fad8d6` | Fondos de apoyo |

## Instalador

`install.sh` abre con el robot dibujado en ASCII/Unicode a color, el wordmark
`B U S C A P E G A` y el mensaje de marca:

> **Hecho desde Chile: Si es chileno, es bueno**

> **Detalle técnico:** el dibujo usa una grilla fija (cabeza y cuerpo en las columnas
> 14–24, centro en la 19) y **solo caracteres de ancho 1**. Se evitan `●`, `★`, `▪` y
> similares porque son *East Asian Ambiguous* y muchos terminales los pintan a doble ancho,
> lo que descuadra el dibujo completo. Los colores usan ANSI truecolor (`38;2;R;G;B`); los
> terminales sin soporte 24-bit los ignoran sin romper el diseño.

Ver también: [[Manual de creación]] para la publicación del sitio en GitHub Pages.
