## Sesión 15/06/2026 — Plan de trabajo

- [ ] **Tarea 3**: Datos del instalador (teléfono y correo) no aparecen en la web → Fix: además del `.env`, también escribir `documentos/settings.json` al final de `install.sh`
- [ ] **Tarea 2**: Validar formato de teléfono (solo dígitos, mínimo 10) y email (contiene @ y .) en `install.sh`
- [ ] **Tarea 1**: Script bash `setup/whatsapp-qr.sh` para obtener el QR de sincronización de WhatsApp + agregar instrucciones al README.md
- [ ] **Tarea 4**: Subir archivos PDF de CV en "Acerca de mí": backend endpoint `POST /api/cv/es/upload` y `POST /api/cv/en/upload` + input de archivo en frontend

---

## Tareas originales

* ~~Sigo sin poder sincronizar mi teléfono con baileys. En caso de que no se pueda hacer desde el instalador ¿Podrías crear un script bash que obtenga el código QR para sincronizar? Y agregarlo a las instrucciones de instalación que van en el readme.md~~  → pendiente en plan
* ~~Lo otro ¿Los datos de teléfono y correo en el bash, se podrían validar?~~ → pendiente en plan
* ~~Ingresé un correo en el instalador y un teléfono, pero cuando voy a ver la configuración en el sitio web no aparecen.~~ → pendiente en plan
* ~~En "Acerca de mí", Los CV en español e inglés debieran permitir subir archivos.~~ → pendiente en plan
