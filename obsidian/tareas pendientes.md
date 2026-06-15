## Plan de trabajo — sesión 15/06/2026

- [x] 1. Commit de cambios pendientes en branch actual (findjobit + scraper)
- [x] 2. Nueva rama: `feature_ui_mejoras_15062026`
- [x] 3. Layout: "Wunen" → enlace a home + texto más grande; saludo "Hola, [nombre]!" en nav
- [x] 4. Settings: agregar campo `user_name`; botón test WhatsApp; info setup WhatsApp y Gmail
- [x] 5. Validate: auto-agregar https:// si falta; fix findjobit.com (resultado incorrecto); cambiar texto "Equivalente..." + botón copiar
- [x] 6. Rename nav: "Acerca de mí" → "Configura tu perfil"; "Respuestas" → "Auto respuestas"
- [x] 7. About: título "Configura tu perfil" + caja explicativa
- [x] 8. Portales: cambiar texto python/claude a "Tip" + botón copiar; validar URL duplicada al validar sitio
- [x] 9. Push a Gitea + deploy en Presto (rsync + docker build)

---

### Ambiente web 


### Generales 


* ¿Es posible, colocar en el menú superior el nombre de quien está usando la plataforma? Que diga "Hola, Rodrigo! ". Ese nombre se podría colocar al inicio, o configurar después dentro de un archivo de configuración donde están todos esos datos (Nombre, Teléfono whatsapp, correo, etc.). También agrega este campo en la pestaña "Configuración". 

* Al hacer clic en "Wunen" se debiera volver al home. ¿Se puede dejar más notorio? Agrandar la letra 

### Dashboard 

* Este debiera ser el home del sitio, donde se muestre información relevante de postulaciones. 
	* Agrega aquí el mensaje de la cantidad de ofertas laborales. 
	* Crea también una "tarjeta" donde se muestren las ofertas totales vs las que se han podido automatizar con el envío a correo. 
	* 

## Ofertas 

 * Al entrar en "Ofertas" me dice que no hay ninguna, lo cual está bien, pero no he ingresado ningún portal, por lo que deberia validar que no hay portales ingresados. 
	


### Validar sitio 

* La aplicación funciona extraña. Aquí el detalle : 
	* Por ejemplo, coloqué "Chiletrabajos.com" que sé que es una web que no existe. . Me apareció el mensaje "No se puede automatizar", me dice que si permite Scrapping pero no tiene autentificación con Google, y mas abajo aparece este mensaje : Error al acceder a la URL: Request URL is missing an 'http://' or 'https://' protocol. Aquí se deben validar ambos temas, y el último mensaje de error que aparece es algo que se podría automatizar, en el momento de escribir el mensaje. Es decir, agregar https si no fue ingresado en la ruta.
	* Puse "https://findjobit.com" y me dice que no permite scrapping y tampoco autentificación con Google, lo cual es un error porque permite ambas cosas. Como dato, en el servidor presto (Puedes entrar con ssh rodrigo@presto) hay una instalación de wunen que está trabajando con findjobit.com. 
* El texto "Equivalente al comando claude", cambialo por "Tip : Si cuentas con claude code, puedes ejecutar este comando desde la terminal, dentro del proyecto : " coloca el comando, y un botón "Copiar" para llevarlo al portapapeles. 


### Portales de empleo 

*  Aparece un listado de "portales con auto-postulacion" sin embargo no hay algun botón o herramienta que permita activarlos, entonces no se entiende mucho la finalidad. 
* El texto para usar los scripts de python o el comando de Claude code, cambia su comentario como una alternativa (Similar a lo descrito en el párrafo anterior), y agrégale un botón "copiar". 
* Si hay portales creados acá, en "Validar sitio", al momento de colocar uno debiera validar que el sitio ingresado no se encuentre acá. 
* 


### Acerca de mí 

* Cambia el menú "Acerca de mí" por "Configura tu perfil", para que se entienda que es al usuario al que se le está usando. Dentro de la página, coloca un pequeño cuadro, que explique porqué es importante llenar estos datos. 


### Respuestas

* Cambia el texto por "Auto respuestas". Anda colocando las cajas de respuestas de cada portal, separado por una caja con el título de la página como nombre del portal. 

### Configuración

* En el botón de notificaciones de whatsapp, crea un botón que permita enviar un mensaje de prueba con la aplicación. 
* Crea procedimientos de configuración, para poder configurara whatsapp con Baileys y el envío de correos mediante google mail. 



# Instalador 

* Falta una opción para que al momento de instalar se pueda realizar la sincronización via whatsapp y el código QR. Además, agrega un script que permita ejecutarlo a futuro si el usuario decide cambiar su número. 

